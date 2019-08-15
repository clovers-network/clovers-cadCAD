from itertools import *
import random
from numpy.random import rand
import numpy
from scipy.stats import norm
import networkx as nx
import math
from networkx.readwrite import json_graph
import os.path
import json
import shutil
import threading

# DG = nx.DiGraph()
# DG.add_edge('a', 'b')
# print json_graph.dumps(DG)

def network_filename(params):
    return "network-%s.gpickle" % hash(frozenset(params.items()))

def savefig(fig, previousRuns, num_timesteps, name):
    tempdir = "tmp"
    os.makedirs(tempdir, exist_ok=True)

    # plt must be in scope when function is called
    fig.savefig(tempdir + '/' + 'from-' + str(previousRuns) + '-to-' + str(previousRuns + num_timesteps) + name + '.png')

def getNetwork(params):
    file_name = network_filename(params)
    if  os.path.exists(file_name):
        g = nx.read_gpickle(file_name)
#         with open('./network.json', 'r') as f:
#             g = json.load(f)
#             g = fromDICT(g)
    else:
        g = nx.DiGraph()
    return g

def saveNetwork(g, params):
    file_name = network_filename(params)
    if  os.path.exists(file_name):
        shutil.copy(file_name, file_name + '.bak')
    nx.write_gpickle(g, file_name)
#     _g = toDICT(g)
#     with open('./network.json', 'w+') as f:  # writing JSON object
#         json.dump(_g, f)

def fromDICT(d):
    G = nx.DiGraph()
    G.add_nodes_from(d['nodes'])
    G.add_edges_from(d['edges'])
    return G


def toDICT(G):
    return dict(nodes=[[n, G.nodes[n]] for n in G.nodes()],
         edges=[[u, v, G.get_edge_data(u, v)] for u,v in G.edges()])

# def genuid(g):
#     found = false
#     while(!found):
#         id = math.floor(rand() * 100000000)
#         found = !g.has_node(id)
#     return id
def genuid(g):
    found = False
    while(not found):
        id = math.floor(rand() * 1000000000000000)
        found = not g.has_node(id)
    return id

def getObjectiveValue(s, clover, market_settings, step, params):
    g = s['network']
    syms = s['symmetries']
    fresh = 1
    if (step - clover['step'] >= market_settings['old_clover_interval'] ):
        fresh = market_settings['old_clover_fresh_factor']
    # if within less than previous 5 boost at least by 110%
    if (clover['step'] + market_settings['med_clover_interval'] >= step):
        fresh = market_settings['med_clover_fresh_factor']
    # if super fresh boost by 120%
    if (clover['step'] + market_settings['new_clover_interval'] == step):
        fresh = market_settings['new_clover_fresh_factor']
        
    listValue =  market_settings['base-price'] + getCloverReward(syms, clover, params['payMultiplier'])
    pretty = clover['pretty'] #NOTE: Pretty must be able to come close to price multiplier

    return listValue * pretty * fresh        


def getSubjectiveValue(s, cloverId, clover, userId, market_settings, step, params):
    cloverObjectiveValue = getObjectiveValue(s, clover, market_settings, step, params)
    foo = [1, 2, 3]
#     TODO: add back when time isn't an issue
#     numpy.random.seed([int(userId/1000000),int(cloverId/1000000)])
    stdDev = market_settings['stdDev']
    return norm.rvs(loc=cloverObjectiveValue,scale=stdDev)


def processSymmetries(s, clover):
    for sy in ['rotSym', 'x0Sym', 'y0Sym', 'xySym', 'xnySym', 'hasSymmetry']:
        s['symmetries'][sy] += (1 if clover[sy] else 0)
    return s

def unprocessSymmetries(s, clover):
    for sy in ['rotSym', 'x0Sym', 'y0Sym', 'xySym', 'xnySym', 'hasSymmetry']:
        s['symmetries'][sy] -= (1 if clover[sy] else 0)
    return s

def processMarketIntentions(s, market_intention, market_settings, step, params):
    g = s['network']
    
    playerId = market_intention['playerId']
    cloverId = market_intention['cloverId']
    intent = market_intention['intent']
    clover = g.nodes[cloverId]

    if intent == 'toBuy':
        price = clover['price']

        if (price == 0):
            raise NameError('cant buy a clover thats not for sale', intent, clover)

        player = g.nodes[playerId]
        # if player doesn't have enough coins, buy some
        if (price > player['supply']):
            costToBuy = calculatePriceForTokens(s, market_settings, price)
            player['supply'] = price + player['supply']
            s['bc-totalSupply'] += price
            s['bc-balance'] += costToBuy
            player['eth-spent'] += costToBuy
        
        # remove coins from buyer
        player['supply'] -= price
        # if owner is bank, burn the coins
        if (owner_type(g, cloverId) == 'bank'):
            s['timestepStats']['cloversBoughtFromBank'] += 1
            s['bc-totalSupply'] -= price
            s['numBankClovers'] -= 1
            s['numPlayerClovers'] += 1
        # else give the coins to the previous owner
        else:
            s['timestepStats']['cloversTraded'] += 1
            currentOwnerId = get_owner(g, cloverId)
            currentOwner = g.nodes[currentOwnerId]
            currentOwner['supply'] += price
        # set the new owner and set the new price to 0
        g = set_owner(g, playerId, cloverId)
        g = set_price(g, cloverId, 0)
    else:
        s['timestepStats']['cloversListedByPlayers'] += 1
        price = getSubjectiveValue(s, cloverId, clover, playerId, market_settings, step, params)
        g = set_price(g, cloverId, price)
    return s


def processBuysAndSells(s, clover_intention, market_settings, bankId, step, params):
    g = s['network']
    userId = clover_intention['user']
    user = g.nodes[userId]
    clover = clover_intention['clover']

    s = processSymmetries(s, clover)
    
    cloverId = add_clover_to_network(s, clover)

    subjectivePrice = getSubjectiveValue(s, cloverId, clover, userId, market_settings, step, params)
    price = getCloverPrice(s, clover, market_settings, params)
    
    if (user['type'] == 'miner'):
        clover_intention['intention'] = 'sell'
    else:
        clover_intention['intention'] = "sell" if price > subjectivePrice else 'keep'
    
    reward = getCloverReward(s['symmetries'], clover, params['payMultiplier'])
    rewardInEth = calculateCashout(s, market_settings, reward)
    g.nodes[cloverId]['reward'] = reward
    
    if (clover_intention['intention'] == 'keep'):
        g = set_owner(g, userId, cloverId)
        s['numPlayerClovers'] += 1
        s['timestepStats']['cloversKept'] += 1
        if (price > user['supply']):
            costToBuy = calculatePriceForTokens(s, market_settings, price)
            user['supply'] = price + user['supply']
            s['bc-totalSupply'] += price
            s['bc-balance'] += costToBuy
            user['eth-spent'] += costToBuy
            user['eth-spent'] += market_settings['buy_coins_cost_in_eth']
        user['eth-spent'] += market_settings['register_clover_cost_in_eth']
        user['supply'] -= price
        s['bc-totalSupply'] -= price
    else:
        if (rewardInEth > market_settings['register_clover_cost_in_eth']):
            g = set_owner(g, bankId, cloverId)
            s['numBankClovers'] += 1
            s['timestepStats']['cloversReleased'] += 1
            listingPrice = getCloverListingPrice(s, clover, market_settings, params)
            g = set_price(g, cloverId, listingPrice)
            user['supply'] += reward
            s['bc-totalSupply'] += reward
            user['eth-spent'] += market_settings['register_clover_cost_in_eth']
        else:
            s = unprocessSymmetries(s, clover)
            delete_clover(s, cloverId)
    return s

def initialize(market_settings, conditions):
    def init_ts(s):
        return calculatePurchaseReturn(s, market_settings, market_settings["initialSpend"])

    conditions['bc-balance'] = market_settings["initialSpend"]
    conditions['bc-totalSupply'] = init_ts(conditions)
    (conditions['network'], conditions['players'], conditions['miners'], conditions['bank']) = initialize_network(market_settings)
    conditions['clovers'] = []
    state = {"s" : conditions}
    return state


def seed_network(n, m, g, market_settings):
    players = []
    for i in range(n):
        nodeId = genuid(g)
        g.add_node(nodeId)
        g.nodes[nodeId]['type'] = "player"
        
        # randomize player's hashrate on
        # a normal distribution centered on 15, stddev=2
        g.nodes[nodeId]['hashrate'] = market_settings['miner_hashrate']()
        g.nodes[nodeId]['player_active_percent'] = market_settings['pct_player_is_active']
        g.nodes[nodeId]['supply'] = 0
        g.nodes[nodeId]['eth-spent'] = 0
        g.nodes[nodeId]['eth-earned'] = 0
        g.nodes[nodeId]['desired_for_sale_ratio'] = market_settings['desired_for_sale_ratio']()
        g.nodes[nodeId]['market_buying_propensity'] = market_settings['market_buying_propensity']()
        g.nodes[nodeId]['is_active'] = False
        players.append(nodeId)
    miners = []    
    for j in range(m):
        nodeId = genuid(g)
        g.add_node(nodeId)
        g.nodes[nodeId]['type'] = "miner"
        g.nodes[nodeId]['cash_out_threshold'] = market_settings['miner_cash_out_threshold']
        g.nodes[nodeId]['hashrate'] = market_settings['miner_hashrate']()
        g.nodes[nodeId]['supply'] = 0
        g.nodes[nodeId]['eth-spent'] = 0
        g.nodes[nodeId]['eth-earned'] = 0
        g.nodes[nodeId]['is_active'] = market_settings['pct_miner_is_active']
        miners.append(nodeId)
    return (g, players, miners)

def initialize_network(market_settings):
    g = nx.DiGraph()
    
    (g, players, miners) = seed_network(market_settings['initial_players'], market_settings['initial_miners'], g, market_settings)
    
    bank = genuid(g)
    g.add_node(bank)
    g.nodes[bank]['type'] = "bank"


    return (g, players, miners, bank)

#helper functions
def get_nodes_by_type(s, node_type_selection):
    if (node_type_selection == 'player'):
        return s['players']
    elif (node_type_selection == 'miner'):
        return s['miners']
    elif (node_type_selection == 'bank'):
        return s['bank']
    elif (node_type_selection == 'clover'):
        return s['clovers']
    else:
        raise NameError('unknown node_type_selection', node_type_selection)
#     return [node for node in g.nodes if g.nodes[node]['type']== node_type_selection ]

def get_edges_by_type(g, edge_type_selection):
    return [edge for edge in g.edges if g.edges[edge]['type']== edge_type_selection ]

def delete_clover(s, cloverId):
    s['clovers'].remove(cloverId)
    s['network'].remove_node(cloverId)


def add_clover_to_network(s, clover, price = 0):
    g = s['network']
    nodeId = genuid(g)
    g.add_node(nodeId)
    s['clovers'].append(nodeId)
    g.nodes[nodeId]['type'] = 'clover'
    g.nodes[nodeId]['reward'] = '0'
    g.nodes[nodeId]['price'] = price
    for attr in clover.keys():
        g.nodes[nodeId][attr] = clover[attr]
    return nodeId

def get_clovers_for_sale(s):
    g = s['network']
    clovers = get_nodes_by_type(s, "clover")
    return [clover for clover in clovers if g.nodes[clover]['price'] > 0]
    
def get_owned_clovers(g, ownerId):
    return list(g.successors(ownerId))
    
def owner_type(g, cloverId):
    return g.nodes[cloverId]['owner_type']

def get_owner(g, cloverId):
    # this could be made safer, to check for multiple
    # owners and return error if multiple owners exist
    # also, we should throw exception if no owner found
    for owner in g.predecessors(cloverId):
        return owner  

def set_owner(g, ownerId, cloverId):
    old_owner = get_owner(g, cloverId)
    if (old_owner != None):
        g.remove_edge(old_owner, cloverId)
    g.add_edge(ownerId, cloverId, type="ownership")
    g.nodes[cloverId]['owner_type'] = g.nodes[ownerId]['type']
    return g
    
def set_price(g, cloverId, price):
    g.nodes[cloverId]['price'] = price
    return g
    
def getSlope(totalSupply, collateral, CW):
    return collateral / (CW * totalSupply ** (1 / CW))

def calculatePriceForTokens(s, market_settings, amount):
    totalSupply = s['bc-totalSupply'] + market_settings['bc-virtualSupply']
    collateral = s['bc-balance'] + market_settings['bc-virtualBalance']
    CW = market_settings['bc-reserveRatio']
    return _calculatePriceForTokens(totalSupply, collateral, CW, amount)

def _calculatePriceForTokens(totalSupply, collateral, CW, amount):
    return collateral * ((amount / totalSupply + 1)**(1/CW)-1)

def getPower(CW):
    return 1 / CW -1
    
def calculatePurchaseReturn(s, market_settings, amount):
    totalSupply = s['bc-totalSupply'] + market_settings["bc-virtualSupply"]
    collateral = s['bc-balance'] + market_settings["bc-virtualBalance"]
    CW = market_settings["bc-reserveRatio"]
    if (s['bc-balance'] <= 0):
        return 0
    return totalSupply * ((1 + amount / collateral)**CW-1)

def calculateCashout(s, market_settings, amount):
    if (s['bc-balance'] <= 0):
        return 0
    totalSupply = s['bc-totalSupply'] + market_settings['bc-virtualSupply']
    collateral = s['bc-balance'] + market_settings['bc-virtualBalance']
    CW = market_settings['bc-reserveRatio']
    result = calculateSellReturn(totalSupply, collateral, CW, amount)
    if (result > s['bc-balance']):
        result = s['bc-balance']
    return result

def calculateSellReturn(totalSupply, collateral, CW, amount):
    if (collateral <= 0):
        return 0
    return collateral * (1 - (1 - amount / totalSupply)**(1/CW))

def calculateCurrentPrice(s, market_settings):
    totalSupply = s['bc-totalSupply'] + market_settings['bc-virtualSupply']
    collateral = s['bc-balance'] + market_settings['bc-virtualBalance']
    CW = market_settings['bc-reserveRatio']
    if (s['bc-balance'] <= 0):
        return 0
    return collateral / (totalSupply * CW)

def getCloverReward(syms, clover, payMultiplier):
    if not clover['hasSymmetry']:
        return 0
    totalRewards = 0
    allSymms = syms['rotSym'] + syms['y0Sym'] + syms['x0Sym'] + syms['xySym'] + syms['xnySym']
    if clover['rotSym']:
        totalRewards += payMultiplier * (1 + allSymms) / (syms['rotSym'] + 1)
    if clover['y0Sym']:
        totalRewards += payMultiplier * (1 + allSymms) / (syms['y0Sym'] + 1)
    if clover['x0Sym']:
        totalRewards += payMultiplier * (1 + allSymms) / (syms['x0Sym'] + 1)
    if clover['xySym']:
        totalRewards += payMultiplier * (1 + allSymms) / (syms['xySym'] + 1)
    if clover['xnySym']:
        totalRewards += payMultiplier * (1 + allSymms) / (syms['xnySym'] + 1)
    return totalRewards

def getCloverListingPrice(s, clover, market_settings, params):
    rewardAmount = getCloverReward(s['symmetries'], clover, params['payMultiplier'])
    payAmount = market_settings['base-price'] + (rewardAmount * market_settings['priceMultiplier'])
    return payAmount

def getCloverPrice(s, clover, market_settings, params):
    rewardAmount = getCloverReward(s['symmetries'], clover, params['payMultiplier'])
    payAmount = market_settings['base-price'] + rewardAmount
    return payAmount

def getSymmetry(symmetryRarities):
    rand_val = rand()
    
    for i in range(1,len(symmetryRarities)+1):
        if rand_val <= numpy.sum(list(symmetryRarities.values())[0:i]):
            break;
    
    return list(symmetryRarities.keys())[i-1]


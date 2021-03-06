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

def network_filename(params):
    return "tmp/network-%s.gpickle" % hash(frozenset(params.items()))

def savefig(fig, previousRuns, num_timesteps, name):
    tempdir = "tmp"
    os.makedirs(tempdir, exist_ok=True)

    # plt must be in scope when function is called
    fig.savefig(tempdir + '/' + 'from-' + str(previousRuns) + '-to-' + str(previousRuns + num_timesteps) + name + '.png')

def getNetwork(params):
    # print("getNetwork")
    file_name = network_filename(params)
    if  os.path.exists(file_name):
        g = nx.read_gpickle(file_name)
    else:
        g = nx.DiGraph()
    # print("gend-etNetwork")
    return g

def saveNetwork(g, params):
    # print("saveNetwork")
    file_name = network_filename(params)
    # print("aftersavenetwork--------1")
    if  os.path.exists(file_name):
        shutil.copy(file_name, file_name + '.bak')
    # print("aftersavenetwork--------2")
    nx.write_gpickle(g, file_name)
    # print("aftersavenetwork--------3")
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
    # g = s['network'] # unused var
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

    listValue =  params['basePrice'] + getCloverReward(syms, clover, params['payMultiplier'])
    # ^ should this also be multiplied by priceMultiplier???? (see line 390)
    pretty = clover['pretty'] #NOTE: Pretty must be able to come close to price multiplier

    return listValue * pretty * fresh        


def getSubjectiveValue(s, cloverId, clover, userId, market_settings, step, params):
    cloverObjectiveValue = getObjectiveValue(s, clover, market_settings, step, params)
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
    # print('begin-processMarketIntentions')
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
            costToBuy = calculatePriceForTokens(s, params, price)
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
    # print('end-processMarketIntentions')
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
    gas_fee = market_settings['register_clover_cost_in_eth'] * s['gasPrice']
    price = price + gas_fee

    if (user['type'] == 'miner'):
        clover_intention['intention'] = 'sell'
    else:
        clover_intention['intention'] = "sell" if price > subjectivePrice else 'keep'
    
    reward = getCloverReward(s['symmetries'], clover, params['payMultiplier'])
    rewardInEth = calculateCashout(s, params, reward)
    g.nodes[cloverId]['reward'] = reward
    
    if (clover_intention['intention'] == 'keep'):
        g = set_owner(g, userId, cloverId)
        s['numPlayerClovers'] += 1
        s['timestepStats']['cloversKept'] += 1
        if (price > user['supply']):
            costToBuy = calculatePriceForTokens(s, params, price)
            user['supply'] = price + user['supply']
            s['bc-totalSupply'] += price
            s['bc-balance'] += costToBuy
            user['eth-spent'] += costToBuy
            user['eth-spent'] += market_settings['buy_coins_cost_in_eth'] * s['gasPrice']
        user['eth-spent'] += market_settings['register_clover_cost_in_eth'] * s['gasPrice']
        user['supply'] -= price
        s['bc-totalSupply'] -= price
    else:
        if (rewardInEth > (market_settings['register_clover_cost_in_eth'] * s['gasPrice'])):
            g = set_owner(g, bankId, cloverId)
            s['numBankClovers'] += 1
            s['timestepStats']['cloversReleased'] += 1
            listingPrice = getCloverListingPrice(s, clover, market_settings, params)
            g = set_price(g, cloverId, listingPrice)
            user['supply'] += reward
            s['bc-totalSupply'] += reward
            user['eth-spent'] += market_settings['register_clover_cost_in_eth'] * s['gasPrice']
        else:
            s = unprocessSymmetries(s, clover)
            delete_clover(s, cloverId)
    return s

def initialize(params, market_settings, conditions):
    # print("initialize")
    def init_ts(s):
        return calculatePurchaseReturn(s, params, market_settings["initialSpend"])
    if conditions['bc-balance'] == 0:
        conditions['bc-balance'] = market_settings["initialSpend"]
        conditions['bc-totalSupply'] = init_ts(conditions)
    (conditions['network'], conditions['players'], conditions['miners'], conditions['bank']) = initialize_network(market_settings)
    
    conditions = initialize_clovers(conditions, market_settings, params)

    initialize_balances(conditions)

    state = {"s" : conditions}
    return state

def initialize_balances(s):
    # print("initialize_balances")
    tokens_to_distribute = s['bc-totalSupply'] - s['foundation-tokens']
    average = tokens_to_distribute / (len(s['players']) + len(s['miners']))
    for p in s['players']:
        s['network'].nodes[p]['balance'] = average
    for m in s['miners']:
        s['network'].nodes[m]['balance'] = average


def initialize_clovers(s, market_settings, params):
    # print("initialize_clovers")
    s['clovers'] = []
    def hasSymmetry(cloverCount):
        return 1
    # don't think i can import the rarity from the config can i?
    rarity = {
        'hasSymmetry': hasSymmetry, # at initialization 100% of clovers have symmetry (until we figure out asymms in the model)
        'claimRate':   0.01,
        'pretty':      0.01, # 1/100 clovers are "pretty"
        'rarePretty':  0.3, # 30/100 rare clovers are "pretty"k
        'symmetries': {
            'rotSym':      72/2705,
            'x0Sym':       223/2705,
            'y0Sym':       221/2705,
            'xySym':       1009/2705,
            'xnySym':      1154/2705,
            'diagRotSym':  21/2705,
            'perpRotSym':  5/2705,
            'allSym':      4/2705
        }
    }

    rarity['hasSymmetry'] = hasSymmetry

    bankClovers = mine_clovers(s['numBankClovers'], 0, False, rarity, market_settings)
    for clover in bankClovers:
        cloverId = add_clover_to_network(s, clover, 10)
        set_owner(s['network'], s['bank'], cloverId)
    playerClovers = mine_clovers(s['numPlayerClovers'], 0, False, rarity, market_settings)
    for clover in playerClovers:
        price = 0
        if (rand() < s['initial-playerCloversForSale'] / s['numPlayerClovers']):
            price = getCloverPrice(s, clover, market_settings, params)

        cloverId = add_clover_to_network(s, clover, price)
        userId = random.choice(s['players'])
        set_owner(s['network'], userId, cloverId)
    return s

def seed_network(n, m, g, market_settings):
    # print("seed_network")
    players = []
    for i in range(n):
        nodeId = genuid(g)
        g.add_node(nodeId)
        g.nodes[nodeId]['type'] = "player"
        
        # randomize player's hashrate on
        # a normal distribution centesupplyred on 15, stddev=2
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
    # print("initialize_network")
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

def calculateSlope(s, params):
    def getSlope(totalSupply, collateral, CW):
        return collateral / (CW * totalSupply ** (1 / CW))

    totalSupply = s['bc-totalSupply'] + params['bc-virtualSupply']
    collateral = s['bc-balance'] + params['bc-virtualBalance']
    CW = params['bc-reserveRatio']

    return getSlope(totalSupply, collateral, CW)


def calculatePriceForTokens(s, params, amount):
    def _calculatePriceForTokens(totalSupply, collateral, CW, amount):
        return collateral * ((amount / totalSupply + 1)**(1/CW)-1)

    totalSupply = s['bc-totalSupply'] + params['bc-virtualSupply']
    collateral = s['bc-balance'] + params['bc-virtualBalance']
    CW = params['bc-reserveRatio']

    return _calculatePriceForTokens(totalSupply, collateral, CW, amount)


def getPower(CW):
    return 1 / CW -1

def calculatePurchaseReturn(s, params, amount):
    # print(params)
    totalSupply = s['bc-totalSupply'] + params['bc-virtualSupply']
    collateral = s['bc-balance'] + params['bc-virtualBalance']
    CW = params["bc-reserveRatio"]
    if (s['bc-balance'] <= 0):
        return 0
    return totalSupply * ((1 + amount / collateral)**CW-1)

def calculateCashout(s, params, amount):
    if (s['bc-balance'] <= 0):
        return 0
    totalSupply = s['bc-totalSupply'] + params['bc-virtualSupply']
    collateral = s['bc-balance'] + params['bc-virtualBalance']
    CW = params['bc-reserveRatio']
    result = calculateSellReturn(totalSupply, collateral, CW, amount)
    if (result > s['bc-balance']):
        result = s['bc-balance']
    return result

def calculateSellReturn(totalSupply, collateral, CW, amount):
    if (collateral <= 0):
        return 0
    return collateral * (1 - (1 - amount / totalSupply)**(1/CW))

def calculateCurrentPrice(s, params):
    totalSupply = s['bc-totalSupply'] + params['bc-virtualSupply']
    collateral = s['bc-balance'] + params['bc-virtualBalance']
    CW = params['bc-reserveRatio']
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
    payAmount = params['basePrice'] + (rewardAmount * params['priceMultiplier'])
    return payAmount

def getCloverPrice(s, clover, market_settings, params):
    rewardAmount = getCloverReward(s['symmetries'], clover, params['payMultiplier'])
    payAmount = params['basePrice'] + rewardAmount
    # ^ should this be multiplied by price multiplier??
    return payAmount

def getSymmetry(symmetryRarities):
    rand_val = rand()
    # print('len(symmetryRarities)+1')
    # print(len(symmetryRarities)+1)
    for i in range(1,len(symmetryRarities)+1):
        # print(symmetryRarities.values())
        if rand_val <= numpy.sum(list(symmetryRarities.values())[0:i]):
            break
    
    return list(symmetryRarities.keys())[i-1]




# mines n clovers, and returns only the rare ones, with rarity
def mine_clovers(num_hashes, step, cloverCount, rarity, market_settings):
    possibleSyms = ['rotSym', 'y0Sym', 'x0Sym', 'xySym', 'xnySym']
    # first determine how many rare clovers are found with the given hashrate
    rare_clovers = num_hashes*rarity['hasSymmetry'](cloverCount)
    rare_clovers = (1 if rand() < (rare_clovers - math.floor(rare_clovers)) else 0) + math.floor(rare_clovers)
    
    clovers = []
    
    # for each rare clover, determine its symmetries and prettiness from utility function
    # and return them as an array 
    for i in range(rare_clovers):
        
        clover = {}
        clover['step'] = step

        symmetry = getSymmetry(rarity['symmetries'])
        for sym in possibleSyms:
            clover[sym] = False
    
        if symmetry in possibleSyms:
            clover[symmetry] = True
        else:
            if sym == 'diagRotSym':
                clover['xySym'] = clover['xnySym'] = clover['rotSym'] = True
            if sym == 'perpRotSym':
                clover['x0Sym'] = clover['y0Sym'] = clover['rotSym'] = True
            if sym == 'allSym':
                for sym in possibleSyms:
                    clover[sym] = True
        
        clover['pretty'] = rand() + market_settings['pretty_multiplier'] if (rand() < rarity['rarePretty']) else 0
        clover['hasSymmetry'] = True
        clovers.append(clover)
    
    return clovers

from itertools import *
from numpy.random import rand
import numpy
from scipy.stats import norm
import networkx as nx

def processSymmetries(s, clover):
    for sy in ['rotSym', 'x0Sym', 'y0Sym', 'xySym', 'xnySym', 'hasSymmetry']:
        s['symmetries'][sy] += (1 if clover[sy] else 0)
    return s

# processBuysAndSells will take a current clover_intention and execute the result of keeping or selling it. This includes updates to the state (s) with regard to bc-totalSupply, bc-balance, user[supply] & user[eth-spent]
def processBuysAndSells(s, clover_intentions, market_settings):
    g = s['network']
    nodeId = clover_intention['user']
    user = g.nodes[nodeId]
    clover = clover_intentions['clover']
    bank = utils.get_nodes_by_type(g, "bank")[0]

    s = processSymmetries(s, clover)
    
    (g, nodeId) = add_clover_to_network(g, clover)

    if (clover_intentions['intention'] == 'keep'):
        set_owner(g, player, nodeId)
        price = getCloverPrice(s, clover, market_settings)
        if (price > user['supply']):
            costToBuy = calculatePriceForTokens(s, market_settings, price)
            user['supply'] = price + user['supply']
            s['bc-totalSupply'] += price
            s['bc-balance'] += costToBuy
            user['eth-spent'] += costToBuy
        user['supply'] -= price
        s['bc-totalSupply'] -= price
    else:
        set_owner(g, bank, nodeId) 
        reward = getCloverReward(s, clover, market_settings)
        user['supply'] += reward
        s['bc-totalSupply'] += reward
    return s

def initialize(market_settings, conditions):
    
    def init_ts(s):
        return calculatePurchaseReturn(market_settings["bc-virtualSupply"], market_settings["bc-virtualBalance"], market_settings["bc-reserveRatio"], market_settings["initialSpend"])
    
    conditions['bc-balance'] = market_settings["initialSpend"]
    conditions['bc-totalSupply'] = init_ts(conditions)
    conditions['network'] = initialize_network(20, 3)
    
    return conditions


def initialize_network(n, m):
    network = nx.DiGraph()
    for i in range(n):
        network.add_node(i)
        network.nodes[i]['type'] = "player"
        
        # randomize player's hashrate on
        # a normal distribution centered on 15, stddev=2
        network.nodes[i]['hashrate'] = norm.rvs(loc=15, scale=2)
        network.nodes[i]['player_active_percent'] = 0.7
        network.nodes[i]['supply'] = 0
        network.nodes[i]['eth-spent'] = 0
        network.nodes[i]['market_listing_propensity'] = 0.3 # percentage of owned clovers to list
        network.nodes[i]['market_buying_propensity'] = 0.8 # probability to buy pretty clovers from market
        
    for j in range(n,n+m):
        network.add_node(j)
        network.nodes[j]['type'] = "miner"
        network.nodes[j]['hashrate'] = norm.rvs(loc=15, scale=2)
        network.nodes[j]['is_active'] = 0.7
    
    network.add_node(n + m)
    network.nodes[n+m]['type'] = "bank"
        
    return network

#helper functions
def get_nodes_by_type(g, node_type_selection):
    
    return [node for node in g.nodes if g.nodes[node]['type']== node_type_selection ]

def get_edges_by_type(g, edge_type_selection):
    return [edge for edge in g.edges if g.edges[edge]['type']== edge_type_selection ]

def add_clover_to_network(g, clover, for_sale = False):
    nodeId = len(g.nodes)
    g.add_node(nodeId)
    g.nodes[nodeId]['type'] = 'clover'
    g.nodes[nodeId]['for_sale'] = for_sale
    for attr in clover.keys():
        g.nodes[nodeId][attr] = clover[attr]
    return (g, nodeId)

def get_clovers_for_sale(g):
    clovers = get_nodes_by_type(g, "clover")
    return [clover for clover in clovers if g.nodes[clover]['for_sale'] == True]
    
def get_owned_clovers(g, ownerId):
    return [clover for clovers in g.succssors(ownerId)]
    
def owner_type(g, cloverId):
    return g.nodes[cloverId]['owner_type']

def get_owner(g, cloverId):
    # this could be made safer, to check for multiple
    # owners and return error if multiple owners exist
    # also, we should throw exception if no owner found
    for owner in g.predecessors(cloverId):
        return owner  

def set_owner(g, ownerId, cloverId):
    g.add_edge(ownerId, cloverId)
    g.edges[(ownerId, cloverId)]['type'] = "ownership"
    g.nodes[cloverId]['owner_type'] = g.nodes[ownerId]['type']
    
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
    
def calculatePurchaseReturn(totalSupply, collateral, CW, amount):
    return totalSupply * ((1 + amount / collateral)**CW-1)

def calculateSellReturn(totalSupply, collateral, CW, amount):
    return collateral * (1 - (1 - amount / totalSupply)**(1/CW))

def calculateCurrentPrice(totalSupply, collateral, CW):
    return collateral / (totalSupply * CW)

# SHOULD UPDATE s TO BE TAKING NETWORK AS AN INPUT, FILTERING BY CLOVER NODES
def getCloverReward(s, clover, market_settings):
    if not clover['hasSymmetry']:
        return 0
    totalRewards = 0
    syms = s['symmetries']
    allSymms = numpy.sum([syms['rotSym'], syms['y0Sym'], syms['x0Sym'], syms['xySym'], syms['xnySym']])
    if clover['rotSym']:
        totalRewards += market_settings['payMultiplier'] * (1 + allSymms) / 2
    if clover['y0Sym']:
        totalRewards += market_settings['payMultiplier'] * (1 + allSymms) / 2
    if clover['x0Sym']:
        totalRewards += market_settings['payMultiplier'] * (1 + allSymms) / 2
    if clover['xySym']:
        totalRewards += market_settings['payMultiplier'] * (1 + allSymms) / 2
    if clover['xnySym']:
        totalRewards += market_settings['payMultiplier'] * (1 + allSymms) / 2
    return totalRewards

def getCloverPrice(s, clover, market_settings):
    rewardAmount = getCloverReward(s, clover, market_settings)
    payAmount = (rewardAmount + market_settings['base-price']) * market_settings['priceMultiplier']
    return payAmount

def getSymmetry(symmetryRarities):
    rand_val = rand()
    
    for i in range(1,len(symmetryRarities)+1):
        if rand_val <= numpy.sum(list(symmetryRarities.values())[0:i]):
            break;
    
    return list(symmetryRarities.keys())[i-1]


from itertools import *
from numpy.random import rand
import numpy
from scipy.stats import norm
import networkx as nx

def getObjectiveValue(s, clover, market_settings, step):
    g = s['network']
    syms = s['symmetries']

    fresh = 1
    # if older than 50 steps, decrease fresh by 50%
    if (step - clover['step'] >= 50 ): #PARAMATER
        fresh = 0.5 #PARAMATER
    # if within less than previous 5 boost at least by 110%
    if (clover['step'] + 5 >= step): #PARAMATER
        fresh = 1.1  #PARAMATER
    # if super fresh boost by 120%
    if (clover['step'] + 1 == step): #PARAMATER
        fresh = 1.2 #PARAMATER
        
    listValue =  market_settings['base-price'] + getCloverReward(syms, clover, market_settings)
    pretty = clover['pretty'] #NOTE: Pretty must be able to come close to price multiplier

    return listValue * pretty * fresh #PARAMATER        


def getSubjectiveValue(s, cloverId, clover, userId, market_settings, step):
    cloverObjectiveValue = getObjectiveValue(s, clover, market_settings, step)
    numpy.random.seed([userId,cloverId])
    stdDev = market_settings['stdDev']
    return norm.rvs(loc=cloverObjectiveValue,scale=stdDev)


def processSymmetries(s, clover):
    for sy in ['rotSym', 'x0Sym', 'y0Sym', 'xySym', 'xnySym', 'hasSymmetry']:
        s['symmetries'][sy] += (1 if clover[sy] else 0)
    return s

def processMarketIntentions(s, market_intention, market_settings, step):
    g = s['network']
    
    playerId = market_intention['playerId']
    cloverId = market_intention['cloverId']
    intent = market_intention['intent']
    clover = g.nodes[cloverId]

    if intent == 'toBuy':
        price = clover['price']

        # confirm it is actually for sale (TODO: should throw error)
        if (price == 0):
            print('ERROR: Price is 0 but it is somehow for sale', market_intention)
            return s

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
            s['bc-totalSupply'] -= price
        # else give the coins to the previous owner
        else:
            currentOwnerId = get_owner(g, cloverId)
            currentOwner = g.nodes[currentOwnerId]
            currentOwner['supply'] += price
        # set the new owner and set the new price to 0
        g = set_owner(g, playerId, cloverId)
        g = set_price(g, cloverId, 0)
    else:
        price = getSubjectiveValue(s, cloverId, clover, playerId, market_settings, step)
        g = set_price(g, cloverId, price)
    return s


def processBuysAndSells(s, clover_intention, market_settings, bankId, step):
    g = s['network']
    userId = clover_intention['user']
    user = g.nodes[userId]
    clover = clover_intention['clover']

    s = processSymmetries(s, clover)
    
    (g, cloverId) = add_clover_to_network(g, clover)

    subjectivePrice = getSubjectiveValue(s, cloverId, clover, userId, market_settings, step)
    price = getCloverPrice(s, clover, market_settings)
    
    if (user['type'] == 'miner'):
        clover_intention['intention'] = 'sell'
    else:
        clover_intention['intention'] = "sell" if price > subjectivePrice else 'keep'
    
    reward = getCloverReward(s['symmetries'], clover, market_settings)
    g.nodes[cloverId]['reward'] = reward
    # TODO: if intention == sell BUT reward < gas costs then skip it
    if (clover_intention['intention'] == 'keep'):
        g = set_owner(g, userId, cloverId)
        if (price > user['supply']):
            costToBuy = calculatePriceForTokens(s, market_settings, price)
            user['supply'] = price + user['supply']
            s['bc-totalSupply'] += price
            s['bc-balance'] += costToBuy
            user['eth-spent'] += costToBuy
        user['supply'] -= price
        s['bc-totalSupply'] -= price
        # TODO: maybe give the clover a for sale price?
    else:
        g = set_owner(g, bankId, cloverId)
        listingPrice = getCloverListingPrice(s, clover, market_settings)
        g = set_price(g, cloverId, listingPrice)
        user['supply'] += reward
        s['bc-totalSupply'] += reward
        
    return s

def initialize(market_settings, conditions):
    
    def init_ts(s):
        return calculatePurchaseReturn(market_settings["bc-virtualSupply"], market_settings["bc-virtualBalance"], market_settings["bc-reserveRatio"], market_settings["initialSpend"])
    
    conditions['bc-balance'] = market_settings["initialSpend"]
    conditions['bc-totalSupply'] = init_ts(conditions)
    conditions['network'] = initialize_network(market_settings['number_of_players'], market_settings['number_of_miners'])
    state = {"s" : conditions}
    return state


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
        network.nodes[i]['eth-earned'] = 0
        network.nodes[i]['desired_for_sale_ratio'] = 0.3 # percentage of owned clovers to list
        network.nodes[i]['market_buying_propensity'] = 0.8 # probability to buy pretty clovers from market
        network.nodes[i]['is_active'] = False
        
    for j in range(n,n+m):
        network.add_node(j)
        network.nodes[j]['type'] = "miner"
        network.nodes[j]['cash_out_threshold'] = 0.01
        network.nodes[j]['hashrate'] = norm.rvs(loc=15, scale=2)
        network.nodes[j]['supply'] = 0
        network.nodes[j]['eth-spent'] = 0
        network.nodes[j]['eth-earned'] = 0
        network.nodes[j]['is_active'] = 0.7
    
    network.add_node(n + m)
    network.nodes[n+m]['type'] = "bank"
    return network

#helper functions
def get_nodes_by_type(g, node_type_selection):
    return [node for node in g.nodes if g.nodes[node]['type']== node_type_selection ]

def get_edges_by_type(g, edge_type_selection):
    return [edge for edge in g.edges if g.edges[edge]['type']== edge_type_selection ]

def add_clover_to_network(g, clover, price = 0):
    nodeId = len(g.nodes)
    g.add_node(nodeId)
    g.nodes[nodeId]['type'] = 'clover'
    g.nodes[nodeId]['reward'] = '0'
    g.nodes[nodeId]['price'] = price
    for attr in clover.keys():
        g.nodes[nodeId][attr] = clover[attr]
    return (g, nodeId)

def get_clovers_for_sale(g):
    clovers = get_nodes_by_type(g, "clover")
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
    
def calculatePurchaseReturn(totalSupply, collateral, CW, amount):
    return totalSupply * ((1 + amount / collateral)**CW-1)

def calculateSellReturn(totalSupply, collateral, CW, amount):
    return collateral * (1 - (1 - amount / totalSupply)**(1/CW))

def calculateCurrentPrice(totalSupply, collateral, CW):
    return collateral / (totalSupply * CW)

# SHOULD UPDATE s TO BE TAKING NETWORK AS AN INPUT, FILTERING BY CLOVER NODES
def getCloverReward(syms, clover, market_settings):
    if not clover['hasSymmetry']:
        return 0
    totalRewards = 0
    allSymms = numpy.sum([syms['rotSym'], syms['y0Sym'], syms['x0Sym'], syms['xySym'], syms['xnySym']])
    if clover['rotSym']:
        totalRewards += market_settings['payMultiplier'] * (1 + allSymms) / (syms['rotSym'] + 1)
    if clover['y0Sym']:
        totalRewards += market_settings['payMultiplier'] * (1 + allSymms) / (syms['y0Sym'] + 1)
    if clover['x0Sym']:
        totalRewards += market_settings['payMultiplier'] * (1 + allSymms) / (syms['x0Sym'] + 1)
    if clover['xySym']:
        totalRewards += market_settings['payMultiplier'] * (1 + allSymms) / (syms['xySym'] + 1)
    if clover['xnySym']:
        totalRewards += market_settings['payMultiplier'] * (1 + allSymms) / (syms['xnySym'] + 1)
    return totalRewards

def getCloverListingPrice(s, clover, market_settings):
    rewardAmount = getCloverReward(s['symmetries'], clover, market_settings)
    payAmount = market_settings['base-price'] + (rewardAmount * market_settings['priceMultiplier'])
    return payAmount

def getCloverPrice(s, clover, market_settings):
    rewardAmount = getCloverReward(s['symmetries'], clover, market_settings)
    payAmount = market_settings['base-price'] + rewardAmount
    return payAmount

def getSymmetry(symmetryRarities):
    rand_val = rand()
    
    for i in range(1,len(symmetryRarities)+1):
        if rand_val <= numpy.sum(list(symmetryRarities.values())[0:i]):
            break;
    
    return list(symmetryRarities.keys())[i-1]


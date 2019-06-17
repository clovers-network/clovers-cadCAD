from itertools import *
from numpy.random import rand
import numpy
from scipy.stats import norm
import networkx as nx



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
                
        
    for j in range(n,n+m):
        network.add_node(j)
        network.nodes[j]['type'] = "miner"
    
    network.add_node(n + m)
    network.nodes[n+m]['type'] = "bank"
        
    return network

#helper functions
def get_nodes_by_type(g, node_type_selection):
    
    return [node for node in g.nodes if g.nodes[node]['type']== node_type_selection ]

def get_edges_by_type(g, edge_type_selection):
    return [edge for edge in g.edges if g.edges[edge]['type']== edge_type_selection ]

def add_clover_to_network(g, clover):
    nodeId = len(g.nodes)
    g.add_node(nodeId)
    g.nodes[nodeId]['type'] = 'clover'
    for attr in clover.keys():
        g.nodes[nodeId][attr] = clover[attr]
    return (g, nodeId)

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
    
def calculatePurchaseReturn(tokenSupply, collateral, CW, amount):
    return tokenSupply * ((1 + amount / collateral)**CW-1)

def calculateSellReturn(tokenSupply, collateral, CW, amount):
    return collateral * ((1 + tokensSold / totalSupply)**(1/CW)-1)

def calculateCurrentPrice(tokenSupply, collateral, CW):
    return collateral / (tokenSupply * CW)

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

#def interpretCombinations(combinationTuple):
#    switcher = {
#        ('rotSym',): ('rotSym',),
#        ('x0Sym',): ('x0Sym',),
#        ('y0Sym',): ('y0Sym',),
#        ('xySym',): ('xySym',),
#        ('xnySym',): ('xnySym',),
#        ('rotSym', 'x0Sym'): ('rotSym', 'x0Sym'),
#        ('rotSym', 'y0Sym'): ('rotSym', 'x0Sym', 'y0Sym'),
#        ('rotSym', 'xySym'): ('rotSym', 'xySym', 'xnySym'),
#        ('rotSym', 'xnySym'): ('rotSym', 'xySym', 'xnySym'),
#        ('x0Sym', 'y0Sym'):  ('rotSym', 'x0Sym', 'y0Sym'),
#        ('x0Sym', 'xySym'): ('rotSym', 'x0Sym', 'y0Sym'), # diag or perp
#        ('x0Sym', 'xnySym'): ('rotSym', 'xySym', 'xnySym'), # diag or perp
#        ('y0Sym', 'xySym'): ('rotSym', 'x0Sym', 'y0Sym'), # diag or perp
#        ('y0Sym', 'xnySym'): ('rotSym', 'xySym', 'xnySym'), # diag or perp
#        ('xySym', 'xnySym'): ('rotSym', 'xySym', 'xnySym'),
#        ('rotSym', 'x0Sym', 'y0Sym'): ('rotSym', 'x0Sym', 'y0Sym'),
#        ('rotSym', 'x0Sym', 'xySym'): ('rotSym', 'xySym', 'xnySym'), # diag or perp
#        ('rotSym', 'x0Sym', 'xnySym'): ('rotSym', 'x0Sym', 'y0Sym'), # diag or perp
#        ('rotSym', 'y0Sym', 'xySym'): ('rotSym', 'xySym', 'xnySym'), # diag or perp
#        ('rotSym', 'y0Sym', 'xnySym'): ('rotSym', 'x0Sym', 'y0Sym'), # diag or perp
#        ('rotSym', 'xySym', 'xnySym'): ('rotSym', 'xySym', 'xnySym'),
#        ('x0Sym', 'y0Sym', 'xySym'): ('rotSym', 'x0Sym', 'y0Sym'),
#        ('x0Sym', 'y0Sym', 'xnySym'): ('rotSym', 'x0Sym', 'y0Sym'),
#        ('x0Sym', 'xySym', 'xnySym'): ('rotSym', 'xySym', 'xnySym'),
#        ('y0Sym', 'xySym', 'xnySym'): ('rotSym', 'xySym', 'xnySym'),
#        ('rotSym', 'x0Sym', 'y0Sym', 'xySym'): ('rotSym', 'x0Sym', 'y0Sym'),
#        ('rotSym', 'x0Sym', 'y0Sym', 'xnySym'): ('rotSym', 'x0Sym', 'y0Sym'),
#        ('rotSym', 'x0Sym', 'xySym', 'xnySym'): ('rotSym', 'xySym', 'xnySym'),
#        ('rotSym', 'y0Sym', 'xySym', 'xnySym'): ('rotSym', 'xySym', 'xnySym'),
#        ('x0Sym', 'y0Sym', 'xySym', 'xnySym'): ('rotSym', 'x0Sym', 'y0Sym', 'xySym', 'xnySym'),
#        ('rotSym', 'x0Sym', 'y0Sym', 'xySym', 'xnySym'): ('rotSym', 'x0Sym', 'y0Sym', 'xySym', 'xnySym')
#    }
#    return switcher.get(combinationTuple, "Invalid Sym Combinatoin")
#
#def createCombinationRarities(rarity):    
#    combinationRarities = {}
#    symCombinations = []
#    possibleSyms = ['rotSym', 'x0Sym', 'y0Sym', 'xySym', 'xnySym']
#    
#    for numSymsFound in range(1,6):
#        for symCombination in combinations(possibleSyms, numSymsFound):
#    
#            # array for probabilities of a symmetry's
#            # presence for multiplying probabilities later
#            probabilities = []
#            
#            # add in the probabilities of these symmetries being present
#            for symPresent in symCombination:
#                probabilities.append(rarity[symPresent])
#            
#            # add in the probabilities of the non-present symmetries not being present
#            for symNotPresent in (set(possibleSyms) - set(symCombination)):
#                probabilities.append(1-rarity[symNotPresent])
#                
#            # multiply all the probabilities, to get a total probability for this symCombination
#            combinationRarities[symCombination] = numpy.product(probabilities)
#        
#    #probOfRare = numpy.sum(list(combinationRarities.values()))
#    #
#    #for k,v in combinationRarities.items():
#    #    combinationRarities[k] = v
#    
#    return combinationRarities
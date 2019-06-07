from numpy.random import rand
import numpy
from config import rarity, market_settings
import math
import utils
import networkx as nx



def getClaim():
    
    return rand() < rarity['claimRate']

def getReward(s, clover):
    if not clover['symms']:
        return 0
    totalRewards = 0
    allSymmetries = numpy.sum([s['rotSym'], s['y0Sym'], s['x0Sym'], s['xySym'], s['xnySym']])
    if clover['rotSym']:
        totalRewards += market_settings['payMultiplier'] * (1 + allSymmetries) / 2
    if clover['y0Sym']:
        totalRewards += market_settings['payMultiplier'] * (1 + allSymmetries) / 2
    if clover['x0Sym']:
        totalRewards += market_settings['payMultiplier'] * (1 + allSymmetries) / 2
    if clover['xySym']:
        totalRewards += market_settings['payMultiplier'] * (1 + allSymmetries) / 2
    if clover['xnySym']:
        totalRewards += market_settings['payMultiplier'] * (1 + allSymmetries) / 2
    return totalRewards


# mines n clovers, and returns only the rare ones, with rarity
def mine_clovers(num_clovers):
    possibleSyms = ['rotSym', 'y0Sym', 'x0Sym', 'xySym', 'xnySym']
    rare_clovers = num_clovers*rarity['hasSymmetry']
    rare_clovers = (1 if rand() < (rare_clovers - math.floor(rare_clovers)) else 0) + math.floor(rare_clovers)
    
    clovers = []
    for i in range(1,rare_clovers+1):
        
        clover = {}

        symmetry = utils.getSymmetry(rarity['symmetries'])
    
        for sym in possibleSyms:
            clover[sym] = False
    
        if symmetry in possibleSyms:
            clover[symmetry] = True
        else:
            if sym == 'diagRotSym':
                clovers['xySym'] = clovers['xnySym'] = clovers['rotSym'] = True
            if sym == 'perpRotSym':
                clovers['x0Sym'] = clovers['y0Sym'] = clovers['rotSym'] = True
            if sym == 'allSym':
                for sym in possibleSyms:
                    clover[sym] = True
        
        clover['pretty'] = (rand() < rarity['rarePretty'])
        clover['symms'] = True
        
        clovers.append(clover)
    
    return clovers


def player_policy(params, step, sL, s):
    
    # mine the clover
    # player_settings = params['player_mining']
    params = params[0]
    
    player_intentions = {}
    
    # iterate through players in a given timestep period and their individual logics
    for node in utils.get_nodes_by_type(s['network'], 'player'):
        
        player = s['network'].nodes[node]
        
        # is the player active in this timestep (probabalistic function)
        if params['player_active']():
            
            # number of hashes calcuated by this player during the period
            num_hashes = player['hashrate'] \
                         * (params['duration']*60) \
                         * player['player_active_percent']
            
            # returns an array of al rare clovers mined during the period
            rare_clovers = mine_clovers(num_hashes)
            
            # PLACEHOLDER: add function for generating non-sym pretty clovers via UI
            
            # number of clovers this user will keep & sell during the time period
            clovers_to_keep = []
            clovers_to_sell = []            
            
            
            for clover in rare_clovers:
                
                if clover['pretty']:
                    # with each additional clover kept, reduce the probability
                    # of a player choosing to keep another pretty clover
                    if (rand() < (1 / 1 + len(clovers_to_keep))):
                        clovers_to_keep.append(clover)
                else:
                    clovers_to_sell.append(clover)
                        
            player_intentions[node] = {
                'clovers_to_sell': clovers_to_sell,
                'clovers_to_keep': clovers_to_keep
            }
    
    return {'player_intentions': player_intentions}
    
    # if rare_clovers:
    #     clover = rare_clovers[0]
    #     # calculate potential rewards for clover
    #     rewardAmount = getReward(s, clover)
    #     
    #     claim = getClaim()
    #     payAmount = (rewardAmount + market_settings['base-price']) * market_settings['priceMultiplier']
    # 
    #     # if the cost to buy is larger than the total user based supply (non-bank owned) there is no possible user
    #     # with enough club token to buy it
    #     if payAmount > s['bc-totalSupply']:
    #         claim = False
    #     if claim:
    #         totalSupply = s['bc-totalSupply'] - payAmount
    #     else:
    #         totalSupply = s['bc-totalSupply'] + rewardAmount
    #         
    #     return ({
    #         'rewards': clover,
    #         'rewardAmount': rewardAmount,
    #         'payAmount': payAmount,
    #         'claim': claim,
    #         'userClovers': rare_clovers
    #     })
    # 
    # 
    # return ({'claim': False, 'rewardAmount': 0, 'rewards': {'x0Sym': False, 'y0Sym': False, 'xySym': False, 'xnySym': False, 'rotSym': False, 'symms': False}})

    

def miner_policy(params, step, sL, s):
    hash_rate = 15 # clovers per second
    
    miner_pool = 3 # number of miners
    
    miner_pct_online = 0.3
    
    clovers_hashed = (hash_rate*60*60)*miner_pool*miner_pct_online
    
    clover = mine_clover()
from numpy.random import rand
import numpy
from config import rarity, market_settings
import math
import utils
import networkx as nx



def getClaim():
    return rand() < rarity['claimRate']

# mines n clovers, and returns only the rare ones, with rarity
def mine_clovers(num_hashes):
    possibleSyms = ['rotSym', 'y0Sym', 'x0Sym', 'xySym', 'xnySym']
    
    
    # first determine how many rare clovers are found with the given hashrate
    rare_clovers = num_hashes*rarity['hasSymmetry']
    rare_clovers = (1 if rand() < (rare_clovers - math.floor(rare_clovers)) else 0) + math.floor(rare_clovers)
    
    clovers = []
    
    # for each rare clover, determine its symmetries and prettiness from utility function
    # and return them as an array 
    for i in range(rare_clovers):
        
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
        clover['hasSymmetry'] = True
        
        clovers.append(clover)
    
    return clovers


def player_policy(params, step, sL, s):
    
    params = params[0]
    
    player_intentions = {}
    clover_intentions = []
    
    # iterate through players in a given timestep period and their individual logics
    for node in utils.get_nodes_by_type(s['network'], 'player'):
        
        player = s['network'].nodes[node]
        
        # is the player active in this timestep (probabalistic function)
        if params['player_active']():
            
            # number of hashes calcuated by this player during the period
            num_hashes = player['hashrate'] \
                         * (params['duration']*60) \
                         * player['player_active_percent']
            
            # returns an array of all rare clovers mined during the period
            rare_clovers = mine_clovers(num_hashes)
            
            # PLACEHOLDER: add function for generating non-sym pretty clovers via UI
            
            for clover in rare_clovers:
                
                clover_intention = {"user": node, "clover": clover}
                
                if clover['pretty']:
                    # with each additional clover kept, reduce the probability
                    # of a player choosing to keep another pretty clover
                    if (rand() < (1 / 1 + len(clovers_to_keep))):
                        clover_intention['intention'] = "keep"
                    else:
                        clover_intention['intention'] = "sell"
                else:
                    clover_intention['intention'] = "sell"
                        
                clover_intentions.append(clover_intention)
    
    return {'clover_intentions': clover_intentions}
    

def miner_policy(params, step, sL, s):
    
    clover_intentions = []
    
    for node in utils.get_nodes_by_type(s['network'], 'miner'):
        miner = s['network'].nodes[node]
        miner_pct_online = 1 # miner always online
        hash_rate = miner['hashrate']
        is_active = miner['is_active']
        
        num_hashes = (hash_rate*params['duration']*60)*miner_pct_online*is_active
        
        clovers = mine_clovers(num_hashes)
        
        for clover in clovers:
            clover_intention = {
                "user": node,
                "intention": "sell"
                "clover": clover
            }
            clover_intentions.append(clover_intention)
            
    return clover_intentions


def market_activity_policy(params, step, sL, s):
    
    g = s['network']
    
    clovers_for_sale = utils.get_clovers_for_sale(g)
    
    def update_listings(player):
        owned_clovers = utils.get_owned_clovers(g, player)
        
        owned_clovers_for_sale = []
        owned_clovers_not_for_sale = []
        for clover in owned_clovers:
            if g.nodes[clover]['for_sale']:
                owned_clovers_for_sale.append(clover)
            else:
                owned_clovers_not_for_sale.append(clover)
        
        
            
            
    for node in utils.get_nodes_by_type(s['network'], 'player'):
        player = s['network'].nodes[node]
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
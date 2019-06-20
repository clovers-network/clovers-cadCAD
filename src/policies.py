from numpy.random import rand, shuffle
import numpy
from random import sample
from config import rarity, market_settings
import math
import utils
import networkx as nx



def getClaim():
    return rand() < rarity['claimRate']

# mines n clovers, and returns only the rare ones, with rarity
def mine_clovers(num_hashes, step):
    possibleSyms = ['rotSym', 'y0Sym', 'x0Sym', 'xySym', 'xnySym']
    
    
    # first determine how many rare clovers are found with the given hashrate
    rare_clovers = num_hashes*rarity['hasSymmetry']
    rare_clovers = (1 if rand() < (rare_clovers - math.floor(rare_clovers)) else 0) + math.floor(rare_clovers)
    
    clovers = []
    
    # for each rare clover, determine its symmetries and prettiness from utility function
    # and return them as an array 
    for i in range(rare_clovers):
        
        clover = {}
        clover['step'] = step

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
        
        clover['pretty'] = rand() + 1 if (rand() < rarity['rarePretty']) else 0
        clover['hasSymmetry'] = True
        
        clovers.append(clover)
    
    return clovers


def player_policy(params, step, sL, s):
    
    params = params[0]
    
    active_players = []
    clover_intentions = []
    s = s['s'] # wrap state for backwards compatibility
    # iterate through players in a given timestep period and their individual logics
    for node in utils.get_nodes_by_type(s['network'], 'player'):
        
        player = s['network'].nodes[node]
        
        # is the player active in this timestep (probabalistic function)
        if params['player_active']():
            active_players.append(node)
            
            # number of hashes calcuated by this player during the period
            num_hashes = player['hashrate'] \
                         * (params['duration']*60) \
                         * player['player_active_percent']
            
            # returns an array of all rare clovers mined during the period
            rare_clovers = mine_clovers(num_hashes, step)
            
            # TODO: add function for generating non-sym pretty clovers via UI
            
            clovers_to_keep = 0
            
            for clover in rare_clovers:
                clover_intentions.append({"user": node, "clover": clover})
    s = {"s": s} # wrap state for backwards compatibility 
    shuffle(clover_intentions)
    return {'clover_intentions': clover_intentions, 'active_players': active_players}
    

def miner_policy(params, step, sL, s):
    params = params[0]
    s = s['s'] # wrap state for backwards compatibility
    clover_intentions = []
    for node in utils.get_nodes_by_type(s['network'], 'miner'):
        miner = s['network'].nodes[node]
        miner_pct_online = 1 # miner always online
        hash_rate = miner['hashrate']
        is_active = miner['is_active']
        
        num_hashes = (hash_rate*params['duration']*60)*miner_pct_online*is_active
        
        clovers = mine_clovers(num_hashes, step)
        
        for clover in clovers:
            clover_intention = {
                "user": node,
                "intention": "sell",
                "clover": clover
            }
            clover_intentions.append(clover_intention)

    s = {"s": s}  # wrap state for backwards compatibility
    shuffle(clover_intentions)
    return {'clover_intentions': clover_intentions}


def market_activity_policy(params, step, sL, s):
    params = params[0]
    s = s['s'] # wrap state for backwards compatibility
    g = s['network']
    def get_sells(playerId):
        owned_clovers = utils.get_owned_clovers(g, playerId)
        owned_clovers_for_sale = []
        owned_clovers_not_for_sale = []
        for clover in owned_clovers:
            if g.nodes[clover]['price'] > 0:
                owned_clovers_for_sale.append(clover)
            else:
                owned_clovers_not_for_sale.append(clover)
        
        for_sale_ratio = 1 if len(owned_clovers) == 0 else len(owned_clovers_for_sale)/len(owned_clovers)
        desired_ratio = g.nodes[playerId]['desired_for_sale_ratio']
        
        to_sell = []
        if for_sale_ratio < desired_ratio:
            for cloverId in owned_clovers_not_for_sale:
                new_ratio = len(to_sell + owned_clovers_for_sale)/len(owned_clovers)
                if rand() < ((desired_ratio - new_ratio)/desired_ratio):
                    to_sell.append({
                        'playerId': playerId,
                        'cloverId': cloverId,
                        'intent': 'toSell'
                    })
        return to_sell

    clovers_for_sale = utils.get_clovers_for_sale(g)

    # shuffle the clovers potentially for sale
    shuffle(clovers_for_sale)

    def get_buys(playerId, clovers_for_sale):
        to_buy = []

        # PARAMETER
        sample_size = 25 if len(clovers_for_sale) > 25 else len(clovers_for_sale)
        random_clovers = sample(clovers_for_sale, sample_size)
        for random_clover_id in random_clovers:
            random_clover = g.nodes[random_clover_id]
            price = random_clover['price']
            subjectivePrice = utils.getSubjectiveValue(s, random_clover_id, random_clover, playerId, market_settings, step)
            if (subjectivePrice < price):
                # remove clover from subsequent possible clovers
                clovers_for_sale.remove(random_clover_id)
                to_buy.append({
                    'playerId': playerId,
                    'cloverId': random_clover_id,
                    'intent': 'toBuy'
                })
        return to_buy
    
    # for each player
    # 
    # scan some assortment of clovers for sale (more of the recent ones)
    # if there are any clovers for sale below the subjective price
    # then buy them
    # 
    # scan some assortment of user's own clovers (more of the older ones)
    # set them for sale at the subjective price

    handleClovers = []
    for playerId in utils.get_nodes_by_type(s['network'], 'player'):
        if params['player_active']():
            handleClovers = handleClovers + get_sells(playerId) + get_buys(playerId, clovers_for_sale)
    s = {"s": s}  # wrap state for backwards compatibility
    # if we shuffle them here, the desire to buy will be different from calculated here
    # we could remedy this by moving the entire operation into the state update function
    # but then we will either have to run the loop on all players twice
    # or we won't be using the policy at all....
    
    # would rather sacrifice the fact that players are doing all their own buys and sells
    # at once instead of interspercing them, because it simplifies the appraisal so much
    # : (
    
    #     shuffle(clover_intentions)
    return {'market_intentions': handleClovers}
            
 
    
    
    
    
    
    
    
    
    
    
    
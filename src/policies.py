from numpy.random import rand, shuffle
import numpy
from random import sample
from config import rarity, market_settings
import math
import utils
import networkx as nx

def participant_pool_policy(params, step, sL, s):
    # print('participant_pool_policy')
    policy = {}
    playerCount = len(s['s']['players'])
    minerCount = len(s['s']['miners'])
    timestep = s['timestep'] + s['s']['previous-timesteps']
    if (timestep != 0 and timestep % market_settings['increase_participants_every_x_steps'] == 0):
        policy['new-players'] = math.ceil(playerCount * market_settings['player_multiplier'])
        policy['new-miners'] = math.ceil(minerCount * market_settings['miner_multiplier'])
    # print('end-participant_pool_policy')
    return policy

def getClaim():
    return rand() < rarity['claimRate']

# TODO: Move this to config
def player_active():
    awake_likelihood = 0.6  # 14.4 hours awake per day
    active_likelihood = 0.005 # 1/200 - one out of every 200 users active
    return rand() < (awake_likelihood*active_likelihood)


def player_policy(params, step, sL, s):
    # print('player_policy')
    # params = params[0]
    active_players = []
    clover_intentions = []
    timestep = s['timestep']
    s = s['s'] # wrap state for backwards compatibility
    s['network'] = utils.getNetwork(params)
    cloverCount = len(s['clovers'])
    timestep = timestep + s['previous-timesteps']
    # iterate through players in a given timestep period and their individual logics
    for node in utils.get_nodes_by_type(s, 'player'):
        
        player = s['network'].nodes[node]
        
        # is the player active in this timestep (probabalistic function)
        if player_active():
            active_players.append(node)
            
            # number of hashes calcuated by this player during the period
            # assuming timestep of 1 hour
            num_hashes = player['hashrate'] \
                         *60*60 \
                         * player['player_active_percent']
            
            # returns an array of all rare clovers mined during the period
            rare_clovers = utils.mine_clovers(num_hashes, timestep, cloverCount, rarity, market_settings)
            
            # TODO: add function for generating non-sym pretty clovers via UI            
            for clover in rare_clovers:
                clover_intentions.append({"user": node, "clover": clover})
    shuffle(clover_intentions)
    # print('end-player_policy')
    return {'clover_intentions': clover_intentions, 'active_players': active_players}
    

def miner_policy(params, step, sL, s):
    # print('miner_policy')
    # params = params[0]
    timestep = s['timestep']
    s = s['s'] # wrap state for backwards compatibility
    s['network'] = utils.getNetwork(params)
    clover_intentions = []
    cloverCount = len(s['clovers'])
    timestep = timestep + s['previous-timesteps']
    for node in utils.get_nodes_by_type(s, 'miner'):
        miner = s['network'].nodes[node]
        miner_pct_online = market_settings['miner_pct_online'] # miner always online
        hash_rate = miner['hashrate']
        is_active = miner['is_active']

        num_hashes = (hash_rate*60*60)*miner_pct_online*is_active
        
        clovers = utils.mine_clovers(num_hashes, timestep, cloverCount, rarity, market_settings)
        
        for clover in clovers:
            clover_intention = {
                "user": node,
                "intention": "sell",
                "clover": clover
            }
            clover_intentions.append(clover_intention)

    shuffle(clover_intentions)
    # print('end-miner_policy')
    return {'clover_intentions': clover_intentions}


def market_activity_policy(params, step, sL, s):
    # print('market_activity_policy')
    # params = params[0]
    timestep = s['timestep']
    s = s['s'] # wrap state for backwards compatibility
    s['network'] = utils.getNetwork(params)
    g = s['network']
    timestep = timestep + s['previous-timesteps']
    def get_sells(playerId):
        owned_clovers = utils.get_owned_clovers(g, playerId) #TODO: check performance
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

    all_clovers_for_sale = utils.get_clovers_for_sale(s)

    # shuffle the clovers potentially for sale
    shuffle(all_clovers_for_sale)
    
    gas_fee = market_settings['register_clover_cost_in_eth'] * s['gasPrice']

    def get_buys(playerId, all_clovers_for_sale):
        # print('get_buys')
        to_buy = []
        hourly_attention_rate = math.floor(market_settings['hourly_attention_rate_for_buying_clovers'])
        sample_size = hourly_attention_rate if len(all_clovers_for_sale) > hourly_attention_rate else len(all_clovers_for_sale)
        random_clovers = sample(all_clovers_for_sale, sample_size)
        for random_clover_id in random_clovers:
            random_clover = g.nodes[random_clover_id]
            price = random_clover['price']
            price = price + gas_fee
            subjectivePrice = utils.getSubjectiveValue(s, random_clover_id, random_clover, playerId, market_settings, timestep, params)
            market_buying_propensity = g.nodes[playerId]['market_buying_propensity']
            _rand = rand()
            if (subjectivePrice > price and market_buying_propensity > _rand):
                # remove clover from subsequent possible clovers
                all_clovers_for_sale.remove(random_clover_id)
                to_buy.append({
                    'playerId': playerId,
                    'cloverId': random_clover_id,
                    'intent': 'toBuy'
                })
        # print('end-get_buys')
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
    for playerId in utils.get_nodes_by_type(s, 'player'):
        if player_active():
            handleClovers = handleClovers + get_sells(playerId) + get_buys(playerId, all_clovers_for_sale)
    # if we shuffle them here, the desire to buy will be different from calculated here
    # we could remedy this by moving the entire operation into the state update function
    # but then we will either have to run the loop on all players twice
    # or we won't be using the policy at all....
    
    # would rather sacrifice the fact that players are doing all their own buys and sells
    # at once instead of interspercing them, because it simplifies the appraisal so much
    # : (
    
    #     shuffle(clover_intentions)
    # print('end-market_activity_policy')
    return {'market_intentions': handleClovers}
            
 
    
    
    
    
    
    
    
    
    
    
    

import utils
import itertools
from config import market_settings
from functools import reduce
import json
import os.path

def initialize(params, step, sL, s, _input):
    print("timestep", s['timestep'])
    print("clovers", len(s['s']['clovers']))
    if (s['timestep'] == 0):
        if os.path.exists("network.gpickle"):
            os.remove("network.gpickle")
        if os.path.exists("last-run.json"):
            os.remove("last-run.json")
        if not os.path.exists('./last-run.json'):
            s = utils.initialize(market_settings, s['s'])
            utils.saveNetwork(s['s']['network'])
            s['s']['network'] = None
        else:
            with open('./last-run.json', 'r') as f:
                s = json.load(f)
                s['s']['previous-timesteps'] = 0
    return ('s', s['s'])

def save_file(params, step, sL, s, _input):
    with open('last-run.json', 'w+') as f:  # writing JSON object
        json.dump(s, f)
    return ('s', s['s'])


def update_participant_pool(params, step, sL, s, _input):
    s = s['s']
    g = utils.getNetwork()
    s['network'] = g
    if 'new-players' in _input:
        (g, players, miners) = utils.seed_network(_input['new-players'], 0, g, market_settings)
        s['players'] = s['players'] + players
    if 'new-miners' in _input:
        (g, players, miners) = utils.seed_network(0, _input['new-miners'], g, market_settings)
        s['miners'] = s['miners'] + miners
    utils.saveNetwork(s['network'])
    s['network'] = None
    return ('s', s)

def update_state(params, step, sL, s, _input):
    _s = s
    s = s['s']
    s['network'] = utils.getNetwork()
    if 'active_players' in _input:
        s['network'] = updateActivePlayers(s, _input['active_players'])
    if 'clover_intentions' in _input:
        s = processCloverIntentions(s, _input['clover_intentions'], _s['timestep'])
    if 'market_intentions' in _input:
        s = processMarketIntentions(s, _input['market_intentions'], _s['timestep'])
    utils.saveNetwork(s['network'])
    s['network'] = None
    return ('s', s)

def update_state_miner_policy(params, step, sL, s, _input):
    _s = s
    s = s['s']
    s['network'] = utils.getNetwork()
    if 'clover_intentions' in _input:
        s = processCloverIntentions(s, _input['clover_intentions'], _s['timestep'])
    s = processMinerCashOuts(s, market_settings)
    utils.saveNetwork(s['network'])
    s['network'] = None
    return ('s', s)
    
def updateActivePlayers(s, active_players):
    all_players = utils.get_nodes_by_type(s, 'player')
    g = s['network']
    for player in all_players:
        if player in active_players:
            g.nodes[player]['is_active'] = True
        else:
            g.nodes[player]['is_active'] = False
    return g

def processMarketIntentions(s, market_intentions, step):
    for market_intention in market_intentions:
        s = utils.processMarketIntentions(s, market_intention, market_settings, step)
    return s

def processCloverIntentions(s, clover_intentions, step):
    bankId = utils.get_nodes_by_type(s, "bank")
    for clover_intention in clover_intentions:
        s = utils.processBuysAndSells(s, clover_intention, market_settings, bankId, step)
    return s

def processMinerCashOuts(s, marketSettings):
    g = s['network']
    
    minerNodes = utils.get_nodes_by_type(s, 'miner')
    
    for node in minerNodes:
        miner = g.nodes[node]
        cash_out_amount = utils.calculateCashout(s, marketSettings, miner['supply']) # returns ETH
        gas_fee = marketSettings['sell_coins_cost_in_eth']
        
        if (cash_out_amount - gas_fee) > miner['cash_out_threshold']:
            miner['eth-earned'] += cash_out_amount
            s['bc-balance'] -= cash_out_amount
            s['bc-totalSupply'] -= miner['supply']
            miner['eth-spent'] += gas_fee
            miner['supply'] = 0
#         else:
#             print('cash out not worh the gas')
                
    return s


 
# # State update functions
# def bc_totalSupply(params, step, sL, s, _input):
#     if _input['clover_intentions']:
#         for clover_intention in _input['clover_intentions']:
#             # updates s[bc-totalSupply], s[bc-balance], network[user] & network[clover]
#             s = utils.processBuysAndSells(s, clover_intention, market_settings)
#     return ('bc-totalSupply', s['bc-totalSupply'])

# def update_symmetries(params, step, sL, s, _input):
#     if _input['clover_intentions']:
#         for clover_intention in _input['clover_intentions']:
#             s = utils.processSymmetries(s, clover_intention['clover']) # could also use processBuysAndSells()
#     return ('symmetries', s['symmetries'])

# def bc_balance(params, step, sL, s, _input):
#     if _input['clover_intentions']:
#         for clover_intention in _input['clover_intentions']:
#             # updates s[bc-totalSupply], s[bc-balance], network[user] & network[clover]
#             s = utils.processBuysAndSells(s, clover_intention, market_settings)
#     return ('bc-balance', s['bc-balance'])

# def update_network(params, step, sL, s, _input):
#     if _input['clover_intentions']:
#         for clover_intention in _input['clover_intentions']:
#             # updates s[bc-totalSupply], s[bc-balance], network[user] & network[clover]
#             s = utils.processBuysAndSells(s, clover_intention, market_settings)
#     return ('network', s['network'])
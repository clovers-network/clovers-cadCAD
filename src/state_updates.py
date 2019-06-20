import utils
import itertools
from config import market_settings
from functools import reduce



def update_state(params, step, sL, s, _input):
    s = s['s']
    if 'active_players' in _input:
        s['network'] = updateActivePlayers(s['network'], _input['active_players'])
    if 'clover_intentions' in _input:
        s = processCloverIntentions(s, _input['clover_intentions'], step)
    if 'market_intentions' in _input:
        s = processMarketIntentions(s, _input['market_intentions'], step)
    return ('s', s)

def update_state_miner_policy(params, step, sL, s, _input):
    s = s['s']
    if 'clover_intentions' in _input:
        s = processCloverIntentions(s, _input['clover_intentions'], step)
    s = processMinerCashOuts(s, market_settings)
    return ('s', s)
    
def updateActivePlayers(g, active_players):
    all_players = utils.get_nodes_by_type(g, 'player')
    
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
    bankId = utils.get_nodes_by_type(s['network'], "bank")[0]
    for clover_intention in clover_intentions:
        s = utils.processBuysAndSells(s, clover_intention, market_settings, bankId, step)
    return s

def processMinerCashOuts(s, marketSettings):
    g = s['network']
    
    minerNodes = utils.get_nodes_by_type(g, 'miner')
    
    for node in minerNodes:
        miner = g.nodes[node]
        
        cash_out_amount = utils.calculatePriceForTokens(s, marketSettings, miner['supply'])
        gas_fee = 0
        
        if (cash_out_amount - gas_fee) > miner['cash_out_threshold']:
            miner['eth-earned'] += cash_out_amount
            s['bc-balance'] -= cash_out_amount
            miner['eth-spent'] += gas_fee
            miner['supply'] = 0
                
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
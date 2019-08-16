import utils
import itertools
from config import market_settings
from functools import reduce
import json
import os.path

def with_network(s, params, updater):
    state = s['s']
    state['network'] = utils.getNetwork(params)

    state = updater(state)

    utils.saveNetwork(state['network'], params)
    state['network'] = None

    return ('s', state)

def initialize(params, step, sL, s, _input):
    #print("Paramset: %s" % params)
    #print("    timestep", s['timestep'])
    #print("    clovers", len(s['s']['clovers']))

    if (s['timestep'] == 0):
        filename = utils.network_filename(params)
        if os.path.exists(filename):
            os.remove(filename)

        s = utils.initialize(params, market_settings, s['s'])
        utils.saveNetwork(s['s']['network'], params)
        s['s']['network'] = None

    # reset timestepStats, as these are counters which should be reset
    # at every new timestep
    for key in s['s']['timestepStats'].keys():
        s['s']['timestepStats'][key] = 0
    return ('s', s['s'])

def update_participant_pool(params, step, sL, s, _input):
    def participant_pool_updater(state):
        g = state['network']
        if 'new-players' in _input:
            (g, players, miners) = utils.seed_network(_input['new-players'], 0, g, market_settings)
            state['players'] = state['players'] + players
        if 'new-miners' in _input:
            (g, players, miners) = utils.seed_network(0, _input['new-miners'], g, market_settings)
            state['miners'] = state['miners'] + miners
        return state

    return with_network(s, params, participant_pool_updater)

def update_state(params, step, sL, s, _input):
    def state_updater(state):
        if 'active_players' in _input:
            state['network'] = updateActivePlayers(state, _input['active_players'])
        if 'clover_intentions' in _input:
            state = processCloverIntentions(params, state, _input['clover_intentions'], s['timestep'])
        if 'market_intentions' in _input:
            state = processMarketIntentions(params, state, _input['market_intentions'], s['timestep'])
        return state

    return with_network(s, params, state_updater)

def update_state_miner_policy(params, step, sL, s, _input):
    def miner_policy_updater(state):
        if 'clover_intentions' in _input:
            state = processCloverIntentions(params, state, _input['clover_intentions'], s['timestep'])
        state = processMinerCashOuts(params, state, market_settings)
        return state

    return with_network(s, params, miner_policy_updater)

def updateActivePlayers(state, active_players):
    all_players = utils.get_nodes_by_type(state, 'player')
    g = state['network']
    for player in all_players:
        if player in active_players:
            g.nodes[player]['is_active'] = True
        else:
            g.nodes[player]['is_active'] = False
    return g

def processMarketIntentions(params, state, market_intentions, step):
    for market_intention in market_intentions:
        state = utils.processMarketIntentions(state, market_intention, market_settings, step, params)
    return state

def processCloverIntentions(params, state, clover_intentions, step):
    bankId = utils.get_nodes_by_type(state, "bank")
    for clover_intention in clover_intentions:
        state = utils.processBuysAndSells(state, clover_intention, market_settings, bankId, step, params)
    return state

def processMinerCashOuts(params, state, marketSettings):
    g = state['network']

    minerNodes = utils.get_nodes_by_type(state, 'miner')

    for node in minerNodes:
        miner = g.nodes[node]
        cash_out_amount = utils.calculateCashout(state, params, miner['supply']) # returns ETH
        gas_fee = marketSettings['sell_coins_cost_in_eth']

        if (cash_out_amount - gas_fee) > miner['cash_out_threshold']:
            miner['eth-earned'] += cash_out_amount
            state['bc-balance'] -= cash_out_amount
            state['bc-totalSupply'] -= miner['supply']
            miner['eth-spent'] += gas_fee
            miner['supply'] = 0
#         else:
#             print('cash out not worh the gas')
    return state


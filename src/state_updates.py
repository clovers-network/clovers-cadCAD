import utils
import itertools
from config import market_settings
from functools import reduce

# State update functions
def bc_totalSupply(params, step, sL, s, _input):
    add = 0
    if _input['player_intentions']:
        
        to_sell = [x['clovers_to_sell'] for x in _input['player_intentions'].values()] 
        # sum clover rewards of list of list (this is the amount of clubtokens leaving the bank)
        total_reward = sum([utils.getCloverReward(s, clover, market_settings) for clover in itertools.chain(*to_sell)])
        
        to_keep = [x['clovers_to_keep'] for x in _input['player_intentions'].values()]
        # sum clover prices of list of list (this is the amount of clubtokens going to the bank)
        total_price = sum([utils.getCloverPrice(s, clover, market_settings) for clover in itertools.chain(*to_keep)])
        
        add = total_price - total_reward        
        
    else:
        add = 0
    return ('bc-totalSupply', add + s['bc-totalSupply'])

def update_symmetries(params, step, sL, s, _input):
    updatedSyms = dict(s['symmetries'])

    if _input['player_intentions']:
        new_clover_lists = [x['clovers_to_sell'] + x['clovers_to_keep'] for x in _input['player_intentions'].values()]

        for clover in itertools.chain(*new_clover_lists):
            for sy in ['rotSym', 'x0Sym', 'y0Sym', 'xySym', 'xnySym', 'hasSymmetry']:
                updatedSyms[sy] += (1 if clover[sy] else 0)
    return ('symmetries', updatedSyms)


def bc_balance(params, step, sL, s, _input):
    return ('bc-balance', s['bc-balance'])

def cloversForSale(params, step, sL, s, _input):
    return ('cloversForSale', s['cloversForSale'])

def update_network(params, step, sL, s, _input):
    g = s['network']
    
    player_intentions = _input['player_intentions']
    bank = utils.get_nodes_by_type(g, "bank")[0]

    for player, intentions in player_intentions.items():
        for clover in intentions['clovers_to_sell']:
            (g, nodeId) = utils.add_clover_to_network(g, clover)
            utils.set_owner(g, bank, nodeId) 
            g.nodes[player]['supply'] += utils.getCloverReward(s, clover, market_settings)
        
        for clover in intentions['clovers_to_keep']:
            (g, nodeId) = utils.add_clover_to_network(g, clover)
            utils.set_owner(g, player, nodeId) 
            g.nodes[player]['supply'] -= utils.getCloverPrice(s, clover, market_settings)
        
    return ('network', g)
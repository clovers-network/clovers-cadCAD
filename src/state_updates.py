import utils
from config import market_settings

# State update functions
def bc_totalSupply(params, step, sL, s, _input):
    add = 0
    if _input['claim']:
        add =  -_input['payAmount']
    else:
        add = _input['rewardAmount']
    return ('bc-totalSupply', add + s['bc-totalSupply'])

def bc_balance(params, step, sL, s, _input):
    return ('bc-balance', s['bc-balance'])

def bankClovers(params, step, sL, s, _input):
    add = 0
    if _input['claim']:
        add = 1
    return ('bankClovers', add + s['bankClovers'])

def userClovers(params, step, sL, s, _input):
    clovers_to_keep = _input['userClovers']
    return ('userClovers', s['userClovers'] + clovers_to_keep)
    
def symms(params, step, sL, s, _input):
    if _input['rewards']['symms']:
        return ('symms', s['symms'] + 1)
    else:
        return ('symms', s['symms'])

def clovers(params, step, sL, s, _input):
    return ('clovers', (s['clovers'] + 1))

def rotSym(params, step, sL, s, _input):
    return ('rotSym', s['rotSym'] + _input['rewards']['rotSym'])

def y0Sym(params, step, sL, s, _input):
    return ('y0Sym', s['y0Sym'] + _input['rewards']['y0Sym'])

def x0Sym(params, step, sL, s, _input):
    return ('x0Sym', s['x0Sym'] + _input['rewards']['x0Sym'])

def xySym(params, step, sL, s, _input):
    return ('xySym', s['xySym'] + _input['rewards']['xySym'])

def xnySym(params, step, sL, s, _input):
    return ('xnySym', s['xnySym'] + _input['rewards']['xnySym'])

def cloversForSale(params, step, sL, s, _input):
    return ('cloversForSale', s['cloversForSale'])


def update_network(params, step, sL, s, _input):
    g = s['network']
    
    player_intentions = _input['player_intentions']
    bank = utils.get_nodes_by_type(g, "bank")[0]

    
    for player, intentions in player_intentions.items():
        
        for clover in intentions['clovers_to_sell']:
            (g, nodeId) = utils.add_clover_to_network(g, clover)
            g.add_edge(bank, nodeId)
            g.edges[(bank, nodeId)]['type'] = "owns"
            g.nodes[player]['supply'] += utils.getCloverReward(s, clover, market_settings)
        
        for clover in intentions['clovers_to_keep']:
            (g, nodeId) = utils.add_clover_to_network(g, clover)
            g.add_edge(player, nodeId)
            g.edges[(player, nodeId)]['type'] = "owns"
            g.nodes[player]['supply'] -= utils.getCloverPrice(s, clover, market_settings)
        
    return ('network', g)
            
            
            
        
        
    
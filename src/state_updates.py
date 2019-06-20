import utils
import itertools
from config import market_settings
from functools import reduce

# State update functions
def bc_totalSupply(params, step, sL, s, _input):
    if _input['clover_intentions']:
        for clover_intention in _input['clover_intentions']:
            # updates s[bc-totalSupply], s[bc-balance], network[user] & network[clover]
            s = utils.processBuysAndSells(s, clover_intention, market_settings)
    return ('bc-totalSupply', s['bc-totalSupply'])

def update_symmetries(params, step, sL, s, _input):
    if _input['clover_intentions']:
        for clover_intention in _input['clover_intentions']:
            s = utils.processSymmetries(s, clover_intention['clover']) # could also use processBuysAndSells()
    return ('symmetries', s['symmetries'])

def bc_balance(params, step, sL, s, _input):
    if _input['clover_intentions']:
        for clover_intention in _input['clover_intentions']:
            # updates s[bc-totalSupply], s[bc-balance], network[user] & network[clover]
            s = utils.processBuysAndSells(s, clover_intention, market_settings)
    return ('bc-balance', s['bc-balance'])

def update_network(params, step, sL, s, _input):
    if _input['clover_intentions']:
        for clover_intention in _input['clover_intentions']:
            # updates s[bc-totalSupply], s[bc-balance], network[user] & network[clover]
            s = utils.processBuysAndSells(s, clover_intention, market_settings)
    return ('network', s['network'])
from numpy.random import rand
from config import rarity, market_settings


def getClaim(s):
    return rand() < rarity['claimRate']

def getReward(s, rewards):
    if not rewards['symms']:
        return 0
    totalRewards = 0
    allSymmetries = s['rotSym'] + s['y0Sym'] + s['x0Sym'] + s['xySym'] + s['xnySym']
    if rewards['rotSym'] == 1:
        totalRewards = market_settings['payMultiplier'] * (1 + allSymmetries) / (1 + s['rotSym'])
    if rewards['y0Sym'] == 1:
        totalRewards = market_settings['payMultiplier'] * (1 + allSymmetries) / (1 + s['y0Sym'])
    if rewards['x0Sym'] == 1:
        totalRewards = market_settings['payMultiplier'] * (1 + allSymmetries) / (1 + s['x0Sym'])
    if rewards['xySym'] == 1:
        totalRewards = market_settings['payMultiplier'] * (1 + allSymmetries) / (1 + s['xySym'])
    if rewards['xnySym'] == 1:
        totalRewards = market_settings['payMultiplier'] * (1 + allSymmetries) / (1 + s['xnySym'])
    return totalRewards

def mine_clover():
    rands = {
        'rotSym': rand(),
        'y0Sym': rand(),
        'x0Sym': rand(),
        'xySym': rand(),
        'xnySym': rand()
    }
    
    clover = {}

    clover['rotSym'] = 1 if (rands['rotSym'] < rarity['rotSym']) else 0
    clover['y0Sym'] = 1 if rands['y0Sym'] < rarity['y0Sym'] else 0
    clover['x0Sym'] = 1 if rands['x0Sym'] < rarity['x0Sym'] else 0
    clover['xySym'] = 1 if rands['xySym'] < rarity['xySym'] else 0
    clover['xnySym'] = 1 if rands['xnySym'] < rarity['xnySym'] else 0
        
    clover['symms'] = (clover['rotSym'] + clover['y0Sym'] + clover['x0Sym'] + clover['xySym'] + clover['xnySym']) > 0

    return clover


def mine_clovers(num_clovers):
    rare_clovers = num_clovers*rarity['hasSymmetry']
    rare_clovers = (1 if rand() < (rare_clovers % math.floor(rare_clovers)) else 0) + math.floor(rare_clovers)
    
    #for i in range(1,rare_clovers-1):

    
    
    
    

    clover['rotSym'] = 1 if (rands['rotSym'] < rarity['rotSym']) else 0
    clover['y0Sym'] = 1 if rands['y0Sym'] < rarity['y0Sym'] else 0
    clover['x0Sym'] = 1 if rands['x0Sym'] < rarity['x0Sym'] else 0
    clover['xySym'] = 1 if rands['xySym'] < rarity['xySym'] else 0
    clover['xnySym'] = 1 if rands['xnySym'] < rarity['xnySym'] else 0
        
    clover['symms'] = (clover['rotSym'] + clover['y0Sym'] + clover['x0Sym'] + clover['xySym'] + clover['xnySym']) > 0

    return clover


def player_policy(params, step, sL, s):
    # mine the clover
    clover = mine_clover()
    # calculate potential rewards for clover
    rewardAmount = getReward(s, clover)
    
    claim = getClaim(s)
    payAmount = (rewardAmount + market_settings['base-price']) * market_settings['priceMultiplier']

    # if the cost to buy is larger than the total user based supply (non-bank owned) there is no possible user
    # with enough club token to buy it
    if payAmount > s['bc-totalSupply']:
        claim = False
    if claim:
        totalSupply = s['bc-totalSupply'] - payAmount
    else:
        totalSupply = s['bc-totalSupply'] + rewardAmount
        
    return ({
        'rands': rands,
        'rewards': rewards,
        'rewardAmount': rewardAmount,
        'payAmount': payAmount,
        'claim': claim
    })

    

def miner_policy(params, step, sL, s):
    hash_rate = 15 # clovers per second
    
    miner_pool = 3 # number of miners
    
    miner_pct_online = 0.3
    
    clovers_hashed = (hash_rate*60*60)*miner_pool*miner_pct_online
    
    clover = mine_clover()
    
    
from numpy.random import rand
from config import rarity, market_settings
from utils import createCombinationRarities

combination_rarities = createCombinationRarities(rarity)

combination_rarities


def getClaim(s):
    return rand() < rarity['claimRate']

def getReward(s, rewards):
    if not rewards['symms']:
        return 0
    totalRewards = 0
    allSymmetries = s['rotSym'] + s['y0Sym'] + s['x0Sym'] + s['xySym'] + s['xnySym']
    if rewards['rotSym']:
        totalRewards = market_settings['payMultiplier'] * (1 + allSymmetries) / 2
    if rewards['y0Sym']:
        totalRewards = market_settings['payMultiplier'] * (1 + allSymmetries) / 2
    if rewards['x0Sym']:
        totalRewards = market_settings['payMultiplier'] * (1 + allSymmetries) / 2
    if rewards['xySym']:
        totalRewards = market_settings['payMultiplier'] * (1 + allSymmetries) / 2
    if rewards['xnySym']:
        totalRewards = market_settings['payMultiplier'] * (1 + allSymmetries) / 2
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
    possibleSyms = ['rotSym', 'y0Sym', 'x0Sym', 'xySym', 'xnySym']

    rare_clovers = num_clovers*rarity['hasSymmetry']
    rare_clovers = (1 if rand() < (rare_clovers % math.floor(rare_clovers)) else 0) + math.floor(rare_clovers)
    
    clovers = []
    for i in range(1,rare_clovers-1):
        
        clover = {}

        symmetry = utils.getSymmetry(rarity['symmetries'])
    
        for sym in possibleSyms:
            clover[sym] = False
    
        if possibleSyms.contains(symmetry):
            clover[symmetry] = True
        else:
            if sym == 'diagRotSym':
                clovers['xySym'] = clovers['xnySym'] = clovers['rotSym'] = True
            if sym == 'perpRotSym':
                clovers['x0Sym'] = clovers['y0Sym'] = clovers['rotSym'] = True
            if sym == 'allSym':
                for sym in possibleSyms:
                    clover[sym] = True
        
        clover['symms'] = True
        
        clovers[i] = clover
    
    return clovers


def player_policy(params, step, sL, s):
    # mine the clover
    rare_clovers = mine_clovers(1)
    # calculate potential rewards for clover
    # CHANGE THIS FROM HERE ==== mine_clovers returns an array of rare clovers, not a single non-rare or rare clover
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
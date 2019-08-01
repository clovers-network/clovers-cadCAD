# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# List of all the state variables in the system and their initial values
from scipy.stats import norm
import random

def market_buying_propensity():
    return random.uniform(0, 0.8) # probability to buy clovers from market (given they meet the value threshold)

def desired_for_sale_ratio():
    return random.uniform(0.5, 0.9) # percentage of owned clovers to list

def miner_hashrate():
    return norm.rvs(loc=30, scale=5) #150/sec with standard deviation of 50

market_settings = {
    'bc-reserveRatio': .33333,  # bonding curve reserve ratio (connector weight)
    'bc-virtualBalance': 33,  # bonding curve virtual balance
    'bc-virtualSupply': 100000,   # bonding curve virtual supply  
    'priceMultiplier': 10,   # used to calculate cost to keep (multiplied by reward amt + base price)
    'base-price': 1,         # minimum price to keep any clover
    'payMultiplier': 0.327,    # used to calculate reward (multiplied by ratio of rarity)
    'initialSpend': 32,       # initial spend in ETH
    'stdDev': 3,               # standard deviation of subjective price to objective price
    'initial_players': 20,
    'initial_miners': 1,
    'register_clover_cost_in_eth': 0.001313,
    'add_to_market_cost_in_eth': 0.00054,
    'buy_from_market_cost_in_eth': 0.002805,
    'sell_coins_cost_in_eth': 0.001012,
    'buy_coins_cost_in_eth': 0.001015,
    'miner_cash_out_threshold': 0.01,
    'hourly_attention_rate_for_buying_clovers': 25,
    'miner_pct_online': 1, # miner is online 100% of the time
    'miner_hashrate': miner_hashrate,
    'pct_miner_is_active': 0.99, # when online, what pct are they actively mining
    'pct_player_is_active': 0.7, # when online, what pct are they actively mining
    'desired_for_sale_ratio': desired_for_sale_ratio,
    'market_buying_propensity': market_buying_propensity,
    'pretty_multiplier': 1, # this number multiplied by some random float between 0 & 1
    'old_clover_interval': 50, # if the clover is older than 50 timesteps it is considered old
    'old_clover_fresh_factor': 0.5, # reduces the value by 50%
    'med_clover_interval': 5, # if the clover is newer than 5 timesteps it is medium fresh
    'med_clover_fresh_factor': 1.05, # increases the value by 5%
    'new_clover_interval': 1, # if the clover is newer than 1 timestep it is fresh
    'new_clover_fresh_factor': 1.1, # increases the value by 10%
    'increase_participants_every_x_steps': 24,
    'player_multiplier': 0.1,
    'miner_multiplier': 0.1,
}

disaster_ideal = {
    "s": {
        "previous-timesteps": 0, 
        "bc-balance": 0.004895516583783437,
        "bc-totalSupply": 23251.366969915605,
        "symmetries": {
            "hasSymmetry": 19651,
            "rotSym": 3940,
            "y0Sym": 3940,
            "x0Sym": 3940,
            "xySym": 3940,
            "xnySym": 3940
        },
        'clovers': [],
        'players': [],
        'miners': [],
        'bank': None,
        'network': None
    }
}

initial_conditions = {
    's': {
        'previous-timesteps': 0,
        'bc-balance': 0,         # bonding curve collateral balance (ETH)
        'bc-totalSupply': 0,     # clubToken totalSupply
        'symmetries': {
            'hasSymmetry': 1130,               # total number of symmetrical clovers
            'rotSym': 39 + 4 + 4 + 13,         # total rotational symmetries
            'y0Sym': 113 + 4 + 4,              # total y = 0 symmetries
            'x0Sym': 112 + 4 + 4,              # total x = 0 symmetries
            'xySym': 394 + 13 + 4,             # total x = y symmetries
            'xnySym': 450 + 13 + 4,            # total x = -y symmetries
        },
        'numBankClovers': 0,
        'numPlayerClovers': 0,
        'timestepStats': {
            'cloversKept': 0,
            'cloversReleased': 0,
            'cloversTraded': 0,
            'cloversBoughtFromBank': 0,
            'cloversListedByPlayers': 0,
        },
        'clovers': [],
        'players': [],
        'miners': [],
        'bank': None,
        'network': None
    }
}

def hasSymmetry(cloverCount):
    base = 0.0001
#     if (cloverCount > 1000):
#         base = 0.00001
#     if (cloverCount > 10000):
#         base = 0.000001
    return base

rarity = {
    'hasSymmetry': hasSymmetry, #0.0001, # 1/10000 clovers are symmetrical, derived from 
    'claimRate':   0.01,
    'pretty':      0.01, # 1/100 clovers are "pretty"
    'rarePretty':  0.3, # 30/100 rare clovers are "pretty"k
    'symmetries': {
        'rotSym':      39/1130,
        'x0Sym':       112/1130,
        'y0Sym':       113/1130,
        'xySym':       394/1130,
        'xnySym':      450/1130,
        'diagRotSym':  13/1130,
        'perpRotSym':  4/1130,
        'allSym':      4/1130
        # DATA FOR CALCULATING RARITIES:
        # total symms: 1130
        # total rot: 61 - 4 - 14 - 4 = 39
        # total x0Sym: 120 - 4 - 4 = 112
        # total y0Sym: 121 - 4 - 4 = 113
        # total xySym: 412 - 14 - 4 = 394
        # total xnySym: 468 - 14 - 4 = 450
        # total diagRotSym: 18 - 4 = 14
        # total perpRotSym: 8 - 4 = 4
        # total allSym: 4
    }
}
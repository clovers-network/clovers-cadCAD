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

gasPrice = 5 #Gwei

market_settings = {
    'initialSpend': 0,       # initial spend in ETH
    'stdDev': 3,               # standard deviation of subjective price to objective price
    'initial_players': 400,
    'initial_miners': 10,
    'gasPrice': gasPrice, #Gwei
    'register_clover_cost_in_eth': (0.000286774 + 0.000521) * gasPrice, # cost multiplied average gas cost
    'add_to_market_cost_in_eth': 0.000102 * gasPrice,
    'buy_from_market_cost_in_eth': 0.000277 * gasPrice,
    'sell_coins_cost_in_eth': 0.000099 * gasPrice,
    'buy_coins_cost_in_eth': 0.000091 * gasPrice,
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
    'player_multiplier': 0.01,
    'miner_multiplier': 0.01,
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
        'bc-balance': 43.43114,         # bonding curve collateral balance (ETH)
        'bc-totalSupply': 34219,     # cloverCoin totalSupply
        'symmetries': {
            'hasSymmetry': 22665,               # total number of symmetrical clovers
            'rotSym': 4591,         # total rotational symmetries
            'y0Sym': 4823,              # total y = 0 symmetries
            'x0Sym': 4931,              # total x = 0 symmetries
            'xySym': 6313,             # total x = y symmetries
            'xnySym': 6417,            # total x = -y symmetries
        },
        'numBankClovers': 17179,
        'numPlayerClovers': 17040,
        'initial-playerCloversForSale': 2885,
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
    base = 0.0002
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
        'rotSym':      72/2705,
        'x0Sym':       223/2705,
        'y0Sym':       221/2705,
        'xySym':       1009/2705,
        'xnySym':      1154/2705,
        'diagRotSym':  21/2705,
        'perpRotSym':  5/2705,
        'allSym':      4/2705
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

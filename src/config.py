# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# List of all the state variables in the system and their initial values

market_settings = {
    'bc-reserveRatio': .33333,  # bonding curve reserve ratio (connector weight)
    'bc-virtualBalance': 33,  # bonding curve virtual balance
    'bc-virtualSupply': 100000,   # bonding curve virtual supply  
    'priceMultiplier': 10,   # used to calculate cost to keep (multiplied by reward amt + base price)
    'base-price': 1,         # minimum price to keep any clover
    'payMultiplier': 0.1,    # used to calculate reward (multiplied by ratio of rarity)
    'initialSpend': 40,       # initial spend in ETH
    'stdDev': 2,               # standard deviation of subjective price to objective price
    'number_of_players': 66,
    'number_of_miners': 34,
    'gas_cost_in_eth': 0.001313,
    'add_to_market_cost_in_eth': 0.00054,
    'buy_from_market_cost_in_eth': 0.002805,
}

initial_conditions = {
    'bc-balance': 0,         # bonding curve collateral balance (ETH)
    'bc-totalSupply': 0,     # clubToken totalSupply
    'symmetries': {
        'hasSymmetry': 0,        # total number of symmetrical clovers
        'rotSym': 0,             # total rotational symmetries
        'y0Sym': 0,              # total y = 0 symmetries
        'x0Sym': 0,              # total x = 0 symmetries
        'xySym': 0,              # total x = y symmetries
        'xnySym': 0,             # total x = -y symmetries
    }
}

rarity = {
    'hasSymmetry': 0.0001, # 1/10000 clovers are symmetrical, derived from 
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
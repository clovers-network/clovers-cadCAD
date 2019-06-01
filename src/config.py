# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# List of all the state variables in the system and their initial values

market_settings = {
    'bc-reserveRatio': .33333,  # bonding curve reserve ratio (connector weight)
    'bc-virtualBalance': 33,  # bonding curve virtual balance
    'bc-virtualSupply': 100000,   # bonding curve virtual supply  
    'priceMultiplier': 10,   # used to calculate cost to keep (multiplied by reward amt + base price)
    'base-price': 1,         # minimum price to keep any clover
    'payMultiplier': 0.1,    # used to calculate reward (multiplied by ratio of rarity)
    'initialSpend': 40       # initial spend in ETH
}

initial_conditions = {
    'bc-balance': 0,         # bonding curve collateral balance (ETH)
    'bc-totalSupply': 0,     # clubToken totalSupply
    'bankClovers': 0,        # total clovers owned by Bank
    'clovers': 0,            # total number of clovers
    'symms': 0,              # total number of symmetrical clovers
    'rotSym': 0,             # total rotational symmetries
    'y0Sym': 0,              # total y = 0 symmetries
    'x0Sym': 0,              # total x = 0 symmetries
    'xySym': 0,              # total x = y symmetries
    'xnySym': 0,             # total x = -y symmetries
}

rarity = {
    'hasSymmetry': 0.0001, # 1/10000 clovers are symmetrical, derived from 
    'claimRate':   0.01,
    'pretty':      0.01, # 1/100 clovers are "pretty"
    'symmetries': {
        'rotSym':      0.03834510595358224,
        'x0Sym':       0.1099899091826438,
        'xySym':       0.3834510595358224,
        'xnySym':      0.44601412714429867,
        'diagRotSym':  0.014127144298688193,
        'perpRotSym':  0.004036326942482341,
        'allSym':      0.004036326942482341
    }
}
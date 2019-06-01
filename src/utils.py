from itertools import *
import numpy

def initialize(market_settings, conditions):
    
    def init_ts(s):
        return calculatePurchaseReturn(market_settings["bc-virtualSupply"], market_settings["bc-virtualBalance"], market_settings["bc-reserveRatio"], market_settings["initialSpend"])
    
    conditions['bc-balance'] = market_settings["initialSpend"]
    conditions['bc-totalSupply'] = init_ts(conditions)
    
    return conditions


def calculatePurchaseReturn(tokenSupply, collateral, CW, amount):
    return tokenSupply * ((1 + amount / collateral)**CW-1)

def calculateSellReturn(tokenSupply, collateral, CW, amount):
    return collateral * ((1 + tokensSold / totalSupply)**(1/CW)-1)

def calculateCurrentPrice(tokenSupply, collateral, CW):
    return collateral / (tokenSupply * CW)


def getSymmetry(symmetryRarities):
    rand_val = rand()
    
    for i in range(1,len(symmetryRarities)+1):
        if rand_val <= numpy.sum(list(symmetryRarities.values())[0:i]):
            break;
    
    return list(syms.keys())[i-1]

#def interpretCombinations(combinationTuple):
#    switcher = {
#        ('rotSym',): ('rotSym',),
#        ('x0Sym',): ('x0Sym',),
#        ('y0Sym',): ('y0Sym',),
#        ('xySym',): ('xySym',),
#        ('xnySym',): ('xnySym',),
#        ('rotSym', 'x0Sym'): ('rotSym', 'x0Sym'),
#        ('rotSym', 'y0Sym'): ('rotSym', 'x0Sym', 'y0Sym'),
#        ('rotSym', 'xySym'): ('rotSym', 'xySym', 'xnySym'),
#        ('rotSym', 'xnySym'): ('rotSym', 'xySym', 'xnySym'),
#        ('x0Sym', 'y0Sym'):  ('rotSym', 'x0Sym', 'y0Sym'),
#        ('x0Sym', 'xySym'): ('rotSym', 'x0Sym', 'y0Sym'), # diag or perp
#        ('x0Sym', 'xnySym'): ('rotSym', 'xySym', 'xnySym'), # diag or perp
#        ('y0Sym', 'xySym'): ('rotSym', 'x0Sym', 'y0Sym'), # diag or perp
#        ('y0Sym', 'xnySym'): ('rotSym', 'xySym', 'xnySym'), # diag or perp
#        ('xySym', 'xnySym'): ('rotSym', 'xySym', 'xnySym'),
#        ('rotSym', 'x0Sym', 'y0Sym'): ('rotSym', 'x0Sym', 'y0Sym'),
#        ('rotSym', 'x0Sym', 'xySym'): ('rotSym', 'xySym', 'xnySym'), # diag or perp
#        ('rotSym', 'x0Sym', 'xnySym'): ('rotSym', 'x0Sym', 'y0Sym'), # diag or perp
#        ('rotSym', 'y0Sym', 'xySym'): ('rotSym', 'xySym', 'xnySym'), # diag or perp
#        ('rotSym', 'y0Sym', 'xnySym'): ('rotSym', 'x0Sym', 'y0Sym'), # diag or perp
#        ('rotSym', 'xySym', 'xnySym'): ('rotSym', 'xySym', 'xnySym'),
#        ('x0Sym', 'y0Sym', 'xySym'): ('rotSym', 'x0Sym', 'y0Sym'),
#        ('x0Sym', 'y0Sym', 'xnySym'): ('rotSym', 'x0Sym', 'y0Sym'),
#        ('x0Sym', 'xySym', 'xnySym'): ('rotSym', 'xySym', 'xnySym'),
#        ('y0Sym', 'xySym', 'xnySym'): ('rotSym', 'xySym', 'xnySym'),
#        ('rotSym', 'x0Sym', 'y0Sym', 'xySym'): ('rotSym', 'x0Sym', 'y0Sym'),
#        ('rotSym', 'x0Sym', 'y0Sym', 'xnySym'): ('rotSym', 'x0Sym', 'y0Sym'),
#        ('rotSym', 'x0Sym', 'xySym', 'xnySym'): ('rotSym', 'xySym', 'xnySym'),
#        ('rotSym', 'y0Sym', 'xySym', 'xnySym'): ('rotSym', 'xySym', 'xnySym'),
#        ('x0Sym', 'y0Sym', 'xySym', 'xnySym'): ('rotSym', 'x0Sym', 'y0Sym', 'xySym', 'xnySym'),
#        ('rotSym', 'x0Sym', 'y0Sym', 'xySym', 'xnySym'): ('rotSym', 'x0Sym', 'y0Sym', 'xySym', 'xnySym')
#    }
#    return switcher.get(combinationTuple, "Invalid Sym Combinatoin")
#
#def createCombinationRarities(rarity):    
#    combinationRarities = {}
#    symCombinations = []
#    possibleSyms = ['rotSym', 'x0Sym', 'y0Sym', 'xySym', 'xnySym']
#    
#    for numSymsFound in range(1,6):
#        for symCombination in combinations(possibleSyms, numSymsFound):
#    
#            # array for probabilities of a symmetry's
#            # presence for multiplying probabilities later
#            probabilities = []
#            
#            # add in the probabilities of these symmetries being present
#            for symPresent in symCombination:
#                probabilities.append(rarity[symPresent])
#            
#            # add in the probabilities of the non-present symmetries not being present
#            for symNotPresent in (set(possibleSyms) - set(symCombination)):
#                probabilities.append(1-rarity[symNotPresent])
#                
#            # multiply all the probabilities, to get a total probability for this symCombination
#            combinationRarities[symCombination] = numpy.product(probabilities)
#        
#    #probOfRare = numpy.sum(list(combinationRarities.values()))
#    #
#    #for k,v in combinationRarities.items():
#    #    combinationRarities[k] = v
#    
#    return combinationRarities
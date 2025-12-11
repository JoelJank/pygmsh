import math
import utils.meshcalc as meshcalc

def createlists(numlayers, firstlayerheight, growthrate): #TODO: when switching to multiple fences: we need to use relatives. Always calculate relative height from fencespacing/2
    elist = [1]*numlayers
    hlist = [firstlayerheight * growthrate**i for i in range(numlayers)]

    totalheight = sum(hlist)
    normalizedhlist = [h/totalheight for h in hlist]

    cumulative_hlist = []
    cumulative = 0
    for h in normalizedhlist:
        cumulative += h
        cumulative_hlist.append(cumulative)
    return elist, cumulative_hlist, totalheight

def extrude_calc(xgrowthrate, meshXFreesize, firstlayerheight, fencespacing = None): #TODO: if the overall height is bigger than fenceSpacing/2 reduce by one layer (drop last entry in list later)
    numlayersbetweenfences = math.ceil(meshcalc.layercalculations(fencespacing/2, xgrowthrate, firstlayerheight)[0])
    numlayersafterfence = math.ceil(meshcalc.inflationlayernumber(firstlayerheight, xgrowthrate, meshXFreesize))

    elistbetweenfences, hlistbetweenfences,_ = createlists(numlayersbetweenfences, firstlayerheight, xgrowthrate)
    elistafterfence, hlistafterfence, totalheightafter = createlists(numlayersafterfence, firstlayerheight, xgrowthrate)

    return [elistbetweenfences, hlistbetweenfences], [elistafterfence, hlistafterfence], totalheightafter

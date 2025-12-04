import numpy as np
import math
from utils.meshcalc import layercalcuations, totalheightcalculation



def infcalc_spline(h1, growthrate, nLayers, hChannel, growthafterinflation, partsheight):
    nparts = len(partsheight)
    meshdata = np.empty((nparts+1,2), dtype = object)
    nFirstlayer, nextlayer, lastlayer = layercalcuations(partsheight[0], growthrate, h1)
    if h1 > partsheight[0]:
        for i in range(0, nparts):
            meshdata[i] = [1, partsheight[i]]
    else:
        meshdata[0] = [math.ceil(nFirstlayer), lastlayer]
        for i in range(1, nparts):
            if nextlayer > partsheight[i]:
                nextlayer = partsheight[i]
                meshdata[i] = [1, nextlayer]
                lastlayer = nextlayer
            else:
                nlayer, nextlayer, lastlayer = layercalcuations(partsheight[i], growthrate, lastlayer)
                meshdata[i] = [math.ceil(nlayer), lastlayer]
    sumLayers = np.sum(meshdata[:-1,0])
    remaininglayer = nLayers - sumLayers
    if remaininglayer > 0:
        heightlastlayer = totalheightcalculation(nextlayer, growthrate, remaininglayer)
        nlayer, nextlayer, lastlayer = layercalcuations(heightlastlayer, growthrate, nextlayer)
        toppoints = heightlastlayer + sum(partsheight)
        meshdata[-1] = [remaininglayer, lastlayer]
    else:
        toppoints =sum(partsheight)+meshdata[-2][1]
        meshdata[-1] = [1, lastlayer]
        
    nbisoben, nextlayeroben, lastlayeroben = layercalcuations(hChannel-toppoints, growthafterinflation, lastlayer)
    return meshdata, toppoints, [math.ceil(nbisoben), lastlayeroben]
        

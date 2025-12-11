import numpy as np
import math

def inflationlayernumber(h1, growthrate, targetheight):
    nlayer = math.log(targetheight/h1)/math.log(growthrate)
    return nlayer


def layercalculations(hparts, growthrate, h1):
    nlayer = math.log(1-(hparts*(1-growthrate)/h1))/math.log(growthrate)
    nextlayer = h1 * growthrate**nlayer
    lastlayer = h1 * growthrate**(nlayer-1)
    return nlayer, nextlayer, lastlayer

def totalheightcalculation(h1, growthrate, nlayers):
    totalheight = h1* (1- growthrate**nlayers) / (1 - growthrate)
    return totalheight


def inflationcalculation(h1, growthrate, nlayers, hFence, nparts, hChannel, growthaferinflation):
    heightparts = hFence /nparts
    meshdata = np.empty((nparts+1,2), dtype = object)
    totalheight = totalheightcalculation(h1, growthrate, nlayers)
    nFirstlayer, nextlayer, lastlayer = layercalculations(heightparts, growthrate, h1)
    if h1 > heightparts: #wenn h1 direkt größer als Zaunhöhe ist
        for i in range(0,nparts):
            meshdata[i] = [1, heightparts*(1+i)]
    else: #sonst normale berechnung
        meshdata[0] = [math.ceil(nFirstlayer), lastlayer]
        for i in range(1,nparts):
            if nextlayer > heightparts:
                nextlayer = heightparts
                meshdata[i] = [1, nextlayer]
                lastlayer = nextlayer
            else:
                nlayer, nextlayer, lastlayer = layercalculations(heightparts, growthrate, nextlayer)
                meshdata[i] = [math.ceil(nlayer), lastlayer]
                
    sumlayers = np.sum(meshdata[:-1,0]) #auffüllen der restlichen Layer
    remaininglayer = nlayers - sumlayers
    if remaininglayer > 0:
        heightlastlayer = totalheightcalculation(nextlayer, growthrate, remaininglayer)
        nlayer, nextlayer, lastlayer = layercalculations(heightlastlayer, growthrate, nextlayer)
        toppoints = heightlastlayer + hFence
        meshdata[-1] = [remaininglayer, lastlayer]
    else:
        toppoints = nparts*heightparts + meshdata[-2][1]
        meshdata[-1] = [1, lastlayer]
        
    #für inflation bis nach oben
    nbisoben, nextlayeroben, lastlayeroben = layercalculations(hChannel-toppoints, growthaferinflation, lastlayer)
    return meshdata, toppoints, [math.ceil(nbisoben), lastlayeroben]
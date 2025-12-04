import numpy as np
import math



def layercalcuations(hparts, growthrate, h1):
    nlayer = math.log(1-(hparts*(1-growthrate)/h1))/math.log(growthrate)
    nextlayer = h1 * growthrate**nlayer
    lastlayer = h1 * growthrate**(nlayer-1)
    return nlayer, nextlayer, lastlayer

def totalheightcalculation(h1, growthrate, nlayers):
    totalheight = h1* (1- growthrate**nlayers) / (1 - growthrate)
    return totalheight


def inflationcalculation(
    h1,
    growthrate,
    nlayers,
    hFence,
    nparts,
    hChannel,
    growthaferinflation,
    section_heights=None,
):
    if section_heights is None:
        section_heights = [hFence / nparts] * nparts
    else:
        section_heights = list(section_heights)
        if len(section_heights) != nparts:
            raise ValueError("section_heights muss genau nparts Einträge besitzen.")
        if not math.isclose(sum(section_heights), hFence, rel_tol=1e-9, abs_tol=1e-12):
            raise ValueError("Summe von section_heights muss hFence ergeben.")

    meshdata = np.empty((nparts + 1, 2), dtype=object)
    totalheight = totalheightcalculation(h1, growthrate, nlayers)

    nFirstlayer, nextlayer, lastlayer = layercalcuations(section_heights[0], growthrate, h1)
    if h1 > section_heights[0]:
        meshdata[0] = [1, section_heights[0]]
    else:
        meshdata[0] = [math.ceil(nFirstlayer), lastlayer]

    for i in range(1, nparts):
        current_height = section_heights[i]
        if nextlayer > current_height:
            nextlayer = current_height
            meshdata[i] = [1, current_height]
            lastlayer = current_height
        else:
            nlayer, nextlayer, lastlayer = layercalcuations(current_height, growthrate, nextlayer)
            meshdata[i] = [math.ceil(nlayer), lastlayer]

    sumlayers = np.sum(meshdata[:-1, 0])
    remaininglayer = nlayers - sumlayers
    if remaininglayer > 0:
        heightlastlayer = totalheightcalculation(nextlayer, growthrate, remaininglayer)
        _, nextlayer, lastlayer = layercalcuations(heightlastlayer, growthrate, nextlayer)
        toppoints = heightlastlayer + hFence
        meshdata[-1] = [remaininglayer, lastlayer]
    else:
        toppoints = sum(section_heights) + meshdata[-2][1]
        meshdata[-1] = [1, lastlayer]

    nbisoben, _, lastlayeroben = layercalcuations(
        hChannel - toppoints, growthaferinflation, lastlayer
    )
    return meshdata, toppoints, [math.ceil(nbisoben), lastlayeroben]
def search_spline(splineList, number):
    index_found = None
    for i, wert in enumerate(splineList):
        if wert == number:
            index_found = i
            break
    return index_found
import math
import os


def read_height_file(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.split()
            if len(parts) == 3:  
                data.append([float(parts[0]), float(parts[1]), float(parts[2])])
    return data

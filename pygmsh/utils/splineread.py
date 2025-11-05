import math
import os


def read_height_file(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            # Zeilen splitten und die Werte als Tupel in die Liste einfügen
            parts = line.split()
            if len(parts) == 3:  # Sicherstellen, dass es genau zwei Werte gibt
                data.append([float(parts[0]), float(parts[1]), float(parts[2])])
    return data

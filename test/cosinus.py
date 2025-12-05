import math
def generate_data():
    data = []
    for i in range(0, 200):  # Angenommen bis 200, du kannst anpassen
        if i < 50 or i > 150:
            val = 0.0
        else:
            # Cosinus-Hub von 0 bei 50 auf 1 bei 100 auf 0 bei 150
            val = 0.5 - 0.5 * math.cos(2 * math.pi * (i - 50) / 100)
        data.append([i, val, 0.0])
    return data

# Daten generieren und ausgeben
data = generate_data()
for row in data:
    print(f"{row[0]} {row[1]:.6f} {row[2]}")
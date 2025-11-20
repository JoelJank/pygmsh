import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#small = 3m width, medium = 5m width, large = 7.6m width
horizontal_red = pd.read_csv("H:\AG Parteli\pygmsh\Meeting 30.10\liucompare\liutetal/velvsxpos_red.csv", header = None, sep = "\t", names = ["x","y"])
horizontal_blue = pd.read_csv("H:\AG Parteli\pygmsh\Meeting 30.10\liucompare\liutetal/velvsxpos_blue.csv", header = None, sep = "\t", names = ["x","y"])
vertical_red = pd.read_csv("H:\AG Parteli\pygmsh\Meeting 30.10\liucompare\liutetal\yposvsvel_red.csv", header = None, sep = "\t", names = ["x","y"])
vertical_blue = pd.read_csv("H:\AG Parteli\pygmsh\Meeting 30.10\liucompare\liutetal\yposvsvel_blue.csv", header = None, sep = "\t", names = ["x","y"])
small_hor_red = pd.read_csv("H:\AG Parteli\pygmsh\Meeting 30.10\liucompare\liutetal/3dliu/3m_hor_red", header = None, sep = "\t", skiprows = 4,skipfooter =1,names = ["x","y"])
small_hor_blue = pd.read_csv("H:\AG Parteli\pygmsh\Meeting 30.10\liucompare\liutetal/3dliu/3m_hor_blue", header = None, sep = "\t", skiprows = 4,skipfooter =1,names = ["x","y"])
small_ver_red = pd.read_csv("H:\AG Parteli\pygmsh\Meeting 30.10\liucompare\liutetal/3dliu/3m_ver_red", header = None, sep = "\t", skiprows = 4,skipfooter =1,names = ["x","y"])
small_ver_blue = pd.read_csv("H:\AG Parteli\pygmsh\Meeting 30.10\liucompare\liutetal/3dliu/3m_ver_blue", header = None, sep = "\t", skiprows = 4,skipfooter =1,names = ["x","y"])
medium_hor_red = pd.read_csv("H:\AG Parteli\pygmsh\Meeting 30.10\liucompare\liutetal/3dliu/5m_hor_red", header = None, sep = "\t", skiprows = 4,skipfooter =1,names = ["x","y"])
medium_hor_blue = pd.read_csv("H:\AG Parteli\pygmsh\Meeting 30.10\liucompare\liutetal/3dliu/5m_hor_blue", header = None, sep = "\t", skiprows = 4,skipfooter =1,names = ["x","y"])
medium_ver_red = pd.read_csv("H:\AG Parteli\pygmsh\Meeting 30.10\liucompare\liutetal/3dliu/5m_ver_red", header = None, sep = "\t", skiprows = 4,skipfooter =1,names = ["x","y"])
medium_ver_blue = pd.read_csv("H:\AG Parteli\pygmsh\Meeting 30.10\liucompare\liutetal/3dliu/5m_ver_blue", header = None, sep = "\t", skiprows = 4,skipfooter =1,names = ["x","y"])
large_hor_red = pd.read_csv("H:\AG Parteli\pygmsh\Meeting 30.10\liucompare\liutetal/3dliu/76m_hor_red", header = None, sep = "\t", skiprows = 4,skipfooter =1,names = ["x","y"])
large_hor_blue = pd.read_csv("H:\AG Parteli\pygmsh\Meeting 30.10\liucompare\liutetal/3dliu/76m_hor_blue", header = None, sep = "\t", skiprows = 4,skipfooter =1,names = ["x","y"])
large_ver_red = pd.read_csv("H:\AG Parteli\pygmsh\Meeting 30.10\liucompare\liutetal/3dliu/76m_ver_red", header = None, sep = "\t", skiprows = 4,skipfooter =1,names = ["x","y"])
large_ver_blue = pd.read_csv("H:\AG Parteli\pygmsh\Meeting 30.10\liucompare\liutetal/3dliu/76m_ver_blue", header = None, sep = "\t", skiprows = 4,skipfooter =1,names = ["x","y"])
norm = 13.8
fig, ax = plt.subplots(1,2, figsize = (12,6))
ax1 = ax[0]
ax2 = ax[1]
#Original Liu et al. data
ax1.plot(horizontal_red["x"], horizontal_red["y"], linestyle = "None", color = "tab:red", marker = "o")
ax1.plot(horizontal_blue["x"], horizontal_blue["y"], linestyle = "None", color = "tab:blue", marker = "D")
ax2.plot(vertical_red["x"], vertical_red["y"], linestyle = "None", color = "tab:red", marker = "o")
ax2.plot(vertical_blue["x"], vertical_blue["y"], linestyle = "None", color = "tab:blue", marker = "D")


ax1.plot((medium_hor_blue["x"]-100)/1.2, (medium_hor_blue["y"])/norm, linestyle = ":", color = "tab:blue", label = "5m width, z/h = 0.38")
ax1.plot((medium_hor_red["x"]-100)/1.2, (medium_hor_red["y"])/norm, linestyle = ":", color = "tab:red", label = "5m width, z/h = 1.88")
ax2.plot((medium_ver_blue["x"]/norm), medium_ver_blue["y"]/1.2, linestyle = ":", color = "tab:blue", label = "5m width, x/h = 4.2")
ax2.plot((medium_ver_red["x"]/norm), medium_ver_red["y"]/1.2, linestyle = ":", color = "tab:red", label = "5m width, z/h = 75")

ax1.plot((large_hor_blue["x"]-100)/1.2, (large_hor_blue["y"])/norm, linestyle = "-", color = "tab:blue", label = "7.6m width, z/h = 0.38")
ax1.plot((large_hor_red["x"]-100)/1.2, (large_hor_red["y"])/norm, linestyle = "-", color = "tab:red", label = "7.6m width, z/h = 1.88")
ax2.plot((large_ver_blue["x"]/norm), large_ver_blue["y"]/1.2, linestyle = "-", color = "tab:blue", label = "7.6m width , x/h = 4.2")
ax2.plot((large_ver_red["x"]/norm), large_ver_red["y"]/1.2, linestyle = "-", color = "tab:red", label = "7.6m width , x/h = 75")

ax1.set_xlabel("x position (m)")
ax1.set_ylabel("normalized velocity")
ax2.set_xlabel("normalized velocity")
ax2.set_ylabel("y position (m)")
ax1.legend()
ax2.legend()
fig.suptitle("Comparison with velocity profiles from Liu et al. (2021), Channel height = 10m, Log inlets with u* = 0.5m/s,\n height fence = 1.2m, width variation, y+=45")

plt.savefig("compare_3d.svg" ,dpi = 300)

# pygmsh
TODO DRINGEND!!!!: HERAUFINDEN WARUM BEI BESTIMMTEN ZAUNHÖHE DAS MESH NICHT MEHR KLAPPT -> vielleicht mal andere Breite probieren?
This small git project is subjected to a specific application of the gmsh api to use it in the simulation of an atmospheric boundary layer with a present obstacle such as an sand fence. 

The necessary steps are:
1. implementing an structured mesh over the whole domain
2. further adding a inflation layer at the lower boundary to resolve the boundary layer around the ground

Espacially when the domain is complicated, for example when the fence has multiple parts that needs to be meshed individualy, this can get really messy in calculating the right growing factors for the boundary layer.

This program tackles that problem and should be a first step into the direction of coupling CFD simulation with models that predict the sand flux based on the results of the CFD simulations, which then provide feedbacks and make changes to the CFD domain. In this case, an efficient and reliable way to mesh the multiple geometries is necessary.

Firstly, this program is designed to be used in 2D cases. However, it is further adapted to also use it in 3D cases


To-do: 
Add coherence Mesh for 2D as well as 3D
Refactoring
Figure out the -1 or -2 Problem
Find way to write the settings files back to keep track of the Parameters that were used to create the mesh

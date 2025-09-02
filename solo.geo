// Gmsh project created on Tue Sep  2 15:28:05 2025
SetFactory("OpenCASCADE");
//+
Point(1) = {-0, 0, 0, 1.0};
//+
Point(2) = {10, 0, 0, 1.0};
//+
Point(3) = {10, 5, 0, 1.0};
//+
Point(4) = {0, 5, 0, 1.0};
//+
Point(5) = {5, 0, 0, 1.0};
//+
Point(6) = {5, 1, 0, 1.0};
//+
Point(7) = {5, 2, 0, 1.0};
//+
Line(1) = {1, 5};
//+
Line(2) = {5, 2};
//+
Line(3) = {2, 3};
//+
Line(5) = {4, 1};
//+
Line(6) = {5, 6};
//+
Line(7) = {6, 7};
//+
Point(8) = {5, 5, 0, 1.0};
//+
Line(8) = {7, 8};

//+
Line(9) = {3, 8};
//+
Line(10) = {8, 4};
//+
Curve Loop(1) = {8, 10, 5, 1, 6, 7};
//+
Plane Surface(1) = {1};
//+
Curve Loop(2) = {8, -9, -3, -2, 6, 7};
//+
Plane Surface(2) = {2};
//+
Transfinite Curve {10, 1, 2, 9} = 10 Using Progression 1;
//+
Transfinite Surface {2} = {8, 5, 2, 3};
//+
Transfinite Surface {1} = {8, 4, 1, 5};
//+
Recombine Surface {1, 2};

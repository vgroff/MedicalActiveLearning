#ifndef GRIDCUT3D
#define GRIDCUT3D

#include <vector>
#include "GridGraph_3D_26C.h"

typedef GridGraph_3D_26C<double, double, float>* Grid3D;
std::vector< std::vector< std::vector< double > > > gridCut3D(std::vector< std::vector< std::vector < double > > > image, 
							      std::vector< std::vector< std::vector< std::vector< double > > > > regTerms, double edgeCoeff, double sigma);

#endif

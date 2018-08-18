%module gridCut3D
%{
#include "gridCut3D.h"
%}
%include "std_vector.i"

namespace std {
	%template(Line)  vector < double >;
	%template(Array) vector < vector < double > >;
	%template(Volume) vector < vector < vector < double > > >;
	%template(CatVolume) vector < vector < vector < vector < double > > > >;
}   


std::vector< std::vector< std::vector < double > > > gridCut3D(std::vector< std::vector< std::vector < double > > > image, std::vector< std::vector< std::vector< std::vector< double > > > > regTerms, double edgeCoeff, double sigma);



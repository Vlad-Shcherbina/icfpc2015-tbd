%module placement

%include "typemaps.i"
%include "std_vector.i"

%template(IntVector) std::vector<int>;
%template(IntVectorVector) std::vector<std::vector<int> >;

%{
#include "placement.h"
%}

%include "placement.h"

%module placement

%include "typemaps.i"
%include "std_vector.i"

%template(IntVector) std::vector<int>;

%{
#include "placement.h"
%}

%include "placement.h"

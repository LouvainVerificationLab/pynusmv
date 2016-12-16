%module(package="pynusmv.nusmv.sat") sat

%include ../global.i

%{
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/sat/sat.h" 

#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/sat/SatSolver.h" 
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/sat/SatIncSolver.h" 
%}

%feature("autodoc", 1);

%include ../typedefs.tpl

/**
 * WARNING : 
 * The following typemaps serve the purpose of letting swig know how to map/unmap
 * SatSolverGroup's. Indeed, SatSolverGroup is typedef'ed as a numsmv_ptrint 
 * which is itself typedef'ed to util_ptrint which is defined nowhere. Because
 * of this, swig does not know how to free a pointer of any of those types and
 * issues a runtime warning. 
 * 
 * Thus, the following typemaps tell swig what to do when it encounters such a
 * pointer.  
 */
/* conversion from python to swig */
%typemap(in) SatSolverGroup {
	$1 = (SatSolverGroup) PyInt_AsLong($input);
}
/* conversion from swig to python */
%typemap(out) SatSolverGroup {
	$result = PyInt_FromLong((long) $1);
}
/******************************************************************************/

%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/sat/sat.h

%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/sat/SatSolver.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/sat/SatIncSolver.h


%inline %{

SatSolver_ptr SatIncSolver_cast_to_SatSolver_ptr(SatIncSolver_ptr ptr){
  return (SatSolver_ptr) ptr;
}

%}
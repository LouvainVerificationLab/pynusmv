%module(package="pynusmv.nusmv.hrc") hrc

%include ../global.i

%{
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/hrc/hrc.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/hrc/hrcCmd.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/hrc/HrcFlattener.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/hrc/HrcNode.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/hrc/hrcPrefixUtils.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/hrc/HrcVarDependencies.h"
%}

// Removing possible memory leak warning.
// Global variables must be cautiously used.
#pragma SWIG nowarn=454

// Ignoring unimplemented functions
%ignore HrcPopulateSymbTable;

%feature("autodoc", 1);

%include ../typedefs.tpl

%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/hrc/hrc.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/hrc/hrcCmd.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/hrc/HrcFlattener.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/hrc/HrcNode.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/hrc/hrcPrefixUtils.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/hrc/HrcVarDependencies.h

%inline %{

/* XGILLARD: 2016-12-02: fix compilation error */
/* HrcNode_ptr mainHrcNode; */

%}

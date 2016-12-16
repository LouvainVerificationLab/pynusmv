%module(package="pynusmv.nusmv.hrc.dumpers") dumpers

%include ../../global.i

%{
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/hrc/dumpers/HrcDumper.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/hrc/dumpers/HrcDumperDebug.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/hrc/dumpers/HrcDumperSmv.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/hrc/dumpers/HrcDumperXml.h" 
%}

// Removing possible memory leak warning.
// Global variables have to be cautiously used.
#pragma SWIG nowarn=451

%feature("autodoc", 1);

%include ../../typedefs.tpl

%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/hrc/dumpers/HrcDumper.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/hrc/dumpers/HrcDumperDebug.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/hrc/dumpers/HrcDumperSmv.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/hrc/dumpers/HrcDumperXml.h
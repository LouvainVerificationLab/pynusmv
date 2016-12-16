%module(package="pynusmv.nusmv.trace.loaders") loaders

%include ../../global.i

%{
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/loaders/TraceLoader.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/loaders/TraceXmlLoader.h" 
%}

%feature("autodoc", 1);

%include ../../typedefs.tpl

%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/loaders/TraceLoader.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/loaders/TraceXmlLoader.h
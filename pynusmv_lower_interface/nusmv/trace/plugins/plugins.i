%module(package="pynusmv.nusmv.trace.plugins") plugins

%include ../../global.i

%{
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/plugins/TraceCompact.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/plugins/TraceExplainer.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/plugins/TracePlugin.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/plugins/TraceTable.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/plugins/TraceXmlDumper.h" 
%}

%feature("autodoc", 1);

%include ../../typedefs.tpl

%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/plugins/TraceCompact.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/plugins/TraceExplainer.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/plugins/TracePlugin.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/plugins/TraceTable.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/plugins/TraceXmlDumper.h
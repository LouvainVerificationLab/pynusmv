%module(package="pynusmv.nusmv.node.printers") printers

%include ../../global.i

%{
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/printers/MasterPrinter.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/printers/PrinterBase.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/printers/PrinterIWffCore.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/printers/PrinterPsl.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/printers/PrinterSexpCore.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/printers/PrinterWffCore.h" 
%}

// Ignoring unimplemented functions
%ignore MasterPrinter_reset_string_stream;

%feature("autodoc", 1);

%include ../../typedefs.tpl

%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/printers/MasterPrinter.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/printers/PrinterBase.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/printers/PrinterIWffCore.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/printers/PrinterPsl.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/printers/PrinterSexpCore.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/printers/PrinterWffCore.h
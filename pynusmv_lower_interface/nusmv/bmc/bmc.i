%module(package="pynusmv.nusmv.bmc") bmc

%include ../global.i

%{
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmc.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcBmc.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcCheck.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcCmd.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcConv.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcDump.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcGen.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcModel.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcPkg.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcSimulate.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcTableau.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcUtils.h"
%}

%feature("autodoc", 1);

%include ../typedefs.tpl

%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmc.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcBmc.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcCheck.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcCmd.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcConv.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcDump.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcGen.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcModel.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcPkg.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcSimulate.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcTableau.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/bmcUtils.h

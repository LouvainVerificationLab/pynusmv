%module(package="pynusmv.nusmv.bmc.sbmc") sbmc

%include ../../global.i

%{
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcBmc.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcBmcInc.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcCmd.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcGen.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcHash.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcNodeStack.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcPkg.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcStructs.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcTableau.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcTableauInc.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcTableauIncLTLformula.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcTableauLTLformula.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcUtils.h" 
%}

// Ignoring unimplemented function
%ignore sbmc_unroll_invariant_propositional;

%feature("autodoc", 1);

%include ../../typedefs.tpl

%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcBmc.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcBmcInc.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcCmd.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcGen.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcHash.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcNodeStack.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcPkg.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcStructs.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcTableau.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcTableauInc.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcTableauIncLTLformula.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcTableauLTLformula.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/bmc/sbmc/sbmcUtils.h
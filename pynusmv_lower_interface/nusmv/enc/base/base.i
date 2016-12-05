%module(package="pynusmv.nusmv.enc.base") base

%include ../../global.i

%{
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/enc/base/BaseEnc.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/enc/base/BoolEncClient.h" 
%}

%feature("autodoc", 1);

%include ../../typedefs.tpl

%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/enc/base/BaseEnc.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/enc/base/BoolEncClient.h
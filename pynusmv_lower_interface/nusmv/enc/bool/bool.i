%module(package="pynusmv.nusmv.enc.bool") "bool"

%include ../../global.i

%{
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/enc/bool/BitValues.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/enc/bool/BoolEnc.h" 
%}

%feature("autodoc", 1);

%include ../../typedefs.tpl

%inline %{
BaseEnc_ptr boolenc2baseenc(BoolEnc_ptr bool_enc) {
    return (BaseEnc_ptr) bool_enc;
}
%}

%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/enc/bool/BitValues.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/enc/bool/BoolEnc.h
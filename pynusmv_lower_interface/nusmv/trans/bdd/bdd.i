%module(package="pynusmv.nusmv.trans.bdd") bdd

%include ../../global.i

%{
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trans/bdd/bdd.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trans/bdd/BddTrans.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trans/bdd/Cluster.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trans/bdd/ClusterList.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trans/bdd/ClusterOptions.h" 

#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h"
%}

%feature("autodoc", 1);

%include ../../typedefs.tpl

%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trans/bdd/bdd.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trans/bdd/BddTrans.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trans/bdd/Cluster.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trans/bdd/ClusterList.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trans/bdd/ClusterOptions.h


%inline %{

BddTrans_ptr BddTrans_copy(const BddTrans_ptr trans) {
    return BDD_TRANS(Object_copy(OBJECT(trans)));
}

void BddTrans_free(BddTrans_ptr trans) {
    Object_destroy(OBJECT(trans), NULL);
}

%}
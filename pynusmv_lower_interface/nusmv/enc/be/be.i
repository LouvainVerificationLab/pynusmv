%module(package="pynusmv.nusmv.enc.be") be

%include ../../global.i

%{
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/enc/be/BeEnc_private.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/enc/be/BeEnc.h" 
%}

%feature("autodoc", 1);

%include ../../typedefs.tpl

%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/enc/be/BeEnc.h

%inline %{
	BaseEnc_ptr BeEnc_ptr_to_BaseEnc_ptr(BeEnc_ptr _enc) {
	    return (BaseEnc_ptr) _enc;
	}
	
	BoolEncClient_ptr BeEnc_ptr_to_BoolEncClient_ptr(BeEnc_ptr _enc) {
	    return (BoolEncClient_ptr) _enc;
	}
	
	BoolEnc_ptr BeEnc_ptr_get_bool_enc(BeEnc_ptr _enc) {
		return ((BoolEncClient_ptr) _enc)->bool_enc;
	}
	
	be_ptr substitute_in_formula(BeEnc_ptr be_enc, be_ptr formula, PyObject* subst_lst){
		/*************** STEP1: Convert the list to int* *********************/
		be_ptr result;
		int i       = 0;
		ssize_t len = PyList_Size(subst_lst);
		// declare a null terminated int array (the nusmv way)
		int* subst = (int*) malloc((len+1)*sizeof(int));
		// raise exception if out of mem !
		if(subst == NULL){
			return PyErr_NoMemory();
		}
		// copy over the list information
		for(i = 0; i<len; i++){
			PyObject* item = PyList_GetItem(subst_lst, i);
			subst[i]       = (int) PyLong_AsLong(item);
		}
		// terminate the list
		subst[len] = (int) NULL;
		
		/******************* STEP2: Call the real api ************************/
		result = Be_LogicalVarSubst(be_enc->be_mgr, 
									formula, 
									subst, 
									be_enc->log2phy, 
									be_enc->phy2log);
		
		/******************* STEP3: Cleanup and return ************************/
		// make sure to cleanup any allocated mem.
		free(subst);
		// return
		return result;
	}
%}
%module(package="pynusmv.nusmv.utils") utils

%include ../global.i

/**
 * This typemap provides the automatic conversion from null terminated list of int stored
 * in an int* to a python list of ints. (null terminated int* is the NuSMV convention).
 */
%typemap(out) int* {
  int* ptr = $1;
  PyObject* ret = PyList_New((Py_ssize_t) 0);

  while(*ptr!=NULL){
    PyList_Append(ret, PyInt_FromLong((long)*ptr));
    ptr++;
  }

  $result = ret;
}

%{
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/utils.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/array.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/assoc.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/avl.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/error.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/heap.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/list.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/NodeGraph.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/NodeList.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/Olist.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/Pair.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/portability.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/range.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/Slist.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/Sset.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/Stack.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/TimerBench.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/Triple.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/ucmd.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/ustring.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/utils_io.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/WordNumber.h"

/* sbusard 11/06/12 - Ignoring lsort.h due to errors in file parsing. */
/*#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/lsort.h"*/
%}

// Ignoring unimplemented functions
%ignore Siter_set_element;
%ignore Utils_get_temp_filename;
%ignore Utils_strtoint;
%ignore error_id_appears_twice_in_idlist_file;
%ignore error_not_word_sizeof;
%ignore util_str2int_inc;

%feature("autodoc", 1);

%include ../typedefs.tpl

%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/utils.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/array.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/assoc.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/avl.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/error.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/heap.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/list.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/NodeGraph.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/NodeList.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/Olist.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/Pair.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/portability.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/range.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/Slist.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/Sset.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/Stack.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/TimerBench.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/Triple.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/ucmd.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/ustring.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/utils_io.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/WordNumber.h

// sbusard 11/06/12 - Ignoring lsort.h due to errors in file parsing.
#%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/lsort.h

%inline %{

array_t* array_alloc_strings(int number) {
    return array_alloc(const char*, number);
}

#include <stdio.h>
void array_insert_strings(array_t* array, int i, const char* datum) {
    datum = util_strsav(datum);
    array_insert(const char*, array, i, datum);
}

const char* array_fetch_strings(array_t* array, int i) {
    return (const char*) array_fetch(const char*, array, i);
}

/**** files ****/

FILE* stdio_fopen(const char* fname, const char* mode){
    return fopen(fname, mode);
}

FILE* stdio_stdin(){
    return stdin;
}
FILE* stdio_stdout(){
    return stdout;
}
FILE* stdio_stderr(){
    return stderr;
}

int stdio_fclose(FILE* f){
    return fclose(f);
}

/* pointer types conversions */
int void_star_to_int(void* p){
    return (int) p;
}
void* int_to_void_star(int i){
    return (void*) i;
}
int* void_star_to_int_star(void* p){
    return (int*) p;
}

void* slist_to_void_star(Slist_ptr l){
    return (void*) l;
}
Slist_ptr void_star_to_slist(void* p){
    return (Slist_ptr) p;
}

void* str_to_void_star(char* text){
  return (void*) text;
}

char* void_star_to_str(void* ptr){
  return (char*) ptr;
}

%}

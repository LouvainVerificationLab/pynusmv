/* ********** COPYRIGHT DISCLAIMER ***************************************
 * This file is part of PyNuSMV + bmc.
 *
 * PyNuSMV + bmc is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * PyNuSMV + bmc is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with PyNuSMV + bmc.  If not, see <http://www.gnu.org/licenses/>.
 *************************************************************************/

/* ********** FILE DOCUMENTATION *****************************************
 * This file contains the SWIG interface for the lower interface of the
 * (custom) BMC module containing code initially written in Python and
 * then translated in C for performance reason: profiling revealed that
 * these function were real performance bottlenecks of the PyNuSMV BMC
 * addition.
 *
 * The binary is built with the regular Makefile of PyNuSMV.
 * If you need to alter this part of the lower interface and dont want to
 * rebuild the COMPLETE library, you may just use the following commands:
 *
 *  cd $PYNUSMV_HOME/src
 *  make bmc_lower
 *  ./build_libnusmv.sh
 *
 *************************************************************************/
%module(package="pynusmv.bmc.lower_intf") lower_intf

%{
#include "../../../nusmv/nusmv-config.h"
#include "../../../nusmv/src/utils/defs.h"
#include "lower_intf.h"
%}

%feature("autodoc", 1);

%include ../../nusmv/typedefs.tpl

%include ../../../nusmv/src/utils/defs.h
%include lower_intf.h

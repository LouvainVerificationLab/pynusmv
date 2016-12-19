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
 *************************************************************************/
%module bmc_utils

%{
#include "../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "bmc_utils.h"
%}

%feature("autodoc", 1);

%include ../nusmv/typedefs.tpl

%include ../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include bmc_utils.h

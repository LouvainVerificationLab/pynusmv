################################################################################
# This make file serves the purpose of compiling and nusmv for your platform
# and link it with minisat.
#
# This file is part of the pynusmv distribution. As such it is licensed to you
# under the term of the LGPLv2. For more information regarding the legal aspect
# of this licensing, please refer to the full text of the license on the free
# software foundation website.
#
# Author: X. Gillard <xavier.gillard [at] uclouvain.be>
################################################################################

# The path to the (unpacked) source folder of NuSMV
NUSMV=./NuSMV-2.5.4/nusmv/

# The path to the patched and compiled version of minisat
MINISAT=../../../MiniSat/minisat
ZCHAFF=../../../ZChaff/zchaff64

RECONFIGURE := $(shell python3 ./reconfiguration_needed.py --test)

ifeq ($(WITH_ZCHAFF), 1)
	solvers_config= --enable-minisat \
									--with-minisat-libdir=$(MINISAT) \
									--with-minisat-incdir=$(MINISAT) \
									--enable-zchaff \
									--with-zchaff-libdir=$(ZCHAFF) \
									--with-zchaff-incdir=$(ZCHAFF)
else
	solvers_config= --enable-minisat \
									--with-minisat-libdir=$(MINISAT) \
									--with-minisat-incdir=$(MINISAT) 
endif

# This target goes through all the steps required to compile NuSMV.
all: nusmv.built

# This target wipes off everything that has been unpacked and built.
clean:
	rm -rf NuSMV-2.5.4
	rm last_config.pickle
	rm nusmv.unpacked
	rm nusmv.patched
	rm nusmv.configured
	rm nusmv.built

# This target just unpacks the archive containing nusmv
nusmv.unpacked:
	tar -xpf NuSMV-2.5.4.tar.gz
	touch nusmv.unpacked

nusmv.patched: nusmv.unpacked
	patch -p0 -N < pynusmv.patch
	patch -p0 -N < cudd.patch
	touch nusmv.patched

# This target configures nusmv for proper compilation on your system
nusmv.configured: nusmv.patched
ifeq ($(RECONFIGURE), yes)
	# Note: because we didn't build the (nusmv-patched) version of CUDD explicitly
	#       the configuration script will schedule a compilation of that library
	#       before proceeding to the rest of the compilation.
	cd $(NUSMV) && ./configure  $(solvers_config) \
															--with-pic \
															CFLAGS="-g -fPIC" \
														  CXXFLAGS="-g -fPIC"

	python3 ./reconfiguration_needed.py --save
endif

# This target proceeds to the build (proper) of the nusmv codebase
#
# Note: because we didn't build the (nusmv-patched) version of CUDD explicitly
#       the configuration script scheduled a compilation of that library
#       before proceeding to the rest of the compilation.
nusmv.built: nusmv.configured
	make -C $(NUSMV)
	touch nusmv.built

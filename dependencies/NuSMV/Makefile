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

# This target goes through all the steps required to compile NuSMV.
all: nusmv.build

# This target wipes off everything that has been unpacked and built.
clean:
	rm -rf NuSMV-2.5.4
	rm nusmv.unpack
	rm nusmv.configure
	rm nusmv.build

# This target just unpacks the archive containing nusmv
nusmv.unpack:
	tar -xpf NuSMV-2.5.4.tar.gz
	touch nusmv.unpack

nusmv.patch: nusmv.unpack
	patch -p0 -N < pynusmv.patch
	touch nusmv.patch

# This target configures nusmv for proper compilation on your system
nusmv.configure: nusmv.patch
	# Note: because we didn't build the (nusmv-patched) version of CUDD explicitly
	#       the configuration script will schedule a compilation of that library
	#       before proceeding to the rest of the compilation.
	cd $(NUSMV) && ./configure  --enable-minisat \
	                            --with-minisat-libdir=$(MINISAT) \
							                --with-minisat-incdir=$(MINISAT) \
															--with-pic \
															--enable-static \
															--enable-static-link \
															CFLAGS="-g -O2 -fPIC" \
														  CXXFLAGS="-g -O2 -fPIC"
	touch nusmv.configure

# This target proceeds to the build (proper) of the nusmv codebase
#
# Note: because we didn't build the (nusmv-patched) version of CUDD explicitly
#       the configuration script scheduled a compilation of that library
#       before proceeding to the rest of the compilation.
nusmv.build: nusmv.configure
	make -C $(NUSMV)
	touch nusmv.build

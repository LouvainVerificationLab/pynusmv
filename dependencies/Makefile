################################################################################
# This make file serves the purpose of triggering the compilation of the native
# (C, C++) dependencies of pynusmv for your platform.
#
# This file is part of the pynusmv distribution. As such it is licensed to you
# under the term of the LGPLv2. For more information regarding the legal aspect
# of this licensing, please refer to the full text of the license on the free
# software foundation website.
#
# Author: X. Gillard <xavier.gillard [at] uclouvain.be>
################################################################################

# This target builds the libnusmv shared library which is used by the lower
# interface of pynusmv
all: minisat.build nusmv.build

# This target wipes off anything that has been unpacked or compiled
clean: minisat.clean nusmv.clean

# This target checks that all the tools and libraries which are required in order
# to build pynusmv and its dependencies are installed on the target system.
# In case of failure, it displays an explanatory message.
system.requirement:
	python3 system_requirements.py
	touch system.requirement

# Builds the minisat binaries which are required to compile nusmv
minisat.build: system.requirement
	make -C MiniSat

# Wipes off anything related to minisat
minisat.clean:
	make -C MiniSat clean

# Builds the nusmv binaries which are required to generate the libnusmv
nusmv.build: system.requirement minisat.build
	make -C NuSMV

# Wipes off anything related to nusmv
nusmv.clean:
	make -C NuSMV clean

################################################################################
# This make file serves the purpose of compiling and patching minisat for your
# platform.
#
# This file is part of the pynusmv distribution. As such it is licensed to you
# under the term of the LGPLv2. For more information regarding the legal aspect
# of this licensing, please refer to the full text of the license on the free
# software foundation website.
#
# Author: X. Gillard <xavier.gillard [at] uclouvain.be>
################################################################################

# This target goes through all the steps required to compile MiniSat.
all: minisat.build

# This target wipes off everything that has been unpacked and built.
clean:
	rm -rf minisat
	rm minisat.unpack
	rm minisat.patch

# This target just unpacks the zip containing minisat
minisat.unpack:
	unzip minisat2-070721.zip
	touch minisat.unpack

# This target successively applies the patches required to make minisat linkable
# with nusmv and to ensure its smooth compilation on all (tested) platforms.
minisat.patch: minisat.unpack
	# Patch nusmv to make it linkable with NuSMV
	patch -p0 -N < nusmv.patch
	# Patch nusmv so that it build smoothly on all (tested) platforms
	patch -p0 -N < pynusmv.patch
	touch minisat.patch

# This target proceeds to the build (proper) of the minisat codebase
minisat.build: minisat.patch
	make -C minisat

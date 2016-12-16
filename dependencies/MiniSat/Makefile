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
all: minisat.built

# This target wipes off everything that has been unpacked and built.
clean:
	rm -rf minisat
	rm minisat.unpacked
	rm minisat.patched

# This target just unpacks the zip containing minisat
minisat.unpacked:
	unzip minisat2-070721.zip
	touch minisat.unpacked

# This target successively applies the patches required to make minisat linkable
# with nusmv and to ensure its smooth compilation on all (tested) platforms.
minisat.patched: minisat.unpacked
	# Patch nusmv to make it linkable with NuSMV
	patch -p0 -N < nusmv.patch
	# Patch nusmv so that it build smoothly on all (tested) platforms
	patch -p0 -N < pynusmv.patch
	# Patch the makefiles to produce position independent code
	# This is necessary to create a sharedlib containing the minisat symbols
	patch -p0 -N < makefiles.patch
	touch minisat.patched

# This target proceeds to the build (proper) of the minisat codebase
minisat.built: minisat.patched
	make -C minisat

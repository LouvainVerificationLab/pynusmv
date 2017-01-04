################################################################################
# This make file serves the purpose of compiling and patching zchaff for your
# platform.
#
# This file is part of the pynusmv distribution. As such it is licensed to you
# under the term of the LGPLv2. For more information regarding the legal aspect
# of this licensing, please refer to the full text of the license on the free
# software foundation website.
#
# Author: X. Gillard <xavier.gillard [at] uclouvain.be>
################################################################################

# This target goes through all the steps required to compile ZChaff.
all: zchaff.built

# This target wipes off everything that has been unpacked and built.
clean:
	rm -rf zchaff.64bit.2007.3.12.zip
	rm -rf zchaff64
	rm zchaff.downloaded
	rm zchaff.patched

# This target just unpacks the zip containing zchaff
zchaff.downloaded:
	python3 ./download_zchaff.py
	touch zchaff.downloaded

# This target successively applies the patches required to make zchaff linkable
# with nusmv and to ensure its smooth compilation on all (tested) platforms.
zchaff.patched: zchaff.downloaded
	# Patch nusmv to make it linkable with NuSMV
	patch -p0 -N < nusmv.patch
	# Patch nusmv so that it build smoothly on all (tested) platforms
	# Basically, this patch only alters the makefile so as to produced position
	# independent code (-fPIC)
	patch -p0 -N < pynusmv.patch
	touch zchaff.patched

# This target proceeds to the build (proper) of the zchaff codebase
zchaff.built: zchaff.patched
	make -C zchaff64 libsat.a
	make -C zchaff64 SAT_C.h

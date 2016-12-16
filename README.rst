PyNuSMV
=======

PyNuSMV is a Python binding for NuSMV. It is intended to provide a
Python interface to NuSMV, allowing to use NuSMV as a library.

More details about this tool are provided in the PyNuSMV documentation
(see the DOCUMENTATION section below).

Preliminary warning
-------------------

PyNuSMV does NOT work with Python 2 !

Installation
------------

Give some instructions for the installation. Should revolve around a
plain

::

    pip3 install pynusmv

Build
-----

Building PyNuSMV requires you to have a few standard tools available on
your computer. Typically the build process should work nice and smooth
on all platform although only OSX and Ubuntu-Linux have actually been
tested.

Dependencies
~~~~~~~~~~~~

The first thing the build process performs in before even stating to try
building PyNuSMV is to check the availability of the following system
requirements. Unfortunately, no guarantee regarding the exhaustivity of
this list can be given although we have strong confidence that it is
sufficient.

-  An ANSI C compiler (gcc will do, as will several versions of cc)
-  A C++ compiler (g++ advised)
-  GNU Flex version 2.5 or greater
-  GNU Bison version 1.22 or greater
-  GNU make utility version 3.74 or greater
-  GNU tar, gzip and unzip (to unpack the sources of the dependencies)
-  GNU patch (to fix some files in the original project distributions)
-  GNU ar and ranlib to create static libraries
-  GNU ln command
-  SWIG version 2.0.6 or higher -- http://www.swig.org/
-  Python3 (version 3.2 or higher) -- http://python.org/
-  Setuptools 2.1 or higher -- https://pypi.python.org/pypi/setuptools
-  pyparsing version 2.0.2 or higher -- http://pyparsing.wikispaces.com/
-  Sphinx if you intend to re-build the project documentation.

Platform specific tools
^^^^^^^^^^^^^^^^^^^^^^^

On OS X, you will also need the ``install_name_tool`` command. But don't
worry much about this one, it should already be installed on your
system. Similarly, on Linux, you will need the ``patchelf`` command
which is used for the same purpose. This should however not be a big
problem since a package for patchelf exists for all major Linux
distributions.

Extra libraries
^^^^^^^^^^^^^^^

In addition to these, you will need to have ``libexpat`` installed on
your system (SWIG on OSX also requires ``pcre`` but this might not be
mandatory on all platforms moreover, you can simply your swig installed
with ``brew install swig`` and that should be enough).

Build process
~~~~~~~~~~~~~

To build and install your distribution of pynusmv from the sources, you
should proceed with the following command: ``python3 setup.py install``

This will start by unpacking, patching and building the following
dependencies:

- MiniSat
- CUDD
- NuSMV

Once that is done, the actual core of setup.py will be executed. This
involves building the dynamic libraries for the lower interface and
package the python modules that build above that lower interface. As
usual, depending on the command you pass to setuptools, the output will
be produced under ``build`` or ``dist``.

Verifying your build
~~~~~~~~~~~~~~~~~~~~

To check if the compilation was successful and make sure you didn't
break anything in the expected behavior of the lib, you can run the unit
tests as such: ``python3 setup.py test``

DOCUMENTATION
-------------

The full API of (the upper interface of) PyNuSMV can be generated thanks
to Sphinx (http://www.sphinx-doc.org/) by running the following command:
``python3 setup.py doc`` or ``python3 setup.py doc --builder=<builder>``

The resulting documentation will be produced in buid/doc/. Where
*builder* is the name of the builder you chose to generate the
documentation. By default, this builder is set to ``html`` which means
the documentation will be generated in html format.

The same documentation is also available on
http://pythonhosted.org/pynusmv/.

Content
-------

This package contains:

*README*
    This file

*dependencies*
    A directory containing the dependencies project necessary to pynusmv

*pynusmv*
    The package containig the whole upper interface of pynusmv

*pynusmv\_lower\_interface*
    The package containing the wole lower interface of pynusmv

*doc*
    A directory containing the files that permit the documentation generation.

*tests*
    The project unittests

*setup.py*
    PyNuSMV compilation file;

Note that pre-compiled versions have less content because only the
minimal required files (i.e. PyNuSMV files and nusmv shared library) are
included.

Legal
-----

PyNuSMV is licensed under the GNU Lesser General Public License (LGPL in
short). See https://www.gnu.org/licenses/lgpl-3.0.en.html for the full
details of the license.

Note
~~~~

Alongside with PyNuSMV, the following dependencies are brought to you
under the following license terms:

- NuSMV : LGPL (same license as PyNuSMV).
- CUDD: MIT license
- MiniSat: MIT license

Credits
-------

PyNuSMV is developed, maintained and distributed by the LVL Group at
Université Catholique de Louvain. Please contact for any question
regarding this software distribution.

NuSMV is a symbolic model checker developed as a joint project between
several partners and distributed under the GNU LGPL license. Please
contact for getting in touch with the NuSMV development staff.

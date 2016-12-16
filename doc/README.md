# Documentation
This folder contains the source code required to generate the documentation
properly. However, because pynusmv comprises the pynusmv_lower_interface which
relies on extensions which themselves depend on `libdependencies.so` which is
only available when the project was built; generating the documentation requires
the doc makefile to be executed from whithin the build directory where a
complete (executable) pynusmv installation exists. Therefore, the content of
this directory is *NOT used as is* but is instead copied to the build location
and then only is the makefile executed.

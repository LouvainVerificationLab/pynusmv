# Migration Script
This folder contains all the migration scripts that I have used to conform the
pynusmv source code from one state 0.0.11 to the newer state where it can be
packaged and distributed over PyPI.

For the recall, here are the purpose of the following scripts:
  - _batch_utils.py_ contains just a bunch of functions that are used in
    the definition of the other migration scripts.
  - _migrate_swintf.py_ migrates the reference to NuSMV and CUDD in the SWIG
    interface files.
  - _migrate_lowerintf.py_ migrates the reference to the pynusmv.nusmv package
    that used to contain the lower interface by a reference to the new package
    `lower_interface`.

## Note
The follwing files have been altered because they cause compilation issues
(symbol redefinition):
  - pynusmv_lower_interface/nusmv/node/node.i
  - pynusmv_lower_interface/nusmv/hrc/hrc.i

# About ZChaff
zChaff is a powerful SAT Solver [1]:http://www.princeton.edu/~chaff/zchaff.html
that can be optionally used with PyNuSMV to perform BMC.

For information about how to compile and link zChaff within NuSMV, and
for other important information about zChaff, please refer to the file
<NuSMV-(version)/zchaff/README> distributed along with the NuSMV
source code.

## Legal conflict
There is currently a legal conflict between pynusmv and ZChaff. Indeed, pynusmv
is licensed under the terms of LGPL while zchaff is not. As a matter of fact
anyone is allowed to do whatever he wants with pynusmv including use it to
develop commercial products but this turns out not to be allowed by zchaff
license. Hence we are not allowed to bundle pynusmv with the source code of
zchaff nor distribute binary versions of it that contain the compiled code of
the solver (this is not a bmc showstopper per-se since minisat is and can be
shipped with the rest of the codebase).

## zChaff License
````
    *****************************************************************
    *** zChaff is for non-commercial purposes only.               ***
    *** NO COMMERCIAL USE OF ZCHAFF IS ALLOWED WITHOUT WRITTEN    ***
    *** PERMISSION FROM PRINCETON UNIVERSITY.                     ***
    *** Please contact Sharad Malik (malik@ee.princeton.edu)      ***
    *** for details.                                              ***
    *****************************************************************

Copyright 2000-2004, Princeton University.  All rights reserved.
By using this software the USER indicates that he or she has read,
understood and will comply with the following:

--- Princeton University hereby grants USER nonexclusive permission
to use, copy and/or modify this software for internal, noncommercial,
research purposes only. Any distribution, including commercial sale
or license, of this software, copies of the software, its associated
documentation and/or modifications of either is strictly prohibited
without the prior consent of Princeton University.  Title to copyright
to this software and its associated documentation shall at all times
remain with Princeton University.  Appropriate copyright notice shall
be placed on all software copies, and a complete copy of this notice
shall be included in all copies of the associated documentation.
No right is  granted to use in advertising, publicity or otherwise
any trademark,  service mark, or the name of Princeton University.


--- This software and any associated documentation is provided "as is"

PRINCETON UNIVERSITY MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS
OR IMPLIED, INCLUDING THOSE OF MERCHANTABILITY OR FITNESS FOR A
PARTICULAR PURPOSE, OR THAT  USE OF THE SOFTWARE, MODIFICATIONS, OR
ASSOCIATED DOCUMENTATION WILL NOT INFRINGE ANY PATENTS, COPYRIGHTS,
TRADEMARKS OR OTHER INTELLECTUAL PROPERTY RIGHTS OF A THIRD PARTY.

Princeton University shall not be liable under any circumstances for
any direct, indirect, special, incidental, or consequential damages
with respect to any claim by USER or any third party on account of
or arising from the use, or inability to use, this software or its
associated documentation, even if Princeton University has been advised
of the possibility of those damages.
````

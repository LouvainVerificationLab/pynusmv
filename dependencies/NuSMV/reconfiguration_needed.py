'''
# This script helps to decide whether or not the underlying version of NuSMV
# should be rebuilt. In particular, it is used to decide whether or not you 
# have chosent to build and link ZCHAFF and recompile the dependencies according
# to your choice.
#
# .. note::
#
#   This test uses environment variables which is not as clean as it could or
#   should but it does the work and was easy to implement + that's the usual
#   way to deal with this kind of stuffs in makefiles
#
# This file is part of the pynusmv distribution. As such it is licensed to you
# under the term of the LGPLv2. For more information regarding the legal aspect
# of this licensing, please refer to the full text of the license on the free
# software foundation website.
#
# Author: X. Gillard <xavier.gillard [at] uclouvain.be>
'''
import os
import argparse
import pickle

def get_last_config():
    try:
        return pickle.load(open("./last_config.pickle", "rb"))
    except:
        return None
        
def get_current_config():
    return {
        'with-zchaff': os.environ["WITH_ZCHAFF"] if "WITH_ZCHAFF" in os.environ else "0"
    }
        
def do_save():
    pickle.dump(get_current_config(), open("./last_config.pickle", "wb"))
    
def do_test():
    return get_current_config() != get_last_config()
    
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test",      action="store_true", help="Print 'yes' iff nusmv needs a reconfiguration")
    parser.add_argument("--save",      action="store_true", help="Dumps the current configuration to file")
    parser.add_argument("--show-last", action="store_true", help="Prints the last configuration")
    parser.add_argument("--show-curr", action="store_true", help="Prints the current configuration")
    args   = parser.parse_args()
    
    if args.test : 
        print( "yes" if do_test() else "no" )
        
    if args.save : 
        do_save()
        
    if args.show_last:
        print(get_last_config())
        
    if args.show_curr:
        print(get_current_config())
    


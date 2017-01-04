'''
# This script is used to download the appropriate version of zchaff for you to
# build and link pynusmv.
#
# This file is part of the pynusmv distribution. As such it is licensed to you
# under the term of the LGPLv2. For more information regarding the legal aspect
# of this licensing, please refer to the full text of the license on the free
# software foundation website.
#
# Author: X. Gillard <xavier.gillard [at] uclouvain.be>
'''
import requests
import shutil

def download_file(url, fname):
    '''
    Downloads the file located at `url` and dumps it into a local file named
    `fname`.
    
    :param url: the url of the file to be downloaded
    :param fname: the name of the file to be saved locally
    '''
    response = requests.get(url, stream=True)
    
    with open(fname, "wb") as f:
      for chunk in response.iter_content(chunk_size=128):
        f.write(chunk)

if __name__ == "__main__":
    archive = "zchaff.64bit.2007.3.12.zip"
    url     = "http://www.princeton.edu/~chaff/zchaff/" + archive

    download_file(url, archive)
    shutil.unpack_archive(archive)

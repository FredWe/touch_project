import numpy as np
import logging
import kaldi_io
import sys
import argparse
import io_helper

def loaddata(scpdict, outtype='raw'):
    alldata = {}
    for uttid, recpath in scpdict.items():
        alldata[uttid] = io_helper.parsefile(recpath, outtype)
    return alldata

def main():
    logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.WARN)
    parser = argparse.ArgumentParser(
        description="load .rec rawfile from first argument SCPPATH, \
            and convert all rec to scpfile-contained-utterence-id-indexed ark file to ARKPATH")
    parser.add_argument("SCPPATH", help="scp file path")
    parser.add_argument("ARKPATH", help="ark file path")
    args = parser.parse_args()
    logging.debug(args)
    SCP_FILEPATH = args.SCPPATH
    ARK_FILEPATH = args.ARKPATH
    if not ARK_FILEPATH.endswith('.ark') or not SCP_FILEPATH.endswith('.scp'):
        logging.error('extension error')
        exit()
    logging.debug(SCP_FILEPATH)
    uttid2recpath = io_helper.loadscp(SCP_FILEPATH)
    logging.debug(uttid2recpath)
    dataset = loaddata(uttid2recpath, 'diff')
    with kaldi_io.open_or_fd(ARK_FILEPATH,'wb') as f:
        for k, m in dataset.items():
            kaldi_io.write_mat(f, m, k)

if __name__ == '__main__':
    main()


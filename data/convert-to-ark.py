import numpy as np
import logging
import kaldi_io
import sys
import argparse

NPAD = 15

def parsefile2raw(filepath):
    data = np.zeros((0, NPAD))
    #logging.debug(filepath)
    with open(filepath, 'r') as file_data:
        for line in file_data:
            rawbytes = [
                onebyte.zfill(2)
                for onebyte in line.strip().split()]
            #logging.debug(rawbytes)
            if not rawbytes: # remove empty line
                continue
            rawsigs = [
                int(rawbytes[idx * 4] + rawbytes[idx * 4 + 1], 16)
                for idx in range(NPAD)]
            #logging.debug(rawsigs)
            #logging.debug(np.array(rawsigs).shape)
            data = np.append(data, [rawsigs], axis=0)
    #logging.debug(data)
    #logging.debug(data.shape)
    return data

def loadata(scpdict):
    alldata = {}
    for uttid, recpath in scpdict.items():
        alldata[uttid] = parsefile2raw(recpath)
    return alldata

def loadscp(scppath):
    scpdict = {}
    with open(scppath, 'r') as scpcontent:
        for line in scpcontent:
            uttid, recpath = line.split()
            scpdict[uttid] = recpath
    return scpdict

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
    if not ARK_FILEPATH.endswith('.ark') or not ARK_FILEPATH.endswith('.ark'):
        logging.error('extension error')
        exit()
    logging.debug(SCP_FILEPATH)
    uttid2recpath = loadscp(SCP_FILEPATH)
    logging.debug(uttid2recpath)
    dataset = loadata(uttid2recpath)
    with kaldi_io.open_or_fd(ARK_FILEPATH,'wb') as f:
        for k, m in dataset.items():
            kaldi_io.write_mat(f, m, k)

if __name__ == '__main__':
    main()


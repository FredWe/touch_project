import numpy as np
import logging
import kaldi_io
import sys

NPAD = 15
ARKFILENAME = 'feats_train.ark'

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
    if len(sys.argv) < 2:
        logging.error('no scp filepath given')
    SCP_FILEPATH = sys.argv[1]
    logging.debug(SCP_FILEPATH)
    uttid2recpath = loadscp(SCP_FILEPATH)
    logging.debug(uttid2recpath)
    dataset = loadata(uttid2recpath)
    with kaldi_io.open_or_fd(ARKFILENAME,'wb') as f:
        for k, m in dataset.items():
            kaldi_io.write_mat(f, m, k)

if __name__ == '__main__':
    main()


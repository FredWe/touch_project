import logging
import kaldi_io
import numpy as np
import os

NPAD = 15
def parsefile_rec2raw(filepath):
    data = np.zeros((0, NPAD))
    logging.debug(filepath)
    with open(filepath, 'r') as file_data:
        for line in file_data:
            rawbytes = [
                onebyte.zfill(2)
                for onebyte in line.strip().split()]
            logging.debug(rawbytes)
            if not rawbytes: # remove empty line
                continue
            rawsigs = [
                int(rawbytes[idx * 4] + rawbytes[idx * 4 + 1], 16)
                for idx in range(NPAD)]
            logging.debug(rawsigs)
            logging.debug(np.array(rawsigs).shape)
            data = np.append(data, [rawsigs], axis=0)
    logging.debug(data)
    logging.debug(data.shape)
    return data

def parsefile(filepath, outtype='raw'):
    data = np.zeros((0, NPAD))
    logging.debug(filepath)
    with open(filepath, 'r') as file_data:
        for line in file_data:
            rawstrs = line.strip().split()
            raws, baselines, diffs, timers, sigs = [], [], [], [], []

            if len(rawstrs) == 63:

                rawbytes = [
                    onebyte.zfill(2)
                    for onebyte in rawstrs]
                logging.debug(rawbytes)
                logging.debug(len(rawbytes))
                raws = [
                        int(rawbytes[idx * 4] + rawbytes[idx * 4 + 1], 16)
                        for idx in range(NPAD)]
                baselines = [
                        int(rawbytes[idx * 4 + 2] + rawbytes[idx * 4 + 3], 16)
                        for idx in range(NPAD)]
                diffs = [
                        raws[idx] - baselines[idx]
                        for idx in range(NPAD)]
                timers = [rawbytes[NPAD * 4]]
            elif len(rawstrs) == 15:
                raws = [int(raw) for raw in rawstrs]
            else:
                continue

            if outtype == 'raw':
                sigs = raws
            elif outtype == 'diff':
                sigs = diffs
            elif outtype == 'baseline':
                sigs = baselines
            elif outtype == 'timer':
                sigs = timers
            data = np.append(data, [sigs], axis=0)
    #logging.debug(data)
    #logging.debug(data.shape)
    return data

def parsefile_ark2mat(filepath):
    return {
        k: m for k, m in
            kaldi_io.read_mat_ark(filepath)}

def outputfile_mat2ark(mat, filepath):
    logging.debug(filepath)
    if not filepath.endswith('.ark'):
        logging.error('extension error')
        return
    with kaldi_io.open_or_fd(filepath, 'wb') as f:
        for k, m in mat.items():
            if 0 in m.shape:
                continue
            kaldi_io.write_mat(f, m, k)

def parse_dictfile(filepath):
    import locale
    logging.debug(locale.getpreferredencoding())
    retdict = {}
    with open(filepath, 'r', encoding='utf-8') as filecontent:
        for line in filecontent:
            logging.debug(line)
            key, value = line.split()
            retdict[key] = value
    return retdict

def loadscp(scppath):
    return parse_dictfile(scppath)

def path2uttid(path):
    PRE1, PRE2 = '[', ']'
    parr = os.path.basename(path.replace(PRE1, '').replace(PRE2, '')).split('_')
    return '_'.join(parr[:len(parr) - 1])

import logging
import kaldi_io
import numpy as np

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
    #logging.debug(filepath)
    with open(filepath, 'r') as file_data:
        for line in file_data:
            rawbytes = [
                onebyte.zfill(2)
                for onebyte in line.strip().split()]
            #logging.debug(rawbytes)
            if not rawbytes: # remove empty line
                continue
            sigs = []
            if outtype == 'raw':
                sigs = [
                    int(rawbytes[idx * 4] + rawbytes[idx * 4 + 1], 16)
                    for idx in range(NPAD)]
            else:
                sigs = [
                    int(rawbytes[idx * 4] + rawbytes[idx * 4 + 1], 16) -
                    int(rawbytes[idx * 4 + 2] + rawbytes[idx * 4 + 3], 16)
                    for idx in range(NPAD)]
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
    with kaldi_io.open_or_fd(filepath,'wb') as f:
        for k, m in mat.items():
            kaldi_io.write_mat(f, m, k)
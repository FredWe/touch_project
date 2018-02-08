import numpy as np

def log_scale(matdict):
    loggedmat = {
        key: np.log2(np.clip(data, 1, None))
            for key, data in matdict.items()}
    return loggedmat

def percentile_scale(matdict, prcmin, prcmax):
    alldata = np.concatenate(list(matdict.values()), axis=0)
    datamin = np.percentile(alldata, prcmin, axis=0)
    datamax = np.percentile(alldata, prcmax, axis=0)
    ret = {
        key: np.clip(data, datamin, datamax)
            for key, data in matdict.items()}
    return ret

def normalize(matdict, log2=True):
    loggedmat = percentile_scale(log_scale(matdict), 1, 99)
    alldata = np.concatenate(list(loggedmat.values()), axis=0)
    sigmas = np.std(alldata, axis=0)
    mus = np.mean(alldata, axis=0)
    ret = {
        key: (data - mus) / sigmas
            for key, data in loggedmat.items()}
    return ret
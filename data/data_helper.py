import numpy as np
import scipy

apply2data = lambda matdict, func: {
        key: func(data)
            for key, data in matdict.items()}

def log_scale(matdict):
    func = lambda data: np.log2(np.clip(data, 1, None))
    return apply2data(matdict, func)

def percentile_scale(matdict, prcmin, prcmax):
    alldata = np.concatenate(list(matdict.values()), axis=0)
    datamin = np.percentile(alldata, prcmin, axis=0)
    datamax = np.percentile(alldata, prcmax, axis=0)
    func = lambda data: np.clip(data, datamin, datamax)
    return apply2data(matdict, func)

def normalize(matdict):
    alldata = np.concatenate(list(matdict.values()), axis=0)
    sigmas = np.std(alldata, axis=0)
    mus = np.mean(alldata, axis=0)
    func = lambda data: (data - mus) / sigmas
    return apply2data(matdict, func)

def minmax(matdict):
    alldata = np.concatenate(list(matdict.values()), axis=0)
    datamax = np.amax(alldata, axis=0)
    datamin = np.amin(alldata, axis=0)
    func = lambda data: (data - datamin) / (datamax - datamin)
    return apply2data(matdict, func)

def medfilt(matdict, filtlen):
    func = lambda data: scipy.signal.medfilt(data, (filtlen,1))
    return apply2data(matdict, func)
import numpy as np

def normalize(matdict, log2=True):
    loggedmat = {
        key: np.log2(np.clip(data, 1, None))
            for key, data in matdict.items()}
    alldata = np.concatenate(list(loggedmat.values()), axis=0)
    sigmas = np.std(alldata, axis=0)
    mus = np.mean(alldata, axis=0)
    ret = {
        key: (data - mus) / sigmas
            for key, data in loggedmat.items()}
    return ret
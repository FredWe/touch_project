import numpy as np
import scipy.signal
from sklearn.cluster import KMeans

# import plot_helper
# apply2data = lambda matdict, func: {
#         key: func(data)
#             for key, data in matdict.items()}
def apply2data(matdict, func):
    logfilename = 'notgood_keylist.log'
    ret = {}
    for key, data in matdict.items():
        try:
            ret[key] = func(data)
        except Exception as e:
            print(key + ' cannot find silence')
            print(key, file=open(logfilename, 'a'))
            ret[key] = data
    return ret
matdict2alldata = lambda matdict: np.concatenate(list(matdict.values()), axis=0)

def invert_dict(d):
    inv = {}
    for k, v in d.items():
        keys = inv.setdefault(v, [])
        keys.append(k)
    return inv

def log_scale(matdict):
    func = lambda data: np.log2(np.clip(data, 1, None))
    return apply2data(matdict, func)

def percentile_scale(matdict, prcmin, prcmax):
    alldata = matdict2alldata(matdict)
    datamin = np.percentile(alldata, prcmin, axis=0)
    datamax = np.percentile(alldata, prcmax, axis=0)
    func = lambda data: np.clip(data, datamin, datamax)
    return apply2data(matdict, func)

def normalize(matdict):
    alldata = matdict2alldata(matdict)
    sigmas = np.std(alldata, axis=0)
    mus = np.mean(alldata, axis=0)
    func = lambda data: (data - mus) / sigmas
    return apply2data(matdict, func)

def minmax(matdict):
    alldata = matdict2alldata(matdict)
    datamax = np.amax(alldata, axis=0)
    datamin = np.amin(alldata, axis=0)
    func = lambda data: (data - datamin) / (datamax - datamin)
    return apply2data(matdict, func)

def medfilt(matdict, filtlen):
    func = lambda data: scipy.signal.medfilt(data, (filtlen,1))
    return apply2data(matdict, func)

def stripcut(matdict, startlen, endlen):
    func = lambda data: data[startlen:data.shape[0] - endlen,:]
    return apply2data(matdict, func)

def drop_negative(matdict, threshold, placehold_value):
    func = lambda data: np.where(data > threshold, data, placehold_value)
    return apply2data(matdict, func)

def nonslide_silencecut(matdict, utt2word, start_preserved_length, end_preserved_length):
    word2utts = invert_dict(utt2word)
    def kmeanscut(data, kmeans):
        centers_norm = np.linalg.norm(kmeans.cluster_centers_, axis=1)
        nonsil_label = np.argmax(centers_norm)
        labels = kmeans.predict(data)
        nonsil_inds = np.arange(data.shape[0])[labels == nonsil_label]
        try:
            start = max(0, min(nonsil_inds) - start_preserved_length)
            end = min(data.shape[0], max(nonsil_inds) + end_preserved_length)
        except Exception as e:
            start = 0
            end = data.shape[0]
            raise
        return data[start:end,:]
    def name2partmatdict(name):
        # print(name)
        filtered_arkmat = {k: m for k, m in matdict.items() if k in word2utts[name]}
        alldata = matdict2alldata(filtered_arkmat)
        kmeans = KMeans(n_clusters=2, random_state=0).fit(alldata)
        ret = apply2data(filtered_arkmat, lambda data: kmeanscut(data, kmeans))
        return ret
    return {k: m for name in word2utts for k, m in name2partmatdict(name).items()}

def slide_silencecut(matdict, dist_threshold, start_preserved_length, end_preserved_length):
    def distcut(data, dist_threshold):
        norms = np.linalg.norm(data[:, :12], axis=1)
        nonsil_inds = np.arange(data.shape[0])[norms > dist_threshold]
        try:
            start = max(0, min(nonsil_inds) - start_preserved_length)
            end = min(data.shape[0], max(nonsil_inds) + end_preserved_length)
        except Exception as e:
            start = 0
            end = data.shape[0]
            raise
        return data[start:end,:]
    ret = apply2data(matdict, lambda data: distcut(data, dist_threshold))
    return ret

def silencecut(matdict, utt2word, dist_threshold, start_preserved_length, end_preserved_length):
    slide_utt2word, nonslide_utt2word = {}, {}
    slide_matdict, nonslide_matdict = {}, {}
    #split data/utt2word
    for utt, word in utt2word.items():
        if word.startswith('增') or word.startswith('减'):
            slide_utt2word[utt] = word
            slide_matdict[utt] = matdict[utt]
        else:
            nonslide_utt2word[utt] = word
            nonslide_matdict[utt] = matdict[utt]
    slide_matdict = slide_silencecut(slide_matdict, dist_threshold, start_preserved_length, end_preserved_length)
    nonslide_matdict = nonslide_silencecut(nonslide_matdict, nonslide_utt2word, start_preserved_length, end_preserved_length)
    ret = {**slide_matdict, **nonslide_matdict}
    return ret

def neo_silencecut(matdict, dist_threshold, start_preserved_length, end_preserved_length):
    def distcut(data, dist_threshold):
        maxv = np.max(data[:, :15], axis=1)
        nonsil_inds = np.arange(data.shape[0])[maxv > dist_threshold]
        try:
            start = max(0, min(nonsil_inds) - start_preserved_length)
            end = min(data.shape[0], max(nonsil_inds) + end_preserved_length)
        except Exception as e:
            start = 0
            end = data.shape[0]
            raise
        return data[start:end,:]
    ret = apply2data(matdict, lambda data: distcut(data, dist_threshold))
    return ret

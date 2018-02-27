import numpy as np
import scipy.signal
from sklearn.cluster import KMeans

apply2data = lambda matdict, func: {
        key: func(data)
            for key, data in matdict.items()}
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

def silencecut(matdict, worddict, start_preserved_length, end_preserved_length):
    def kmeanscut(data, kmeans):
        centers_norm = np.linalg.norm(kmeans.cluster_centers_, axis=1)
        nonsil_label = np.argmax(centers_norm)
        labels = kmeans.predict(data)
        nonsil_inds = np.arange(data.shape[0])[labels == nonsil_label]
        start = max(0, min(nonsil_inds) - start_preserved_length)
        end = min(data.shape[0], max(nonsil_inds) + end_preserved_length)
        return data[start:end,:]
    def name2partmatdict(name):
        filtered_arkmat = {k: m for k, m in matdict.items() if k in invdict[name]}
        alldata = matdict2alldata(filtered_arkmat)
        kmeans = KMeans(n_clusters=2, random_state=0).fit(alldata)
        return apply2data(filtered_arkmat, lambda data: kmeanscut(data, kmeans))
    invdict = invert_dict(worddict)
    return {k: m for k,m in name2partmatdict(name).items() for name in invdict}

    # for name in invdict:
    #     filtered_arkmat = {k: m for k, m in matdict.items() if k in invdict[name]}
    #     alldata = matdict2alldata(filtered_arkmat)
    #     kmeans = KMeans(n_clusters=2, random_state=0).fit(alldata)

    #     centers_norm = np.linalg.norm(kmeans.cluster_centers_, axis=1)
    #     nonsil_label_index = np.argmax(centers_norm)

    # for name in worddict.values():
    #     print(name)
    #     filtered_arkmat = {k: m for k, m in arkmat.items() if name in k}
    #     alldata = np.concatenate(list(filtered_arkmat.values()), axis=0)
    #     # kmeans_pca(alldata, name)
    #     K = 2
    #     kmeans = KMeans(n_clusters=K, random_state=0).fit(alldata)   
    #     uttid, data = filtered_arkmat.popitem()
    #     plot_kmeans(data, uttid, kmeans)

    # labels = kmeans.predict(data)
    # np.arange(data.shape[0])[labels == nonsil_label_index]

    # fig = plt.figure(figsize=(16, 12))
    # axes = fig.subplots(NPAD)#, sharey=True)
    # flg = False
    # centers_norm = np.linalg.norm(kmeans.cluster_centers_, axis=1)
    # sil_index = np.argmax(centers_norm)
    # labels = kmeans.predict(data)
    # for i in range(NPAD):
    #     ploted = data[:, i]
    #     axes[i].plot(ploted, '-+')
    #     axes[i].plot(np.arange(len(ploted))[labels == sil_index], ploted[labels == sil_index], 'r+')
    #     axes[i].set_ylabel(i)
    # plt.savefig('%s.png' % fname)
    # plt.close()
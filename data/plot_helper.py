import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np

NPAD = 15
SCANRES = 14
plt.rcParams['axes.formatter.useoffset'] = False

def plot_values(data, fname):
    n_channel = data.shape[1]
    fig = plt.figure(figsize=(16, 12))
    axes = fig.subplots(n_channel)#, sharey=True)
    for i in range(n_channel):
        axes[i].plot(data[:, i], '-+')
        axes[i].set_ylabel(i)
    plt.savefig('%s.png' % fname)
    plt.close()

def hist_values(data, log=False, bins=128):
    fig = plt.figure(figsize=(16, 12))
    axes = fig.subplots(NPAD, sharex=True)
    for i in range(NPAD):
        #fig = plt.figure()
        axes[i].hist(data[:, i], bins=bins, log=log)
        axes[i].set_ylabel(i)
    plt.show()#block=False)

def hist_normpdf(data):
    s = np.std(data, axis=0)
    m = np.mean(data, axis=0)
    fig = plt.figure(figsize=(16, 12))
    axes = fig.subplots(NPAD, sharex=True)
    for i in range(NPAD):
        #fig = plt.figure()
        n, bins, patches = axes[i].hist(data[:, i], bins=512, log=True, normed=True)
        axes[i].set_ylabel(i)
        y = mlab.normpdf(bins, m[i], s[i])
        axes[i].plot(bins, y, '--')
    fig.tight_layout()
    plt.show()#block=False)

def plot_kmeans(data, fname, kmeans, **kw):
    fig = plt.figure(figsize=(16, 12))
    fig.subplots_adjust(hspace=0)
    axes = fig.subplots(NPAD)
    centers_norm = np.linalg.norm(kmeans.cluster_centers_, axis=1)
    nonsil_index = np.argmax(centers_norm)
    labels = kmeans.predict(data)
    for i in range(NPAD):
        ploted = data[:, i]
        axes[i].plot(ploted, '-+')
        axes[i].plot(np.arange(len(ploted))[labels == nonsil_index], ploted[labels == nonsil_index], 'r+')
        axes[i].set_ylabel(i)
    plt.show()
    # plt.savefig('%s.png' % fname)
    plt.close()
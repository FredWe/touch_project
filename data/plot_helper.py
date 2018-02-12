import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np

NPAD = 15
SCANRES = 14

def plot_values(data, fname):
    fig = plt.figure()
    axes = fig.subplots(NPAD)#, sharey=True)
    for i in range(NPAD):
        axes[i].plot(data[:, i], '-+')
        axes[i].set_ylabel(i)
    plt.savefig('%s.png' % fname)
    plt.close()

def hist_values(data, ylogflag):
    fig = plt.figure()
    axes = fig.subplots(NPAD, sharex=True)
    for i in range(NPAD):
        #fig = plt.figure()
        axes[i].hist(data[:, i], bins=512, log=ylogflag)
        axes[i].set_ylabel(i)
    plt.show()#block=False)

def hist_normpdf(data):
    s = np.std(data, axis=0)
    m = np.mean(data, axis=0)
    fig = plt.figure()
    axes = fig.subplots(NPAD, sharex=True)
    for i in range(NPAD):
        #fig = plt.figure()
        n, bins, patches = axes[i].hist(data[:, i], bins=512, log=True, normed=True)
        axes[i].set_ylabel(i)
        y = mlab.normpdf(bins, m[i], s[i])
        axes[i].plot(bins, y, '--')
    fig.tight_layout()
    plt.show()#block=False)
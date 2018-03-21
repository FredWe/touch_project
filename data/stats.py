import io_helper
import plot_helper
import sys
import numpy as np
import data_helper
import logging
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture

maxth = 16383 # 2 ** 14
minth = 12288 # maxth * 3 / 4
NPAD = 15

def val2char(val, vmin, vmax):
    if val < vmin:
        return '-'
    if val > vmax:
        return '+'
    return ' '

def plot_values_annotation(data, fname, **kw):
    fig = plt.figure(figsize=(16, 12))
    axes = fig.subplots(NPAD)#, sharey=True)
    flg = False
    for i in range(NPAD):
        axes[i].plot(data[:, i])#, '-+')
        axes[i].set_ylabel(i)
        vmin = kw['datameans'] - 3 * kw['datastds']
        # vmax = 0
        ymin = max(min(data[:, i]), vmin[i])
        # ymax = min(max(data[:, i]), vmax)
        ymax = max(data[:, i])
        axes[i].set_ylim(ymin, ymax)
        for ii in range(data.shape[0]):
            ch = val2char(data[ii, i], ymin, ymax)
            if ch == '-':
                flg = True
            axes[i].text(ii, ymin, ch, weight='bold', color='red')
    if flg:
        plt.savefig('%s.png' % fname)
    plt.close()

def plot_delta_zero_annotation(data, fname, **kw):
    fig = plt.figure(figsize=(16, 12))
    axes = fig.subplots(NPAD + 1)#, sharey=True)
    data = np.diff(data, axis=0)
    flg = False
    threshold = 15
    rep = np.sum(data == 0, axis=1)
    for i in range(NPAD + 1):
        ploted = None
        if i == NPAD:
            ploted = rep
        else:
            ploted = data[:, i]
        axes[i].plot(ploted)
        axes[i].set_ylabel(i)
        ymin = min(ploted)
        if i < NPAD:
            for ii in range(data.shape[0]):
                ch = ''
                if ploted[ii] == 0:
                    flg = True
                    ch = '-'
                axes[i].text(ii, ymin, ch, weight='bold', color='red')
        else:
            for ii in range(data.shape[0]):
                ch = ''
                if ploted[ii] >= threshold:
                    flg = True
                    ch = '^'
                axes[i].text(ii, ymin, ch, weight='bold', color='red')
    if flg:
        plt.savefig('%s.png' % fname)
    plt.close()

def plot_pca(X):
    import matplotlib.pyplot as plt
    from sklearn.decomposition import PCA
    from mpl_toolkits.mplot3d import Axes3D

    pca = PCA(n_components=3)
    X_r = pca.fit(X).transform(X)

    # Percentage of variance explained for each components
    print('explained variance ratio (first two components): %s'
        % str(pca.explained_variance_ratio_))

    fig = plt.figure(figsize=(16, 12))
    # ax = Axes3D(fig)
    # plt.figure(figsize=(16, 12))
    # colors = ['navy', 'turquoise', 'darkorange']
    # lw = .001

    # for color, i, target_name in zip(colors, [0, 1, 2], target_names):
    plt.scatter(X_r[:, 0], X_r[:, 1], alpha=.8)
    # ax.scatter(X_r[:, 0], X_r[:, 1], X_r[:, 2], alpha=.8)
    plt.legend(loc='best', shadow=False, scatterpoints=1)
    plt.title('PCA of all samples')

    plt.show()

def kmeans_pca(X, name):
    K = 2
    kmeans = KMeans(n_clusters=K, random_state=0).fit(X)
    print(kmeans.cluster_centers_)
    kmeans_labels = kmeans.predict(X)

    pca = PCA(n_components=2)
    X_r = pca.fit_transform(X)

    # Percentage of variance explained for each components
    print('explained variance ratio (first two components): %s'
        % str(pca.explained_variance_ratio_))

    fig = plt.figure(figsize=(16, 12))
    # colors = ['navy', 'turquoise', 'darkorange']
    colors = ['blue', 'red']
    target_names = ['Class 0', 'Class 1']

    for color, i, target_name in zip(colors, [0, 1], target_names):
        plt.scatter(X_r[kmeans_labels == i, 0], X_r[kmeans_labels == i, 1], alpha=.8, c=color, label=target_name)
    plt.legend(loc='best', shadow=False, scatterpoints=1)
    plt.title('PCA of %s' % name)
    # plt.savefig('PCA-2means%s.png' % name)
    plt.show()
    plt.close()

def gmm_pca(X, name):
    K = 2
    gmm = GaussianMixture(n_components=K, random_state=0).fit(X)
    print(gmm.means_)
    gmm_labels = gmm.predict(X)

    pca = PCA(n_components=2)
    X_r = pca.fit_transform(X)

    # Percentage of variance explained for each components
    print('explained variance ratio (first two components): %s'
        % str(pca.explained_variance_ratio_))

    fig = plt.figure(figsize=(16, 12))
    # colors = ['navy', 'turquoise', 'darkorange']
    colors = ['blue', 'red']
    target_names = ['Class 0', 'Class 1']

    for color, i, target_name in zip(colors, [0, 1], target_names):
        plt.scatter(X_r[gmm_labels == i, 0], X_r[gmm_labels == i, 1], alpha=.8, c=color, label=target_name)
    plt.legend(loc='best', shadow=False, scatterpoints=1)
    plt.title('PCA of %s' % name)
    # plt.savefig('PCA-2gmm%s.png' % name)
    plt.show()
    plt.close()

def main():
    action_names = [
        '_click-button-up_',
        '_click-button-down_',
        '_click-button-left_',
        '_click-button-right_',
        '_click-button-leftup_',
        '_click-button-leftdown_',
        '_click-button-rightup_',
        '_click-button-rightdown_',
        '_click-button-MFB_',
        '_hush_',
        '_shorthush_',
        '_double-shorthush_',
        '_double-click_',
        '_longpress_']
    action_names = [
        # '_longpress_',
        # '_click-button-MFB_',
        # '_hush_',
        '_shorthush_']
    arkmat = io_helper.parsefile_ark2mat(sys.argv[1])
    # utt2word = io_helper.parse_dictfile(sys.argv[2])
    
    arkmat = data_helper.medfilt(arkmat, 3)
    arkmat = data_helper.stripcut(arkmat, 3, 3)
    alldata = np.concatenate(list(arkmat.values()), axis=0)
    datameans = np.mean(alldata, axis=0)
    datastds = np.std(alldata, axis=0)
    logging.info('std:\n%s' % datastds)
    logging.info('mean:\n%s' % datameans)

    # arkmat = data_helper.silencecut(arkmat, utt2word, 10, 10)

    # arkmat = data_helper.normalize(arkmat)
    # arkmat = data_helper.minmax(arkmat)
    # arkmat = data_helper.drop_negative(arkmat, -10, 0)
    alldata = np.concatenate(list(arkmat.values()), axis=0)[:, :12]
    norms = np.linalg.norm(alldata, axis=1)
    logging.debug(alldata.shape)
    logging.debug(norms.shape)
    key, data = arkmat.popitem()
    logging.debug(key)
    logging.debug(np.linalg.norm(data[:, :12], axis=1) > 70)
    logging.debug(np.arange(data.shape[0])[np.linalg.norm(data[:, :12], axis=1) > 70])
    # plot_helper.hist_values(norms, True)
    # plt.hist(norms, bins=1024, log=True)

    """
    actionlen = {}
    for name in action_names:
        print(name)
        filtered_arkmat = {k: m for k, m in arkmat.items() if name in k}
        alldata = np.concatenate(list(filtered_arkmat.values()), axis=0)
        # kmeans_pca(alldata, name)
        K = 2
        kmeans = KMeans(n_clusters=K, random_state=0).fit(alldata)
        def kmeans_count(data, kmeans):
            centers_norm = np.linalg.norm(kmeans.cluster_centers_, axis=1)
            nonsil_label = np.argmax(centers_norm)
            labels = kmeans.predict(data)
            nonsil_inds = np.arange(data.shape[0])[labels == nonsil_label]
            try:
                start = min(nonsil_inds)
                end = max(nonsil_inds)
            except Exception as e:
                return None
            # return end - start + 1
            return None # TODO
    """
        # plot actions time length distribution
    """
        nonsil_lens = [kmeans_count(m, kmeans) for m in filtered_arkmat.values() if kmeans_count(m, kmeans) != None]
        actionlen[name] = nonsil_lens
        """

        # uttid, data = filtered_arkmat.popitem()
        # plot_helper.plot_kmeans(data, uttid, kmeans)

    """
    fig = plt.figure(figsize=(16, 12))
    axes = fig.subplots(len(action_names), sharex=True)
    for i, name in enumerate(action_names):
        axes[i].hist(actionlen[name], bins=128)#, log=ylogflag)
        axes[i].set_ylabel(name)
    """

    # plot actions time length distribution
    """
    for i, name in enumerate(action_names):
        fig = plt.figure(figsize=(16, 12))
        plt.title(name)
        plt.hist(actionlen[name], bins=128)#, log=ylogflag)
        plt.axvline(np.median(actionlen[name]), color='y', linestyle='dashed', linewidth=2)
        plt.text(np.median(actionlen[name]) + 0.1, 20, np.median(actionlen[name]))
    """
    plt.show()

    # kmeans = KMeans(n_clusters=2, random_state=0).fit(alldata)
    # print(alldata.shape)
    # for uttid, data in arkmat.items():
    #     # plot_delta_zero_annotation(data, uttid)
    #     plot_helper.plot_kmeans(data, uttid, kmeans)


if __name__ == '__main__':
    logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)
    main()
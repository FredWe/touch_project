import io_helper
import plot_helper
import sys
import numpy as np
import data_helper
import logging
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

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
    fig = plt.figure()
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
    fig = plt.figure()
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

def plot_kmeans(data, fname, kmeans, **kw):
    fig = plt.figure(figsize=(16, 12))
    axes = fig.subplots(NPAD)#, sharey=True)
    flg = False
    centers_norm = np.linalg.norm(kmeans.cluster_centers_, axis=1)
    sil_index = np.argmax(centers_norm)
    labels = kmeans.predict(data)
    for i in range(NPAD):
        ploted = data[:, i]
        axes[i].plot(ploted, '-+')
        axes[i].plot(np.arange(len(ploted))[labels == sil_index], ploted[labels == sil_index], 'r+')
        axes[i].set_ylabel(i)
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

    fig = plt.figure()
    # ax = Axes3D(fig)
    # plt.figure()
    # colors = ['navy', 'turquoise', 'darkorange']
    # lw = .001

    # for color, i, target_name in zip(colors, [0, 1, 2], target_names):
    plt.scatter(X_r[:, 0], X_r[:, 1], alpha=.8)
    # ax.scatter(X_r[:, 0], X_r[:, 1], X_r[:, 2], alpha=.8)
    plt.legend(loc='best', shadow=False, scatterpoints=1)
    plt.title('PCA of all samples')

    plt.show()

def plot_manifold(X):
    import numpy as np
    import matplotlib.pyplot as plt
    from time import time
    from sklearn import datasets, manifold
    # # 使用sklearn的manifold包中的MDS类，先指定把X转换到一个三维空间中，
    # manif = manifold.LocallyLinearEmbedding(n_components=2, n_jobs=-1, method='ltsa', n_neighbors=6, eigen_solver='dense') # 转换成2维的时候修改这里
    # Xtrans = manif.fit_transform(X)

    # # # t-SNE embedding of the digits dataset
    # # print("Computing t-SNE embedding")           
    # # tsne = manifold.TSNE(n_components=2, init='pca')
    # # t0 = time()
    # # Xtrans = tsne.fit_transform(X)

    # plt.scatter(Xtrans[:, 0], Xtrans[:, 1], alpha=.8)
    # plt.legend(loc='best', shadow=False, scatterpoints=1)
    # plt.title("manifold")
    
    # # plot_embedding(X_tsne,                                   
    # #             "t-SNE embedding of the digits (time %.2fs)" %
    # #             (time() - t0))                           

    # plt.show() 

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
    plt.savefig('PCA-2means%s.png' % name)
    plt.close()
    # plt.show()

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
    arkmat = io_helper.parsefile_ark2mat(sys.argv[1])
    
    arkmat = data_helper.medfilt(arkmat, 3)
    arkmat = data_helper.stripcut(arkmat, 3, 3)
    alldata = np.concatenate(list(arkmat.values()), axis=0)
    datameans = np.mean(alldata, axis=0)
    datastds = np.std(alldata, axis=0)
    logging.info('std:\n%s' % datastds)
    logging.info('mean:\n%s' % datameans)

    # arkmat = data_helper.normalize(arkmat)
    # arkmat = data_helper.minmax(arkmat)
    # arkmat = data_helper.drop_negative(arkmat, 0, 0)
    alldata = np.concatenate(list(arkmat.values()), axis=0)
    # plot_helper.hist_values(alldata, True)

    for name in action_names:
        print(name)
        filtered_arkmat = {k: m for k, m in arkmat.items() if name in k}
        alldata = np.concatenate(list(filtered_arkmat.values()), axis=0)
        # kmeans_pca(alldata, name)
        K = 2
        kmeans = KMeans(n_clusters=K, random_state=0).fit(alldata)
        uttid, data = filtered_arkmat.popitem()
        plot_kmeans(data, uttid, kmeans)
    
    # K = 2
    # kmeans = KMeans(n_clusters=K, random_state=0).fit(alldata)
    
    # print(alldata.shape)
    # for uttid, data in arkmat.items():
    #     # plot_delta_zero_annotation(data, uttid)
    #     plot_kmeans(data, uttid, kmeans)


if __name__ == '__main__':
    logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.INFO)
    main()
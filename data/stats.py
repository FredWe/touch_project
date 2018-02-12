import io_helper
import plot_helper
import sys
import numpy as np
import data_helper
import logging
import matplotlib.pyplot as plt

maxth = 16383 # 2 ** 14
minth = 12288 # maxth * 3 / 4
NPAD = 15

def val2char(val):
    if val < minth:
        return '-'
    if val > maxth:
        return '+'
    return ' '

def plot_values_annotation(data, fname):
    fig = plt.figure()
    axes = fig.subplots(NPAD)#, sharey=True)
    flg = False
    for i in range(NPAD):
        axes[i].plot(data[:, i])#, '-+')
        axes[i].set_ylabel(i)
        ymin = max(min(data[:, i]), minth)
        ymax = min(max(data[:, i]), maxth)
        axes[i].set_ylim(ymin, ymax)
        for ii in range(data.shape[0]):
            ch = val2char(data[ii, i])
            if ch != ' ':
                flg = True
            axes[i].text(ii, ymin, ch, weight='bold', color='red')
    if flg:
        plt.savefig('%s.png' % fname)
    plt.close()

def main():
    arkmat = io_helper.parsefile_ark2mat(sys.argv[1])
    datum = list(arkmat.values())
    alldata = np.concatenate(datum, axis=0)
    logging.info('std:\n%s' % np.std(alldata, axis=0))
    logging.info('mean:\n%s' % np.mean(alldata, axis=0))
    arkmat = data_helper.medfilt(arkmat, 3)
    arkmat = data_helper.stripcut(arkmat, 3, 3)
    # arkmat = data_helper.normalize(arkmat)
    filt_alldata = np.concatenate(list(arkmat.values()), axis=0)
    # logging.debug(filt_alldata)
    plot_helper.hist_values(filt_alldata, False)
    # print(alldata.shape)
    # for uttid, data in arkmat.items():
    #     plot_values_annotation(data, uttid)


if __name__ == '__main__':
    logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.INFO)
    main()
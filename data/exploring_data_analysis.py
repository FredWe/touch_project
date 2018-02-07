import glob
import logging
import numpy as np
import os.path
import matplotlib.pyplot as plt
import scipy.signal
import sklearn.preprocessing

NPAD = 15

def check_sampling_interval(filenames):
    interval_dict = {
        filepath:
        float(os.path.splitext(os.path.basename(filepath))[0].split('_')[-1]) /
        sum(1 for line in open(filepath)) * 1000
        for filepath in filenames}
    for k,v in interval_dict.items():
        if v < 12.5:
            print(k, v)
    #logging.debug(interval_list)
    logging.debug('max, %s' % max(interval_dict.values()))
    logging.debug('min, %s' %  min(interval_dict.values()))
    logging.debug('std, %s' % np.std(list(interval_dict.values())))
    logging.debug('mean, %s' % np.mean(list(interval_dict.values())))

def parse_file(filepath):
    data = np.zeros((0, NPAD))
    #logging.debug(filepath)
    with open(filepath, 'r') as file_data:
        for line in file_data:
            rawbytes = [
                onebyte.zfill(2)
                for onebyte in line.strip().split()]
            #logging.debug(rawbytes)
            if not rawbytes:
                continue
            diffsigs = [
                int(rawbytes[idx * 4] + rawbytes[idx * 4 + 1], 16) -
                int(rawbytes[idx * 4 + 2] + rawbytes[idx * 4 + 3], 16)
                for idx in range(NPAD)]
            #logging.debug(diffsigs)
            #logging.debug(np.array(diffsigs).shape)
            data = np.append(data, [diffsigs], axis=0)
    #logging.debug(data)
    #logging.debug(data.shape)
    return data

def analyze_values(filedata_list):
    allvalues = np.concatenate(filedata_list, axis=0)
    #logging.debug(allvalues)
    #logging.debug(allvalues.shape)
    logging.debug('max:\n%s' % np.amax(allvalues, axis=0))
    logging.debug('min:\n%s' %  np.amin(allvalues, axis=0))
    logging.debug('std:\n%s' % np.std(allvalues, axis=0))
    logging.debug('mean:\n%s' % np.mean(allvalues, axis=0))

def plot_values(data):
    fig = plt.figure()
    axes = fig.subplots(NPAD)
    for i in range(NPAD):
        axes[i].plot(data[:, i], '-+')
        axes[i].set_ylabel(i)
    #plt.show(block=False)

def hist_values(data):
    fig = plt.figure()
    axes = fig.subplots(NPAD)
    for i in range(NPAD):
        #fig = plt.figure()
        axes[i].hist(data[:, i], bins=512, log=True)
        axes[i].set_ylabel(i)
    #plt.show(block=False)

def stft_values(data):
    fig = plt.figure()
    axes = fig.subplots(NPAD)
    for i in range(NPAD):
        f,t,Zxx = scipy.signal.stft(data[:, i], 77, nperseg=10)
        axes[i].pcolormesh(t, f, np.abs(Zxx), vmax=200)
        axes[i].set_ylabel(i)
    #plt.show(block=False)

def percentile_scale(data, prcmin, prcmax):
    datamin = np.percentile(data, prcmin, axis=0)
    datamax = np.percentile(data, prcmax, axis=0)
    return np.clip(data, datamin, datamax)

def main():
    logging.basicConfig(level=logging.DEBUG)
    DATA_FILENAMES = glob.glob('*/*[0-9].[0-9]*.rec')
    check_sampling_interval(DATA_FILENAMES)
    #logging.debug([parse_file(onef) for onef in DATA_FILENAMES])
    
    datum = [parse_file(onef) for onef in DATA_FILENAMES]
    filtered_datum = [scipy.signal.medfilt(data, (3, 1)) for data in datum]
    #logging.debug(analyze_values(datum))
    # logging.debug(analyze_values(filtered_datum))
    # filei = 0
    # for anali in range(len(DATA_FILENAMES)):
    #     logging.debug(DATA_FILENAMES[anali])
    #     data = parse_file(DATA_FILENAMES[anali])
    #     plot_values(data)
    #     # plot_values(scipy.signal.medfilt(data, (3, 1)))
    #     plt.savefig('%s.png' % os.path.splitext(os.path.basename(DATA_FILENAMES[anali]))[0])
    #     # stft_values(datum[anali])
    #     # plt.savefig('%s_stft.png' % os.path.splitext(os.path.basename(DATA_FILENAMES[anali]))[0])
    
    alldata = np.concatenate(datum, axis=0)
    # hist_values(alldata)
    # plt.savefig('hist_all.png')

    
    filtered_alldata = np.concatenate(filtered_datum, axis=0)
    logging.debug(filtered_alldata.shape)
    for prc in [0.1, 1, 99, 99.99]:
        prcs = np.percentile(filtered_alldata, prc, axis=0)
        logging.debug("%s percentile" % prc)
        logging.debug(prcs)
    plot_values(filtered_alldata)
    scaled_alldata = percentile_scale(filtered_alldata, 1, 99)
    plot_values(scaled_alldata)
    hist_values(scaled_alldata)
    plt.savefig('hist_all.png')
    
    #hist_values(filtered_alldata)

    #plt.show()

if __name__ == '__main__':
    main()


import numpy as np
import os
import matplotlib.pyplot as plt
import scipy.signal
import sklearn.preprocessing
import json
import logging
import glob
import kaldi_io
import random

NPAD = 15

def parse_file(filepath):
    data = np.zeros((0, NPAD))
    #logging.debug(filepath)
    with open(filepath, 'r') as file_data:
        for line in file_data:
            rawbytes = [
                onebyte.zfill(2)
                for onebyte in line.strip().split()]
            #logging.debug(rawbytes)
            if not rawbytes: # remove empty line
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
        axes[i].plot(data[:, i])#, '+')
        axes[i].set_ylabel(i)
    #plt.show(block=False)

def hist_values(data):
    fig = plt.figure()
    axes = fig.subplots(NPAD)
    for i in range(NPAD):
        #fig = plt.figure()
        axes[i].hist(data[:, i], bins=20, normed=True, log=True)
        axes[i].set_ylabel(i)
    #plt.show(block=False)

def filter_clip_scale(alldata):
    PRCMIN = 1
    PRCMAX = 99
    scaler = sklearn.preprocessing.MinMaxScaler()
    for folder in alldata:
        groupdata = np.concatenate([item['data'] for item in alldata[folder]], axis=0)
        datamin = np.percentile(groupdata, PRCMIN, axis=0)
        datamax = np.percentile(groupdata, PRCMAX, axis=0)
        groupdata = np.clip(groupdata, datamin, datamax)
        scaler.fit(groupdata)
        for item in alldata[folder]:
            data = scipy.signal.medfilt(item['data'], (3, 1))
            data = np.clip(data, datamin, datamax)
            item['data'] = scaler.transform(data)

def playbackward_dataugment(alldata):
    transdict = {
        'Clockwise': 'CounterClockwise',
        'CounterClockwise': 'Clockwise'}
    for folder in alldata:
        for idx in range(len(alldata[folder])):
            origitem = alldata[folder][idx]
            if origitem['action'] == 'Slide':
                alldata[folder].append({
                    'basicname': origitem['basicname'],
                    'variant': origitem['variant'] + '->backward',
                    'action': origitem['action'],
                    'actionparams': [transdict[origitem['actionparams'][0]]] + origitem['actionparams'][:0:-1],
                    'data': np.flip(origitem['data'], 0)})

def rotate_dataugment(alldata):
    for folder in alldata:
        for idx in range(len(alldata[folder])):
            origitem = alldata[folder][idx]
            if origitem['action'] == 'Slide':
                dataparts = np.split(origitem['data'], [12], axis=1)
                for delta in range(1, 12):
                    alldata[folder].append({
                        'basicname': origitem['basicname'],
                        'variant': origitem['variant'] + '->rotated',
                        'action': origitem['action'],
                        'actionparams': [origitem['actionparams'][0]] + [
                            (int(pos) + delta) % 12 for pos in origitem['actionparams'][1:]],
                        'data': np.concatenate(
                            (np.roll(dataparts[0], delta, axis=1), dataparts[1]),
                            axis=1)})

def label_data(alldata):
    for folder in alldata:
        for item in alldata[folder]:
            if item['action'] == 'Slide':
                if len(item['actionparams']) < 3:
                    logging.debug(item['actionparams'])
                direction = item['actionparams'][0]
                start = int(item['actionparams'][1])
                end = int(item['actionparams'][2])
                delta = 0
                if direction == 'Clockwise':
                    delta = (end - start) % 12
                elif direction == 'CounterClockwise':
                    delta = (start - end) % 12
                delta = 12 if not delta else delta
                item['label'] = '%s%s' % (direction, delta)
            else:
                item['label'] = '%s%s' % (item['action'], ''.join(item['actionparams']))

def load_data(alldata):
    """
    alldata strcture: alldata{folder} -> folder: samples[singledata{}] ->
        singledata: {'basicname': *. 'variant': *, 'action': *, 'actionparams': *, 'data': *} ->
        data: np.ndarray(n, 15)
    """
    filenames = glob.glob('*/*.rec')
    for filepath in filenames:
        paths = os.path.split(filepath)
        folder = paths[0]
        basicname  = os.path.splitext(paths[1])[0]
        if folder not in alldata:
            alldata[folder] = []
        actarr = basicname.split('_')[1].split('-')
        if actarr[0] == 'Slide' and len(actarr) < 4:
            logging.debug('basicname' % basicname)
            logging.debug(actarr)
        alldata[folder].append({
            'basicname': basicname,
            'variant': 'original',
            'action': actarr[0],
            'actionparams': actarr[1:],
            'data': parse_file(filepath)})

def export2kaldi(databyid):
    kaldidata = databyid
    filter_field = ('Click1', 'Hush', 'Click2', 'Click3')#, 'LongPress')
    #exclude_field = ('LongPress')
    test_size = 0.2
    trainset = []
    testset = []
    filtered_kaldidata = {}
    for k, v in kaldidata.items():
        label = k.split('_')[0]
        if label in filter_field:
        #if label not in exclude_field:
            if label not in filtered_kaldidata:
                filtered_kaldidata[label] = []
            filtered_kaldidata[label].append((k, v))
    for label in filtered_kaldidata:
        length = len(filtered_kaldidata[label])
        random.shuffle(filtered_kaldidata[label])
        testset.extend(filtered_kaldidata[label][:int(length * test_size)])
        trainset.extend(filtered_kaldidata[label][int(length * test_size):])
    with kaldi_io.open_or_fd('feats_train.ark','wb') as f:
        for k, m in trainset:
            kaldi_io.write_mat(f, m, k)
    with kaldi_io.open_or_fd('feats_test.ark','wb') as f:
        for k, m in testset:
            kaldi_io.write_mat(f, m, k)
    # after this, copy-feats could be used to generate the corresponding scp file

def output(alldata):
    OUTPUT_FOLDER = 'output'
    databyid = {}
    metadata = {}
    index = 0
    if not os.path.isdir(OUTPUT_FOLDER):
        os.mkdir(OUTPUT_FOLDER)
    for folder in alldata:
        for item in alldata[folder]:
            name = '%s_%s' % (item['label'], index)
            np.savetxt('%s/%s.csv' % (OUTPUT_FOLDER, name), item['data'], delimiter=',')
            metadata[name] = {k: v for k, v in item.items() if k != 'data'}
            databyid[name] = item['data']
            index += 1
    with open('index.json', 'w') as fp:
        json.dump(metadata, fp)
    return databyid

def main():
    logging.basicConfig(level=logging.DEBUG)
    alldata = {}
    databyid = {}
    load_data(alldata)
    filter_clip_scale(alldata)
    playbackward_dataugment(alldata)
    rotate_dataugment(alldata)
    label_data(alldata)
    databyid = output(alldata)
    export2kaldi(databyid)
"""
    index = 0
    for folder in alldata:
        for item in alldata[folder]:
            plot_values(item['data'])
            plt.savefig('%s_%s.png' % (item['label'], index))
            index += 1
"""

if __name__ == '__main__':
    main()


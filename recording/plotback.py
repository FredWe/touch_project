#! /usr/bin/env python3
# -*- coding: utf-8 -*-

' readfile from argument module '

__author__ = 'Fred Wei'

import sys
import re
import logging

import numpy as np
import matplotlib.pyplot as plt

logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)
logging.debug(sys.argv)
NSIGS = 17
NPAD = 15
NCLICKER = 3
NSLIDER = 12
INPUT_FILENAME = sys.argv[1]
EXT = INPUT_FILENAME.split('.')[-1]
CONF = {
    'txt': {
        'pattern': r'w 37\+ 00\+ 00\+ r 37\+ (.+)\+ p',
        'delim': r'+ '
        },
    'dat': {
        'pattern': r'37 (.+)',
        'delim': r' '
        },
    'rec': {
        'pattern': r'(.+)',
        'delim': r' '
        }
    }
if EXT == 'txt':
    logging.debug('txt')
elif EXT == 'iic' or EXT == 'dat':
    logging.debug('iic or dat')
    EXT = 'dat'
elif EXT == 'rec':
    logging.debug('rec')
else:
    logging.warning('unrecognized extension')

def treatline(line):
    """
    treating a sindle line of dumped datafile, return parsed data
    """
    logging.debug(line)
    mat = re.match(CONF[EXT]['pattern'], line)
    logging.debug(mat)
    rawsigs, sigs = None, None
    if mat:
        logging.debug(mat.group(1))
        rawbytes = mat.group(1).split(CONF[EXT]['delim'])
        logging.debug(rawbytes)
        rawbytes.insert(-3, '00') # align to decode
        logging.debug(rawbytes)
        bytes_zipped = zip(rawbytes[::2], rawbytes[1::2])
        rawsigs = [int(t[0].zfill(2) + t[1].zfill(2), 16) for t in bytes_zipped]
        logging.debug(rawsigs)
        rawsigs_zipped = zip(rawsigs[:-2:2], rawsigs[1:-2:2])
        sigs = [t[0] - t[1] for t in rawsigs_zipped] + rawsigs[-2:]
        logging.debug(sigs)
    return rawsigs, sigs

def plot_values(data):
    fig = plt.figure()
    axes = fig.subplots(data.shape[1], sharey=True)
    for i in range(data.shape[1]):
        axes[i].plot(data[:, i], '-+')
        axes[i].set_ylabel(i)
    #plt.show(block=False)

def plot_rawvalues(data):
    raws = data[:, ::2]
    bslns = data[:, 1::2]
    for dat in raws, bslns:
        fig = plt.figure()
        axes = fig.subplots(dat.shape[1])
        for i in range(dat.shape[1]):
            axes[i].plot(dat[:, i], '-+')
            axes[i].set_ylabel(i)
            # minprc, maxprc = 0, 100
            minprc, maxprc = 2, 100
            ymin = np.percentile(dat[:, i], minprc)
            ymax = np.percentile(dat[:, i], maxprc)
            axes[i].set_ylim(ymin, ymax)

def main():
    """
    main function
    """
    # Data for plotting
    data = np.zeros((1, 15))
    rawdata = np.zeros((1, 30))

    with open(INPUT_FILENAME, 'r') as file_data:
        if EXT != 'csv':
            for line in file_data:
                rawsigs, sigs = treatline(line.strip())
                logging.debug(sigs)
                logging.debug(rawsigs)
                logging.debug(len(rawsigs) if rawsigs else -1)
                logging.debug(rawsigs[:30] if rawsigs else '_')
                if sigs:
                    data = np.append(data, [sigs[:15]], axis=0)
                    rawdata = np.append(rawdata, [rawsigs[:30]], axis=0)
        else:
            data = np.loadtxt(file_data, delimiter=',')

    print(data[:, 1].shape)

    plot_values(data)
    # plot_rawvalues(rawdata)
    plt.show()

if __name__ == '__main__':
    main()

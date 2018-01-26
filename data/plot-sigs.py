#! /usr/bin/env python3
# -*- coding: utf-8 -*-

' readfile from argument module '

__author__ = 'Fred Wei'

import sys
import re
import logging
import glob
import os

import numpy as np
import matplotlib.pyplot as plt

logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.INFO)
logging.debug(sys.argv)
NSIGS = 17
NPAD = 15
NCLICKER = 3
NSLIDER = 12

def treatline(line):
    """
    treating a sindle line of dumped datafile, return parsed data
    """
    logging.debug(line)
    mat = re.match(r'(.+)', line)
    logging.debug(mat)
    rawsigs, sigs = None, None
    if mat:
        logging.debug(mat.group(1))
        rawbytes = mat.group(1).split()
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

def plot_rawvalues(data, fname):
    raws = data[:, ::2]
    bslns = data[:, 1::2]
    for name, dat in {'raw': raws, 'baseline': bslns}.items():
        for minprc, maxprc in ((2, 98), (0, 100)):
            fig = plt.figure()
            axes = fig.subplots(dat.shape[1])
            for i in range(dat.shape[1]):
                axes[i].plot(dat[:, i], '-+')
                axes[i].set_ylabel(i)
                ymin = np.percentile(dat[:, i], minprc)
                ymax = np.percentile(dat[:, i], maxprc)
                axes[i].set_ylim(ymin, ymax)
            plt.savefig('%s_%s_%dprc-%dprc.png' % (fname, name, minprc, maxprc))
            plt.close()

def plot_values(data, fname):
    fig = plt.figure()
    axes = fig.subplots(NPAD)#, sharey=True)
    for i in range(NPAD):
        axes[i].plot(data[:, i], '-+')
        axes[i].set_ylabel(i)
    plt.savefig('%s.png' % fname)
    plt.close()

def main():
    """
    main function
    """
    DATA_FILENAMES = glob.glob('*/*.rec')
    for onef in DATA_FILENAMES:
        data = np.zeros((1, 15))
        rawdata = np.zeros((1, 30))
        with open(onef, 'r') as file_data:
            for line in file_data:
                rawsigs, sigs = treatline(line.strip())
                logging.debug(sigs)
                logging.debug(rawsigs)
                logging.debug(len(rawsigs) if rawsigs else -1)
                logging.debug(rawsigs[:30] if rawsigs else '_')
                if sigs:
                    data = np.append(data, [sigs[:15]], axis=0)
                    rawdata = np.append(rawdata, [rawsigs[:30]], axis=0)        
        logging.info(onef)
        prefix = os.path.basename(onef).split('_')[1]
        if prefix.startswith('Slide'):
            continue
        # plot_rawvalues(rawdata, os.path.basename(onef))
        plot_values(data, os.path.basename(onef))
        # break

if __name__ == '__main__':
    main()

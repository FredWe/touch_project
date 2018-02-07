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

# INPUT_FILENAME = sys.argv[1]

def treatline(line):
    """
    treating a sindle line of dumped datafile, return parsed data
    """
    logging.debug(line)
    mat = re.match(r'(.+)', line)
    logging.debug(mat)
    sigsonmask = None
    if mat:
        logging.debug(mat.group(1))
        rawbytes = mat.group(1).split(r' ')
        logging.debug(rawbytes)
        onmask = (int(rawbytes[61], 16) << 8) | int(rawbytes[62], 16)
        logging.debug(onmask)
        sigsonmask = [int(x) for x in format(onmask, 'b').zfill(16)][::-1]
    return sigsonmask

def plot_values(data):
    fig = plt.figure()
    axes = fig.subplots(data.shape[1], sharey=True)
    for i in range(data.shape[1]):
        axes[i].plot(data[:, i], '-+')
        axes[i].set_ylabel(i)
    #plt.show(block=False)

def main():
    """
    main function
    """
    DATA_FILENAMES = glob.glob('*/*.rec')
    for onef in DATA_FILENAMES:
        logging.info(onef)
        prefix = os.path.basename(onef).split('_')[1]
        if prefix.startswith('Clock') or prefix.startswith('Counter') or prefix.startswith('Slide'):
            continue

        # Data for plotting
        data = np.zeros((1, 15))
        with open(onef, 'r') as file_data:
            for line in file_data:
                sigs = treatline(line.strip())
                logging.debug(sigs)
                if sigs:
                    data = np.append(data, [sigs[:15]], axis=0)

        plot_values(data)
        plt.savefig('%s.png' % os.path.basename(onef))
        plt.close()

    # # Data for plotting
    # data = np.zeros((1, 15))
    # with open(INPUT_FILENAME, 'r') as file_data:
    #     for line in file_data:
    #         sigs = treatline(line.strip())
    #         logging.debug(sigs)
    #         if sigs:
    #             data = np.append(data, [sigs[:15]], axis=0)

    # print(data[:, 1].shape)

    # plot_values(data)
    # plt.show()

if __name__ == '__main__':
    main()

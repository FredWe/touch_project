#! /usr/bin/env python3
# -*- coding: utf-8 -*-

' readfile from argument module '

__author__ = 'Fred Wei'

import os
import logging
import glob

import numpy as np
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.WARN)
NSIGS = 17
NPAD = 15

def plot_values(data):
    fig = plt.figure()
    axes = fig.subplots(NPAD)#, sharey=True)
    for i in range(NPAD):
        axes[i].plot(data[:, i], '-+')
        axes[i].set_ylabel(i)
    #plt.show(block=False)

def main():
    """
    main function
    """
    # Data for plotting

    DATA_FILENAMES = glob.glob('output/*.csv')
    for onef in DATA_FILENAMES:
        print(onef)
        prefix = os.path.basename(onef).split('_')[0]
        if prefix.startswith('Clock') or prefix.startswith('Counter'):
            continue
        data = np.loadtxt(onef, delimiter=',')
        plot_values(data)
        plt.savefig('%s.png' % os.path.basename(onef))

if __name__ == '__main__':
    main()

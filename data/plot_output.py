#! /usr/bin/env python3
# -*- coding: utf-8 -*-

' readfile from argument module '

__author__ = 'Fred Wei'

import sys
import logging

import io_helper
import plot_helper
import data_helper

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np

NPAD = 15
SCANRES = 14

def plot_values(data, fname):
    fig = plt.figure(figsize=(16, 12))
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
    # Data for plotting
    plt.rcParams['axes.formatter.useoffset'] = False

    arkmat = io_helper.parsefile_ark2mat(sys.argv[1])
    arkmat = {k: m  for k, m in arkmat.items() if 'longpress' in k}
    arkmat = data_helper.medfilt(arkmat, 3)
    arkmat = data_helper.stripcut(arkmat, 3, 3)

    for uttid, data in arkmat.items():
        plot_values(data, uttid)
    
if __name__ == '__main__':
    main()

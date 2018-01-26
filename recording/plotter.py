#! /usr/bin/env python3
# -*- coding: utf-8 -*-

' plotter: plotting module '

__author__ = 'Fred Wei'

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
from matplotlib.collections import PatchCollection
from matplotlib.animation import FuncAnimation

def _pol2cart(rho, phi):
    """
    transform polar coordinates to cartesian systems
    https://stackoverflow.com/questions/20924085/python-conversion-between-coordinates
    """
    x_cart = rho * np.cos(phi)
    y_cart = rho * np.sin(phi)
    return (x_cart, y_cart)

def waitforbuttonpress():
    plt.waitforbuttonpress()

class Plotter(object):
    """
    implementing a wrapper class for polymorphism
    """
    def __init__(self, interval, sourcetype):
        """
        initialize plotter differently to adapt multiple type of data source (
            static data or data queue)
        """
        self.interval = interval
        self.sourcetype = sourcetype # 'static' | 'queue'

    @staticmethod
    def anim_update_static(frame, patch_collection, state):
        """
        animation update: set Wedges' color
        """
        sigs = frame
        colors = [
            (sigs[i] - state['min'][i]) / (state['max'][i] - state['min'][i])
            for i in range(15)]

        patch_collection.set_array(
            np.array(colors[-4::-1] + colors[-3:])) # shift to adapt to actual layout
        return patch_collection,

    @staticmethod
    def anim_update_queue(_, dataq, patch_collection, state):
        """
        start data collection
        """
        rawline = dataq.get()
        rawbytes = rawline.split() # read data from queue
        #print(rawbytes)
        if len(rawbytes) != 63:
            return patch_collection,
        rawbytes.insert(-3, b'00') # align to decode
        rawsigs = [0] * 32
        try:
            rawsigs = [
                int(rawbytes[i].zfill(2) + rawbytes[i+1].zfill(2), 16)
                for i in range(0, len(rawbytes), 2)]
        except ValueError as ex:
            print(rawbytes)
            print(ex)
        # concat high byte & low byte and convert from HEX to DEC
        sigs = [rawsigs[i] - rawsigs[i+1] for i in range(0, len(rawsigs) - 2, 2)] + rawsigs[-2:]

        state['min'] = [min(state['min'][i], sigs[i]) for i in range(15)]
        state['max'] = [max(state['max'][i], sigs[i]) for i in range(15)]
        colors = [
            (sigs[i] - state['min'][i]) / (state['max'][i] - state['min'][i])
            for i in range(15)]

        patch_collection.set_array(
            np.array(colors[-4::-1] + colors[-3:])) # shift to adapt to actual layout
        return patch_collection,

    def plot(self, data):
        """
        reuse plotting code for polymorphism
        """
        theta = np.linspace(-75, 285, 13)
        theta_intern = np.linspace(45, 405, 4)

        fig = plt.figure()
        pltaxe = plt.axes(aspect='equal')
        pltaxe.set_xlim(-1.1, 1.1)
        pltaxe.set_ylim(-1.1, 1.1)

        patches = []
        patches.extend(
            Wedge((0, 0), 1, theta[i], theta[i+1], width=0.5, color='0')
            for i in range(len(theta) - 1))
        patches.extend(
            Wedge((0, 0), 0.5, theta_intern[i], theta_intern[i+1], width=0.5, color='1')
            for i in range(len(theta_intern) - 1))

        patch_collection = PatchCollection(patches, animated=True, cmap='jet')

        patch_collection.set_array(np.array([0] * 12 + [1] * 3))
        pltaxe.add_collection(patch_collection)
        plt.colorbar(patch_collection, ax=pltaxe)

        slider_degrees = range(270, -60 - 1, -30)
        #clicker_degrees = range(105, 345 + 1, 120)
        centers = [_pol2cart(1.05, deg * np.pi / 180) for deg in slider_degrees]

        for idx, cen in enumerate(centers):
            plt.text(
                cen[0], cen[1], str(idx),
                horizontalalignment='center', verticalalignment='center')

        # switch animation method by sourcetype
        state = {}
        if self.sourcetype == 'static':
            state = {
                'min': data['min'],
                'max': data['max']
            }

            _ = FuncAnimation(
                fig, self.anim_update_static, frames=data['sigs'], fargs=(patch_collection, state),
                interval=self.interval, repeat=False, blit=True)
        elif self.sourcetype == 'queue':
            state = {
                'min': [0] * 15,
                'max': [1] * 15
            }

            _ = FuncAnimation(
                fig, self.anim_update_queue, fargs=(data['queue'], patch_collection, state),
                interval=self.interval, repeat=False, blit=True)

        plt.show(block=False)

    def plot_static(self, data):
        """
        function for ploting static data (from file)
        """
        theta = np.linspace(-75, 285, 13)
        theta_intern = np.linspace(45, 405, 4)

        fig = plt.figure()
        pltaxe = plt.axes(aspect='equal')
        pltaxe.set_xlim(-1.1, 1.1)
        pltaxe.set_ylim(-1.1, 1.1)

        patches = []
        patches.extend(
            Wedge((0, 0), 1, theta[i], theta[i+1], width=0.5, color='0')
            for i in range(len(theta) - 1))
        patches.extend(
            Wedge((0, 0), 0.5, theta_intern[i], theta_intern[i+1], width=0.5, color='1')
            for i in range(len(theta_intern) - 1))

        patch_collection = PatchCollection(patches, animated=True, cmap='jet')

        state = {
            'min': data['min'],
            'max': data['max']
        }

        patch_collection.set_array(np.array([0] * 12 + [1] * 3))
        pltaxe.add_collection(patch_collection)
        plt.colorbar(patch_collection, ax=pltaxe)

        slider_degrees = range(270, -60 - 1, -30)
        #clicker_degrees = range(105, 345 + 1, 120)
        centers = [_pol2cart(1.05, deg * np.pi / 180) for deg in slider_degrees]

        for idx, cen in enumerate(centers):
            plt.text(
                cen[0], cen[1], str(idx),
                horizontalalignment='center', verticalalignment='center')

        _ = FuncAnimation(
            fig, self.anim_update_static, frames=data['sigs'], fargs=(patch_collection, state),
            interval=self.interval, repeat=False, blit=True)

        plt.show(block=False)

    def plot_queue(self, dataq):
        """
        plottinf data from queue
        """
        theta = np.linspace(-75, 285, 13)
        theta_intern = np.linspace(45, 405, 4)

        fig = plt.figure()
        plt_ax = plt.axes(aspect='equal')
        plt_ax.set_xlim(-1, 1)
        plt_ax.set_ylim(-1, 1)

        patches = []
        patches += [
            Wedge((0, 0), 1, theta[i], theta[i+1], width=0.5, color='0')
            for i in range(len(theta)-1)]
        patches += [
            Wedge((0, 0), 0.5, theta_intern[i], theta_intern[i+1], width=0.5, color='1')
            for i in range(len(theta_intern)-1)]

        patch_collection = PatchCollection(patches, cmap='jet', animated=True)

        state = {
            'min': [0] * 15,
            'max': [1] * 15
        }

        patch_collection.set_array(np.array([0] * 12 + [1] * 3))
        plt_ax.add_collection(patch_collection)
        plt.colorbar(patch_collection, ax=plt_ax)

        _ = FuncAnimation(
            fig, self.anim_update_queue, fargs=(dataq, patch_collection, state),
            interval=self.interval, repeat=False, blit=True)

        plt.show()

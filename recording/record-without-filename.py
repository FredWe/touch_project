#! /usr/bin/env python3
# -*- coding: utf-8 -*-

' recording & plotting sensor data & save them '

__author__ = 'Fred Wei'

import multiprocessing
import time
import queue

import serial
import os.path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
from matplotlib.collections import PatchCollection
from matplotlib.animation import FuncAnimation

def delayout(stateq, nameq, dataq):
    state = {
        'recording': False,
        'naming': False
    }
    filedata = []
    filename = ''
    while True:
        rawline = ser.readline().strip()
        dataq.put_nowait(rawline)
        #print('delayout: ' + ret)
        #print(state)
        #print(len(filedata))
        if not stateq.empty():
            stateqs = stateq.get_nowait()
            print('stateq get: ' + stateqs)
            if stateqs == 's':
                filedata.clear()
                state['recording'] = True
                state['naming'] = False
                filedata.append(rawline)
            elif stateqs == 'e':
                state['recording'] = False
                state['naming'] = True
            else:
                pass
            print(state)
        else:
            #print('delayout: stateq is empty')
            pass

        if not nameq.empty():
            nameqs = nameq.get_nowait()
            print('nameq get: ' + nameqs)
            filename = nameqs

            print(state)
        else:
            #print('delayout: nameq is empty')
            pass

        if state['recording']:
            filedata.append(rawline)
        elif state['naming']:
            if not bool(filedata):
                filename = ''
                state['recording'] = False
                state['naming'] = False
            elif bool(filename):
                i = 0
                while os.path.exists('%s_%s.rec' % (filename, i)):
                    i += 1
                with open('%s_%s.rec' % (filename, i) , 'w') as f:
                    f.write('\n'.join(line.decode() for line in filedata))
                print('%s lines are saved with filename as %s_%s.rec' % (len(filedata), filename, i))
                filedata.clear()
                filename = ''
                state['recording'] = False
                state['naming'] = False

def anim_update(framei, dataq, pc, state):
    # start data collection
    rawline = dataq.get()
    rawBytes = rawline.split() # read data from queue
    #print(rawBytes)
    if len(rawBytes) != 63:
        return pc,
    rawBytes.insert(-3, b'00') # align to decode
    rawSigs = [int(rawBytes[i].zfill(2) + rawBytes[i+1].zfill(2), 16) for i in range(0, len(rawBytes), 2)]
    # concat high byte & low byte and convert from HEX to DEC
    sigs = [rawSigs[i] - rawSigs[i+1] for i in range(0, len(rawSigs) - 2, 2)] + rawSigs[-2:]

    state['min'] = [min(state['min'][i], sigs[i]) for i in range(15)]
    state['max'] = [max(state['max'][i], sigs[i]) for i in range(15)]
    colors = [(sigs[i] - state['min'][i]) / (state['max'][i] - state['min'][i]) for i in range(15)]

    pc.set_array(np.array(colors[-4::-1] + colors[-3:])) # shift to adapt to actual layout
    return pc,


def draw(dataq):
    theta = np.linspace(-75, 285, 13)
    theta_intern = np.linspace(45, 405, 4)

    fig = plt.figure()
    ax = plt.axes(aspect='equal')
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)

    patches = []
    patches += [Wedge((0, 0), 1, theta[i], theta[i+1], width=0.5, color='0') for i in range(len(theta)-1)]
    patches += [Wedge((0, 0), 0.5, theta_intern[i], theta_intern[i+1], width=0.5, color='1') for i in range(len(theta_intern)-1)]

    pc = PatchCollection(patches, cmap=plt.cm.jet, animated=True)

    state = {
        'min': [0] * 15,
        'max': [1] * 15
    }

    pc.set_array(np.array([0] * 12 + [1] * 3))
    ax.add_collection(pc)
    plt.colorbar(pc, ax=ax)

    ani = FuncAnimation(fig, anim_update, fargs=(dataq, pc, state), interval=1, repeat=False, blit=True)

    plt.show()


if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyUSB0', 1500000)

    stateq = multiprocessing.Queue(1)
    nameq = multiprocessing.Queue(1)
    dataq = multiprocessing.Queue()

    datap = multiprocessing.Process(target=delayout, args=(stateq, nameq, dataq))
    drawp = multiprocessing.Process(target=draw, args=(dataq, ))
    datap.start()
    drawp.start()

    while True:
        instr = input('main: input --> ')
        print('main: ' + instr)
        if instr == 'q':
            nameq.put_nowait('lastone')
            stateq.put_nowait('e')
            time.sleep(.1)
            datap.terminate()
            drawp.terminate()
            break
        elif instr == 's':
            stateq.put_nowait(instr)
            pass
        elif instr == 'e':
            stateq.put_nowait(instr)
            pass
        else:
            nameq.put_nowait(instr)

    print('Program quit')

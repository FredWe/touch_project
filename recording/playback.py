#! /usr/bin/env python3
# -*- coding: utf-8 -*-

' playingback & plotting recorded sensor data '

__author__ = 'Fred Wei'

import sys
import plotter

INPUT_FILENAME = sys.argv[1]
INTERVAL = sys.argv[2] if len(sys.argv) > 2 else 10
"""
def anim_update(frame, patch_collection, state):
    sigs = frame
    colors = [(sigs[i] - state['min'][i]) / (state['max'][i] - state['min'][i]) for i in range(15)]

    patch_collection.set_array(
        np.array(colors[-4::-1] + colors[-3:])) # shift to adapt to actual layout
    return patch_collection,
"""
def preprocessing(data):
    """
    load data from data file and parse it
    """
    with open(INPUT_FILENAME, 'r') as file_data:
        for line in file_data:
            raw_bytes = line.split()
            #print(raw_bytes)
            if len(raw_bytes) != 63:
                continue
            raw_bytes.insert(-3, '00') # align to decode
            raw_sigs = [
                int(raw_bytes[i].zfill(2) + raw_bytes[i+1].zfill(2), 16)
                for i in range(0, len(raw_bytes), 2)]
            # concat high byte & low byte and convert from HEX to DEC
            sigs = [
                raw_sigs[i] - raw_sigs[i+1]
                for i in range(0, len(raw_sigs) - 2, 2)] + raw_sigs[-2:]
            data['sigs'].append(sigs)
            data['min'] = [min(data['min'][i], sigs[i]) for i in range(15)]
            data['max'] = [max(data['max'][i], sigs[i]) for i in range(15)]

def main():
    """
    main function
    """
    data = {
        'max': [1] * 15,
        'min': [0] * 15,
        'sigs': []
    }
    preprocessing(data)
    plter = plotter.Plotter(INTERVAL, 'static')
    plter.plot(data)
    plotter.waitforbuttonpress()
    print('Program quit')

if __name__ == '__main__':
    main()

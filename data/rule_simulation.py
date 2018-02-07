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

logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)
logging.debug(sys.argv)

# INPUT_FILENAME = sys.argv[1]

def treatline(line):
    """
    treating a sindle line of dumped datafile, return parsed data
    """
    # logging.debug(line)
    mat = re.match(r'(.+)', line)
    # logging.debug(mat)
    timer, sigsonmask = None, None
    if mat:
        # logging.debug(mat.group(1))
        rawbytes = mat.group(1).split(r' ')
        # logging.debug(rawbytes)
        timer = int(rawbytes[60], 16)
        onmask = (int(rawbytes[61], 16) << 8) | int(rawbytes[62], 16)
        # logging.debug(onmask)
        sigsonmask = [int(x) for x in format(onmask, 'b').zfill(16)][::-1]
    return timer, sigsonmask

def plot_values(data):
    fig = plt.figure()
    axes = fig.subplots(data.shape[1], sharey=True)
    for i in range(data.shape[1]):
        axes[i].plot(data[:, i], '-+')
        axes[i].set_ylabel(i)



def get_button_num():
    return 1
def click_event_intergration(event):
    pass
def inform_hush_on(state):
    state['record'] += ' hush_on'
def inform_hush_off(state):
    state['record'] += ' hush_off'
def inform_longpress(state):
    state['record'] += ' longpress'
def inform_very_longpress(state):
    state['record'] += ' very_longpress'
def inform_single_click(state):
    state['record'] += ' single_click'
def inform_double_click(state):
    state['record'] += ' double_click'
def inform_triple_click(state):
    state['record'] += ' triple_click'
def clear_button_numdata():
# void clearButtonNumData(void)
# {
# 	gTouchData->buttonNumData.buttonNumDetectFlag = 0;
# 	gTouchData->buttonNumData.cnt = 0;
# 	memset(&gTouchData->buttonNumData.num,0,sizeof(gTouchData->buttonNumData.num));
# }
    pass
def button_num_detect():
    
# static void buttonNumDetect(void)
# {
# 	if(gTouchData->buttonNumData.buttonNumDetectFlag == 0)
# 	{		
# 		gTouchData->buttonNumData.num[gTouchData->buttonNumData.cnt] = getButtonNum();
# 		gTouchData->buttonNumData.cnt++;
		
# 		if(gTouchData->buttonNumData.cnt == 2)
# 		{
# 			gTouchData->buttonNumData.cnt = 0;
# 			if(gTouchData->buttonNumData.num[0] == gTouchData->buttonNumData.num[1])
# 			{
# 				//gTouchData->buttonNumData.num[0] = 0;
# 			}
# 			else
# 			{
# 				gTouchData->buttonNumData.num[1] = BUTTON_DEFAULT;
# 			}
# 		}
# 		gTouchData->buttonNumData.buttonNumDetectFlag = 1;
# 	}	
# }
    pass
def button_num_release(state):
    state['button_num_detect_flag'] = False
def event_clear(state):
    state['event'] = ''

HUSH_PAD_CNT = 8
def could_hush(state):
    if state['sum'] >= HUSH_PAD_CNT:
        if not state['hushing_flag']:
            state['hush_delay_timer_flag'] = True
    else:
        state['hush_delay_timer'] = 0
        state['hush_delay_timer_flag'] = False
    if state['hush_delay_timer'] > 500:
        state['hushing_flag'] = True
        return True
    return False

def detect_hush(state):
    if not state['hush_detect_flag']:
        state['hush_detect_flag'] = True
        cancel_click(state)
        state['event'] = 'hush_on'
        inform_hush_on(state)

def release_hush(state):
    if state['hush_detect_flag']:
        state['hush_detect_flag'] = False
        state['hush_delay_timer'] = 0
        state['event'] = 'hush_off'
        state['hushing_flag'] = False
        inform_hush_off(state)
        event_clear(state)

def cancel_click(state):
    state['click_detect_flag'] = False
    state['internal_timer_flag']= False
    state['internal_timer']= 0
    state['multiple_timer'] = 0
    state['multiple_timer_flag'] = False
    state['click_cnt'] = 0
    state['longpress_flag'] = False
    state['very_longPress_flag'] = False

def could_click(state):
    if state['event'] != 'slider_inc' and state['event'] != 'slider_dec' and state['event'] != 'hush_on':
        return True
    return False

def detect_click(state):
    state['click_detect_flag'] = True
    state['internal_timer_flag'] = True
    state['multiple_timer_flag'] = False
    state['multiple_timer'] = 0
    button_num_detect()
    if state['internal_timer'] > 2000 and not state['longpress_flag']:
        state['longpress_flag'] = True
        state['event'] = 'longpress'
        inform_longpress(state)
        # inform_longpress(click_event_intergration('longpress'))
        clear_button_numdata()
    if state['internal_timer'] > 5000 and not state['very_longpress_flag']:
        state['very_longpress_flag'] = True
        state['event'] = 'very_longpress'
        inform_very_longpress(state)
        # inform_very_longpress(click_event_intergration('very_longpress'))
        clear_button_numdata()

def release_click(state):
    button_num_release(state)
    if state['event']  == 'longpress' or state['event']  == 'very_longpress':
        state['internal_timer_flag'] = False
        state['internal_timer'] = 0
        state['click_detect_flag'] = False
        state['longpress_flag'] = False
        state['very_longpress_flag'] = False
        clear_button_numdata()
        event_clear(state)
    if state['click_detect_flag']:
        state['click_detect_flag'] = False
        state['multiple_timer'] = 0
        state['multiple_timer_flag'] = True
        state['internal_timer'] = 0
        state['internal_timer_flag'] = False
        state['click_cnt'] += 1        
    if state['multiple_timer'] >= 300:
        state['multiple_timer'] = 0
        state['multiple_timer_flag'] = False
        if state['click_cnt'] == 1:
            state['event']  == 'single_click'
            inform_single_click(state)
            # inform_single_click(click_event_intergration('single_click'))
            clear_button_numdata()
            event_clear(state)
        elif state['click_cnt'] == 2:
            state['event']  == 'double_click'
            inform_double_click(state)
            # inform_double_click(click_event_intergration('double_click'))
            clear_button_numdata()
            event_clear(state)
        elif state['click_cnt'] == 3:
            state['event']  == 'triple_click'
            inform_triple_click(state)
            # inform_triple_click(click_event_intergration('triple_click'))
            clear_button_numdata()
            event_clear(state)
        else:
            clear_button_numdata()
        state['click_cnt'] = 0

def timer(state):
    if state['hush_delay_timer_flag']:
        state['hush_delay_timer'] += state['timer']
    if state['internal_timer_flag']:
        state['internal_timer'] += state['timer']
    if state['multiple_timer_flag']:
        state['multiple_timer'] += state['timer']

def mainloop(state):
    timer(state)
    if state['sum'] > 0:
        if could_hush(state):
            detect_hush(state)
        if could_click(state):
            detect_click(state)
    else:
        release_click(state)
        release_hush(state)
    logging.debug(state)    

def main():
    """
    main function
    """
    DATA_FILENAMES = glob.glob('*/hanson_LongPress_1_4.95.rec')
    for onef in DATA_FILENAMES:
        logging.info(onef)
        prefix = os.path.basename(onef).split('_')[1]
        if prefix.startswith('Clock') or prefix.startswith('Counter') or prefix.startswith('Slide'):
            continue

        state = {
            'timer': 0,
            'sigons': [],
            'sum': 0,
            'record': '',
            'hush_delay_timer': 0,
            'hush_detect_flag': False,
            'hush_delay_timer_flag': False,
            'internal_timer_flag': False,
            'internal_timer': 0,
            'multiple_timer_flag': False,
            'multiple_timer': 0,
            'event': '',
            'click_detect_flag': False,
            'hushing_flag': False,
            'click_cnt': 0,
            'longpress_flag': False,
            'very_longpress_flag': False}
        # Data for plotting
        data = np.zeros((1, 15))
        with open(onef, 'r') as file_data:
            for line in file_data:
                timer, sigs = treatline(line.strip())
                if not sigs:
                    continue
                logging.debug(sigs)
                state['timer'] = timer
                state['sigons'] = sigs
                state['sum'] = sum(sigs)
                data = np.append(data, [sigs[:15]], axis=0)
                mainloop(state)
            # if True:
            if state['record'].strip() != 'longpress':
                logging.warn(onef)
                logging.warn('record: %s' % state['record'])

                # plot_values(data)
                # plt.savefig('%s.png' % os.path.basename(onef))
                # plt.close()

if __name__ == '__main__':
    main()
#! /usr/bin/env python3
# -*- coding: utf-8 -*-

' recording & plotting sensor data & save them '

__author__ = 'Fred Wei'

import os
import sys
import random
import multiprocessing
import time
import logging
import serial
import json
import subprocess

import plotter

GESTURES_DICT = {
    'click': '单击',
    'double-click': '双击小鸟',
    'longpress': '长按小鸟',
    'hush': 'HUSH',
    'shorthush': '轻拍',
    'double-shorthush': '轻拍两下',
    'clockwise': '顺时针',
    'countercw': '逆时针'}
BUTTONS_DICT = {
    'button-MFB': '小鸟',
    'button-up': '[6]',
    'button-down': '[0]',
    'button-left': '[3]',
    'button-right': '[9]',
    'button-leftup': '[4]',
    'button-rightup': '[8]',
    'button-leftdown': '[2]',
    'button-rightdown': '[10]'}
PRONOUNCE_DICT = {
    'HUSH': 'HASH',
    '[10]': '[十]'}
ROUNDLEN = 12
SAMPLEN = 6
SLIDE_SAMPLEN = 2
STARTCMD = 's'
ENDCMD = 'e'
QUITCMD = 'q'
DATA_BASEDIR = 'data'
CONFIG_FILENAME = 'config_serial.json'

def serial_config(confilename):
    dat = None
    with open(confilename) as fp:
        dat = json.load(fp)
    return (dat['BAUDRATE'], dat['SERIAL_PATH'])

def checkdir(data_basedir):
    username = sys.argv[1] if len(sys.argv) > 1 else input('input tester name: ')
    user_datadir = os.path.join(data_basedir, username)
    if not os.path.exists(data_basedir):
        os.mkdir(data_basedir)
    if not os.path.exists(user_datadir):
        os.mkdir(user_datadir)
    return (username, user_datadir)

USERNAME, DATADIR = checkdir(DATA_BASEDIR)
BAUDRATE, SERIAL_PATH = serial_config(CONFIG_FILENAME)

def delayout(stateq, nameq, dataq):
    """
    control recording start / end, real-time capturing sensor data
    """
    ser = serial.Serial(SERIAL_PATH, BAUDRATE)
    state = {
        'recording': False,
        'naming': False
    }
    filedata = []
    filename = ''
    starttime = 0
    endtime = 0
    while True:
        rawline = ser.readline().strip()
        dataq.put_nowait(rawline)
        #print('delayout: ' + ret)
        #print(state)
        if not stateq.empty():
            stateqs = stateq.get_nowait()
            print('stateq get: ' + stateqs)
            if stateqs == STARTCMD:
                filedata.clear()
                filedata.append(rawline)
                starttime = time.time()
                state['recording'] = True
                state['naming'] = False
            elif stateqs == ENDCMD:
                endtime = time.time()
                state['recording'] = False
                state['naming'] = True
            print(state)

        if not nameq.empty():
            nameqs = nameq.get_nowait()
            print('nameq get')#: ' + nameqs)
            filename = nameqs
            print(state)

        if state['recording']:
            filedata.append(rawline)
        elif state['naming']:
            if not filedata:
                filename = ''
                state['recording'] = False
                state['naming'] = False
            elif filename:
                combined_filename = '%s_%.2f.rec' % (
                    os.path.join(DATADIR, filename),
                    (endtime - starttime))
                with open(combined_filename, 'w') as file_data:
                    file_data.write('\n'.join(line.decode() for line in filedata))
                print('%s lines are saved with filename as %s' % (len(filedata), combined_filename))
                filedata.clear()
                filename = ''
                starttime = 0
                endtime = 0
                state['recording'] = False
                state['naming'] = False

def slides_coco(direction, username):
    """
    generate randomly shuffled slides actions for each ROUNDLEN times SLIDE_SAMPLEN
    """
    slide_actions = []
    for rlen in range(ROUNDLEN):
        for idx_slide_sample in range(SLIDE_SAMPLEN):
            startpos = random.randrange(ROUNDLEN)
            slide_actions.append(
                '%s_%s-%s-%s_%s' % (
                    username, direction, startpos,
                    (startpos + rlen) % ROUNDLEN,
                    rlen * SLIDE_SAMPLEN + idx_slide_sample))
    random.shuffle(slide_actions)
    return slide_actions

def slides(direction, username):
    """
    generate random start-end slides actions times SAMPLEN
    """
    slide_actions = []
    for _ in range(SAMPLEN):
        startpos = random.randrange(ROUNDLEN)
        endpos = random.randrange(ROUNDLEN)
        slide_actions.append(
            '%s_%s-%s-%s' % (username, direction, startpos, endpos))
    random.shuffle(slide_actions)
    return slide_actions

def clicks(username):
    """
    generate randomly located clicks actions times SAMPLEN
    """
    click_actions = []
    for pos in BUTTONS_DICT:
        for _ in range(SAMPLEN):
            click_actions.append(
                '%s_%s-%s' % (username, 'click', pos))
    random.shuffle(click_actions)
    return click_actions

def random_insert_seq(lst, seq):
    """
    randomly insert seq into lst with keeping original order of lst
    lst changed in-place
    https://stackoverflow.com/questions/2475518/python-how-to-append-elements-to-a-list-randomly
    """
    insert_locations = random.sample(range(len(lst) + len(seq)), len(seq))
    inserts = dict(zip(insert_locations, seq))
    iter_lst = iter(lst)
    lst[:] = [
        inserts[pos]
        if pos in inserts else next(iter_lst)
        for pos in range(len(lst) + len(seq))]

def actionlist(username):
    """
    import from previous actionlist file or regenerate a new actionlist
    """
    username = username.strip()
    print('Hi, %s' % username)
    filename = '%s.actionlist' % username
    action_list = []
    if os.path.exists(filename):
        with open(filename, 'r') as file_actionlist:
            action_list = [line.strip() for line in file_actionlist]
    else:
        # add clockwise/counterCW gestures ROUNDLEN * SLIDE_SAMPLEN,
        # start position randomly generated
        clockwises = slides('clockwise', username)
        countercws = slides('countercw', username)
        singleclicks = clicks(username)
        action_list.extend(clockwises)
        action_list.extend(countercws)
        nonslides = singleclicks + [
            '%s_%s' % (username, item)
            for item in GESTURES_DICT
            if item not in ('click', 'clockwise', 'countercw')
            for i in range(SAMPLEN)]
        random.shuffle(nonslides)
        random_insert_seq(action_list, nonslides)
        action_list = ['%s_%d'% (item, ind)
            for ind, item in enumerate(action_list)]
    return action_list

def translate_by_dicts(origstr, *manydicts):
    """
    return replaced string by many dicts
    """
    newstr = origstr
    for onedict in manydicts:
        logging.debug(onedict)
        for origword in sorted(onedict.keys(), key=len, reverse=True):
            newstr = newstr.replace(origword, onedict[origword])
    return newstr

def pronounce(str):
    cmdstr = "spd-say -i +100 -r +30 -l 'zh' -t 'female1' '%s'" % str
    proc = subprocess.Popen(cmdstr, shell=True)

def main():
    """
    main function
    """
    logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)
    state_queue = multiprocessing.Queue(1)
    name_queue = multiprocessing.Queue(1)
    data_queue = multiprocessing.Queue()

    plter = plotter.Plotter(1, 'queue')

    data_process = multiprocessing.Process(
        target=delayout, args=(state_queue, name_queue, data_queue))
    draw_process = multiprocessing.Process(
        target=plter.plot, args=({'queue': data_queue}, ))
    data_process.start()
    draw_process.start()

    actions = actionlist(USERNAME)
    #print(actions)

    instr = ''
    idx = None
    for idx, val in enumerate(actions):
        actstr = translate_by_dicts(val.split('_')[1], GESTURES_DICT, BUTTONS_DICT)
        pronounce_str = translate_by_dicts(actstr, PRONOUNCE_DICT)
        logging.debug(pronounce_str)
        pronounce(pronounce_str)
        print(
            '[!] 按 %s <Enter> 之后, 请做以下动作: [\033[30;103m %s \033[0m]' %
            (STARTCMD, actstr))
        print(
            '[-] 做完动作之后，按 %s <Enter> 保存。按 %s <Enter> 退出' %
            (ENDCMD, QUITCMD))
        while True:
            instr = input('main: input --> ')
            print('main: ' + instr)
            if instr == QUITCMD:
                break
            elif instr == STARTCMD:
                state_queue.put_nowait(instr)
            elif instr == ENDCMD:
                name_queue.put_nowait(val)
                state_queue.put_nowait(instr)
                break
            else:
                #nameq.put_nowait(instr)
                pass

        if instr == QUITCMD: # let QUITCMD break to the most outer loop
            break

        time.sleep(.1) # add a delay to make display in more natural order

    with open('%s.actionlist' % USERNAME, 'w') as file_actionlist:
        if instr == QUITCMD:
            file_actionlist.write('\n'.join(actions[idx:]))

    data_process.terminate()
    draw_process.terminate()
    print('退出')

if __name__ == '__main__':
    main()

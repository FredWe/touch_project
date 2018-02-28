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
import json
import subprocess
import termios
import tty
import serial

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
    'HUSH': 'ha4shi',
    '10': '十',
    '11': '十一',
    '12': '十二',
    ']-[': '到',
    '逆时针': 'ni4时针'}
ROUNDLEN = 12
SAMPLEN = 10
SLIDE_SAMPLEN = 2
STARTKEY = 's'
ENDKEY = 'e'
QUITKEY = 'q'
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
    loginstants = []
    while True:
        rawline = ser.readline().strip()
        dataq.put_nowait(rawline)
        logging.debug(state)
        if not stateq.empty():
            stateqs = stateq.get_nowait()
            logging.info('stateq get: ' + stateqs)
            if stateqs == STARTKEY:
                filedata.clear()
                filedata.append(rawline)
                starttime = time.time()
                loginstants.clear()
                loginstants.append(time.time())
                state['recording'] = True
                state['naming'] = False
            elif stateqs == ENDKEY:
                endtime = time.time()
                state['recording'] = False
                state['naming'] = True
            logging.info(state)

        if not nameq.empty():
            nameqs = nameq.get_nowait()
            logging.info('nameq get')#: ' + nameqs)
            filename = nameqs
            logging.info(state)

        if state['recording']:
            filedata.append(rawline)
            loginstants.append(time.time())
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
                # with open(combined_filename.replace('.rec', '.log'), 'w') as file_data:
                #     file_data.write('\n'.join(str(ins) for ins in loginstants))
                print('%s lines are saved with filename as %s' % (len(filedata), combined_filename))
                filedata.clear()
                loginstants.clear()
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
            '%s_%s-[%s]-[%s]' % (username, direction, startpos, endpos))
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

def pronounce(instr):
    cmdstr = "spd-say -r +20 -l 'zh' '%s'" % instr
    _ = subprocess.Popen(cmdstr, shell=True)

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main():
    """
    main function
    """
    logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.WARN)
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

    inkey = ''
    idx = None
    for idx, val in enumerate(actions):
        actstr = translate_by_dicts(val.split('_')[1], GESTURES_DICT, BUTTONS_DICT)
        pronounce_str = translate_by_dicts(actstr, PRONOUNCE_DICT)
        logging.debug(pronounce_str)
        pronounce(pronounce_str)
        print(
            '[!] 按 %s 之后, 请做以下动作: [\033[30;103m %s \033[0m]' %
            (STARTKEY, actstr))
        print(
            '[-] 做完动作之后，按 %s 保存。按 %s 退出' %
            (ENDKEY, QUITKEY))
        print('main: input --> ', end='')
        sys.stdout.flush()
        while True:
            inkey = getch()
            print(inkey)
            print('main: input --> ', end='')
            sys.stdout.flush()
            logging.info('main: ' + inkey)
            if inkey == QUITKEY:
                break
            elif inkey == STARTKEY:
                state_queue.put_nowait(inkey)
            elif inkey == ENDKEY:
                name_queue.put_nowait(val)
                state_queue.put_nowait(inkey)
                break

        if inkey == QUITKEY: # let QUITKEY break to the most outer loop
            break

        time.sleep(.1) # add a delay to make display in more natural order

    with open('%s.actionlist' % USERNAME, 'w') as file_actionlist:
        if inkey == QUITKEY:
            file_actionlist.write('\n'.join(actions[idx:]))

    data_process.terminate()
    draw_process.terminate()
    print('退出')

if __name__ == '__main__':
    main()

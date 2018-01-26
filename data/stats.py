import os.path
import glob

DATA_FILENAMES = glob.glob('*/*.rec')
cnt = {
    'click1': 0,
    'click2': 0,
    'click3': 0,
    'hush': 0,
    'longpress': 0,
    'clockwise1': 0,
    'clockwise2': 0,
    'clockwise3': 0,
    'clockwise4': 0,
    'clockwise5': 0,
    'clockwise6': 0,
    'clockwise7': 0,
    'clockwise8': 0,
    'clockwise9': 0,
    'clockwise10': 0,
    'clockwise11': 0,
    'clockwise12': 0,
    'counterclockwise1': 0,
    'counterclockwise2': 0,
    'counterclockwise3': 0,
    'counterclockwise4': 0,
    'counterclockwise5': 0,
    'counterclockwise6': 0,
    'counterclockwise7': 0,
    'counterclockwise8': 0,
    'counterclockwise9': 0,
    'counterclockwise10': 0,
    'counterclockwise11': 0,
    'counterclockwise12': 0}

for onef in DATA_FILENAMES:
    #print(onef)
    bsname_arr = os.path.splitext(os.path.basename(onef))[0].split('_')
    a = bsname_arr[1].split('-')
    """
    if bsname_arr[0] == 'fred':
        continue
    """
    if a[0] == 'Click':
        if int(a[1]) < 1 or int(a[1]) > 3:
            print('click abnormal', a)
        else:
            cnt['click%s' % a[1]] += 2
    elif a[0] == 'Hush':
        cnt['hush'] += 2
    elif a[0] == 'LongPress':
        cnt['longpress'] += 2
    elif a[0] == 'Slide':
        if len(a) < 3:
            print(a)
        start = int(a[2])
        end = int(a[3])
        delta = 0
        if a[1] == 'Clockwise':
            delta = (int(end) - int(start)) % 12
        elif a[1] == 'CounterClockwise':
            delta = (int(start) - int(end)) % 12
        else:
            print('unknown action', a)
        delta = 12 if not delta else delta
        #cnt['%s%s' % (str.lower(a[1]), delta)] += 12
        cnt['%s%s' % ('clockwise', delta)] += 12
        cnt['%s%s' % ('counterclockwise', delta)] += 12
    else:
        print('unknown action', a)

print(cnt)


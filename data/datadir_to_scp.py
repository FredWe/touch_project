import glob
import logging
import argparse
import os

def path2uttid(path):
    PRE1, PRE2 = '[', ']'
    parr = os.path.basename(path.replace(PRE1, '').replace(PRE2, '')).split('_')
    return '_'.join(parr[:len(parr) - 1])

def main():
    logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.WARN)
    parser = argparse.ArgumentParser(
        description="find all .rec rawfile from argument DATAPATH, \
            and convert all .rec path to scp file in SCPPATH")
    parser.add_argument("DATAPATH", help="data file path")
    parser.add_argument("SCPPATH", help="scp file path")
    args = parser.parse_args()
    logging.debug(args)
    SCP_FILEPATH = args.SCPPATH
    DATA_FILEPATH = args.DATAPATH
    if not SCP_FILEPATH.endswith('.scp'):
        raise ValueError('extension error')
    logging.debug(SCP_FILEPATH)
    recfiles = glob.glob(os.path.join(DATA_FILEPATH, '**', '*.rec'), recursive=True)
    for filepath in recfiles:
        if ' ' in filepath:
            raise ValueError('%s\nthis filepath contains space' % filepath)
    scps = (
        '%s %s' % (path2uttid(filepath), filepath)
        for filepath in recfiles
        if os.path.getsize(filepath) > 0) # non-empty files
    with open(SCP_FILEPATH, 'w') as fd:
        fd.write('\n'.join(scps))

if __name__ == '__main__':
    main()

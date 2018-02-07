import glob
import logging
import argparse
import os

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
        logging.error('extension error')
        exit()
    logging.debug(SCP_FILEPATH)
    recfiles = glob.glob(os.path.join(DATA_FILEPATH, '**', '*.rec'), recursive=True)
    parr = lambda path: os.path.basename(path).split('_')
    path2uttid = lambda path: '_'.join(parr(path)[:len(parr(path)) - 1])
    scps = ('%s %s' % (path2uttid(filepath), filepath) for filepath in recfiles)
    with open(SCP_FILEPATH, 'w') as fd:
        fd.write('\n'.join(scps))

if __name__ == '__main__':
    main()

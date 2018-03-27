import io_helper
import logging
import sys
import subprocess
import os

IMAGEDIR = ''
SCPPATH = ''
UTTID = sys.argv[1]

def main():
    utt2recpath = io_helper.parse_dictfile(SCPPATH)
    recpath = utt2recpath[UTTID]
    imagename = io_helper.path2uttid(recpath)
    imagepath = os.path.join(IMAGEDIR, '%s.png' % imagename)
    subprocess.run('eog %s' % imagepath, shell=True)

if __name__ == '__main__':
    logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)
    main()
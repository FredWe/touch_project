import io_helper
import plot_helper
import sys
import numpy as np
import data_helper
import logging

def main():
    arkmat = io_helper.parsefile_ark2mat(sys.argv[1])
    datum = list(arkmat.values())
    alldata = np.concatenate(datum, axis=0)
    logging.info('std:\n%s' % np.std(alldata, axis=0))
    logging.info('mean:\n%s' % np.mean(alldata, axis=0))
    filt_datad = data_helper.normalize(arkmat)
    logging.debug(filt_datad)
    filt_datum = list(filt_datad.values())
    filt_alldata = np.concatenate(filt_datum, axis=0)
    logging.debug(filt_alldata)
    plot_helper.hist_values(filt_alldata)

if __name__ == '__main__':
    logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)
    main()
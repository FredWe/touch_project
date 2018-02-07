import io_helper
import plot_helper
import sys
import numpy as np

def main():
    arkmat = io_helper.parsefile_ark2mat(sys.argv[1])
    datum = list(arkmat.values())
    alldata = np.concatenate(datum, axis=0)
    plot_helper.hist_values(alldata)

if __name__ == '__main__':
    main()
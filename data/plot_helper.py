import matplotlib.pyplot as plt

NPAD = 15
def hist_values(data):
    fig = plt.figure()
    axes = fig.subplots(NPAD, sharex=True)
    for i in range(NPAD):
        #fig = plt.figure()
        axes[i].hist(data[:, i], bins=512, log=True)
        axes[i].set_ylabel(i)
    plt.show()#block=False)
import kaldi_io
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
import common

def plotdata_bykey(data, key, flag_decode):
    alignment = common.decode_alignment if flag_decode else common.alignment
    transid2info = common.transid2info()
    pdfid2info = common.pdfid2info()
    NPAD = 15
    fig = plt.figure(figsize=(24, 13.5))
    axes = fig.subplots(NPAD, sharey=True)
    for i in range(NPAD):
        axes[i].plot(data[key][:, i], '-+')
        axes[i].set_ylabel(i)
    axes[0].set_title(key + (' DECODE' if flag_decode else ''))
    
    phone2short = {'shortmid': 'm', 'SIL': 'S', 'all': 'a'}
    stt = 1 # for True
    for ind, it in enumerate(alignment[key]):
        currstt = int(transid2info[it]['hmmstate'])
        if currstt - stt != 0:
            for i_pad in range(NPAD):
                axes[i_pad].annotate(
                    phone2short[transid2info[it]['phone']] + transid2info[it]['hmmstate'],
                    xy=(ind, data[key][:, i_pad][ind]), xytext=(ind, data[key][:, i_pad][ind] + 0.1), arrowprops=dict(arrowstyle='->'))
        stt = currstt

def plot_ali(key, flag_decode):
    alignment = common.decode_alignment if flag_decode else common.alignment
    transid2info = common.transid2info()
    pdfid2info = common.pdfid2info()
    # for k, v in sorted(common.alignment.items()):
    #     print(k)
    #     print(' '.join([
    #         transid2info[it]['phone'] + transid2info[it]['hmmstate']# + transid2info[it]['transtext']
    #         for it in v]))

    # print(common.numpdfs())
    # print(pdfid2info)

    feats = {k: m for k, m in kaldi_io.read_mat_ark('../feats/feats_train.ark')}

    plotdata_bykey(feats, key, flag_decode)

    print(' '.join([
        transid2info[it]['phone'] + transid2info[it]['hmmstate']# + transid2info[it]['transtext']
        for it in alignment[key]]))

if __name__ == '__main__':
    IS_DECODE = False # True # 
    feats = {k: m for k, m in kaldi_io.read_mat_ark('../feats/feats_train.ark')}
    keey = list(feats.keys())[0]
    #keey = 'Click3_14717'
    plot_ali(keey, IS_DECODE)
    IS_DECODE = True
    plot_ali(keey, IS_DECODE)
    plt.show()


# >>> ll = plt.plot_ali(x,y)
# >>> xl = plt.xlabel('horizontal axis')
# >>> yl = plt.ylabel('vertical axis')
# >>> ttl = plt.title('sine function')
# >>> ax = plt.axis([-2, 12, -1.5, 1.5])
# >>> grd = plt.grid(True)
# >>> txt = plt.text(0,1.3,'here is some text')
# >>> ann = plt.annotate('a point on curve',xy=(4.7,-1),xytext=(3,-1.3), arrowprops=dict(arrowstyle='->'))
# >>> plt.show()
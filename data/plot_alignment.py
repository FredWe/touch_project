import kaldi_io
import numpy as np
import matplotlib.pyplot as plt
import kaldi_helper
import logging
import argparse

KALDI_DIR = '~/Documents/kaldi'
MDL_PATH = 'temp/40.mdl'
ALIGZ_PATH = 'temp/ali.1.gz'
PHONES_PATH = 'temp/phones.txt'
ARK_PATH = 'temp/feats_train.ark'

def plot_alignment_bykey(data, key, alignment, transid2info):
    NPAD = 15
    fig = plt.figure(figsize=(16, 12))
    fig.subplots_adjust(hspace=0)
    axes = fig.subplots(NPAD, sharey=True)
    for i in range(NPAD):
        axes[i].plot(data[key][:, i], '-+')
        axes[i].set_ylabel(i)
    
    prevphone, prevstate = '', 0
    for ind, it in enumerate(alignment[key]):
        info = transid2info[it]
        currphone, currstate = info['phone'], int(info['hmmstate'])
        if currphone != prevphone or currstate != prevstate:
            for i_pad in range(NPAD):
                if prevphone != '' and currphone != prevphone:
                    axes[i_pad].axvline(ind - 0.5, color='r', linestyle='dashed')
                elif currstate != prevstate:
                    axes[i_pad].axvline(ind - 0.5, color='y', linestyle='dashed')
            axes[0].annotate(
                info['phone'] + info['hmmstate'],
                rotation=90, xy=(ind, data[key][:, 0][ind]), va='bottom',)
        prevphone, prevstate = currphone, currstate
    plt.show()

def plot_ali(key, feats):
    alignment = kaldi_helper.alignment()
    transid2info = kaldi_helper.transid2info()
    for k, v in sorted(kaldi_helper.alignment().items()):
        logging.debug(k)
        logging.debug(' '.join([
            transid2info[it]['phone'] + transid2info[it]['hmmstate']# + transid2info[it]['transtext']
            for it in v]))

    plot_alignment_bykey(feats, key, alignment, transid2info)

    logging.debug(' '.join([
        transid2info[it]['phone'] + transid2info[it]['hmmstate']# + transid2info[it]['transtext']
        for it in alignment[key]]))

if __name__ == '__main__':
    plt.rcParams['axes.formatter.useoffset'] = False
    logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.WARN)
    parser = argparse.ArgumentParser(description="plot alignment by utterance id")
    parser.add_argument("UTTERANCE_ID", help="utterance id")
    args = parser.parse_args()
    logging.debug(args)
    UTTID = args.UTTERANCE_ID
    kaldi_helper.basicConfig(**{
        'kaldi_dir': KALDI_DIR,
        'mdl_path': MDL_PATH,
        'aligz_path': ALIGZ_PATH,
        'phones_path': PHONES_PATH,
        'ark_path': ARK_PATH,
    })
    feats = {k: m for k, m in kaldi_io.read_mat_ark(ARK_PATH)}
    plot_ali(UTTID, feats)

import os
import plotali
import matplotlib.pyplot as plt

base_path = '../exp/mono0a/decode_train_touch'

with open(os.path.join(base_path, 'scoring_kaldi/best_wer')) as f:
    params = f.readline().strip().split('_')
    print(params)
    lmwt, wip = params[-2], params[-1]

with open(os.path.join(base_path, 'wer_%s_%s' % (lmwt, wip))) as f:
    print('')
    for line in f:
        print(line.strip())

with open(os.path.join(base_path, 'scoring_kaldi/wer_details/ops')) as f:
    print('')
    for line in f:
        print(line.strip())

with open(os.path.join(base_path, 'scoring_kaldi/penalty_%s/%s.txt' % (wip, lmwt))) as f:
    print('')
    for line in f:
        params = line.strip().split()
        if len(params) != 2 or params[0].split('_')[0] != params[1]:
            print(line.strip())
            
            IS_DECODE = False
            plotali.plot_ali(params[0], IS_DECODE)
            plt.savefig('%s_ali.png' % params[0])
            IS_DECODE = True
            plotali.plot_ali(params[0], IS_DECODE)
            plt.savefig('%s_ali_decode.png' % params[0])
            

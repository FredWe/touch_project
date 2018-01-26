PROJECTDIR = '/home/fredwei/Documents/kaldi/egs/touch-project'
TRAINDIR = '%s/s5/data/train_touch' % PROJECTDIR
TESTDIR = '%s/s5/data/test_touch' % PROJECTDIR

def text(directory, ids):
    with open('%s/text' % directory, 'w') as f:
        f.write('\n'.join(
            '%s %s' % (uid, uid.split('_')[0]) for uid in ids))

def spk2utt(directory, ids):
    with open('%s/spk2utt' % directory, 'w') as f:
        f.write('global ')
        f.write(' '.join(ids))

def utt2spk(directory, ids):
    with open('%s/utt2spk' % directory, 'w') as f:
        f.write('\n'.join('%s global' % uid for uid in ids))

def main():
    for d in (TRAINDIR, TESTDIR):
        with open('%s/feats.scp' % d, 'r') as f:
            ids = [line.strip().split(' ')[0] for line in f]
            #print(d, ids)
            spk2utt(d, ids)
            utt2spk(d, ids)
            text(d, ids)

if __name__ == '__main__':
    main()

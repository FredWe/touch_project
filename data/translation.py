import kaldi_helper

KALDI_DIR = '~/Documents/kaldi'
MDL_PATH = 'temp/40.mdl'
ALIGZ_PATH = 'temp/ali.1.gz'
PHONES_PATH = 'temp/phones.txt'
ARK_PATH = 'temp/feats_train.ark'

if __name__ == '__main__':
    kaldi_helper.basicConfig(**{
        'kaldi_dir': KALDI_DIR,
        'mdl_path': MDL_PATH,
        'aligz_path': ALIGZ_PATH,
        'phones_path': PHONES_PATH,
        'ark_path': ARK_PATH,
    })
    transid2info = kaldi_helper.transid2info()
    pdfid2info = kaldi_helper.pdfid2info()

    for k, v in sorted(kaldi_helper.alignment().items()):
        print(k)
        print(' '.join([
            transid2info[it]['phone'] + transid2info[it]['hmmstate']# + transid2info[it]['transtext']
            for it in v]))

    pdfid2count = {k: 0 for k in pdfid2info.keys()}
    print(kaldi_helper.numpdfs())
    print(pdfid2info)

    for v in kaldi_helper.alignment().values():
        for transid in v:
            thispdfid = int(transid2info[transid]['pdfid'])
            pdfid2count[thispdfid] += 1
    print(pdfid2count)
    for k, v in pdfid2count.items():
        print(pdfid2info[k])
        # print(v)

    phone2framenum = {it['phone']: 0 for it in pdfid2info.values()}
    for k, v in pdfid2count.items():
        phone2framenum[pdfid2info[k]['phone']] += v
    print(phone2framenum)
    
    for k, v in pdfid2count.items():
        print(pdfid2info[k])
        # print('%.3f%%' % (v / phone2framenum[pdfid2info[k]['phone']] * 100))



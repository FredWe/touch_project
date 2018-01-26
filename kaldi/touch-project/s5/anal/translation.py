import common

if __name__ == '__main__':
    transid2info = common.transid2info()
    pdfid2info = common.pdfid2info()

    for k, v in sorted(common.alignment.items()):
        print(k)
        print(' '.join([
            transid2info[it]['phone'] + transid2info[it]['hmmstate']# + transid2info[it]['transtext']
            for it in v]))

    pdfid2count = {k: 0 for k in pdfid2info.keys()}
    print(common.numpdfs())
    print(pdfid2info)

    for v in common.alignment.values():
        for transid in v:
            thispdfid = int(transid2info[transid]['pdfid'])
            pdfid2count[thispdfid] += 1
    print(pdfid2count)
    for k, v in pdfid2count.items():
        print(pdfid2info[k])
        print(v)

    phone2framenum = {it['phone']: 0 for it in pdfid2info.values()}
    for k, v in pdfid2count.items():
        phone2framenum[pdfid2info[k]['phone']] += v
    print(phone2framenum)

    for k, v in pdfid2count.items():
        print(pdfid2info[k])
        print('%.3f%%' % (v / phone2framenum[pdfid2info[k]['phone']] * 100))



def ngramsout(gesseq):
    geslines = sorted({'-1 %s' % ges[0] for ges in gesseq if ges[0] != '<SIL>'})
    geslines.extend(['-99 <s>', '-1 </s>'])
    with open('task.arpabo', 'w') as f:
        f.write('\\data\\\n')
        f.write('ngram 1=%d\n' % len(geslines))
        f.write('\n\\1-grams:\n\n')
        f.write('\n'.join(geslines))
        f.write('\n\n\\end\\\n')

def phonesout(gesseq):
    phoneset = sorted({p for ges in gesseq for p in ges[1:]})
    with open('phones.txt', 'w') as f:
        f.write('\n'.join(phoneset))

def lexiconout(gesseq):
    with open('lexicon.txt', 'w') as f:
        f.write('\n'.join(' '.join(ges) for ges in gesseq))
        f.write('\n')
    with open('lexicon_nosil.txt', 'w') as f:
        f.write('\n'.join(
            ' '.join(ges)
            for ges in gesseq
            if ges[0] != '<SIL>'))
        f.write('\n')

def generateall():
    gesseq = [
        ('<SIL>', 'SIL'),
        ('LongPress', 'longmid'),
        ('Hush', 'all')]
    for n in range(1, 4):
        gesseq.append((
            'Click%d' % n,
            *['shortmid' for i in range(n)]))
    for slen in range(1, 13):
        for start in range(12):
            gesseq.append((
                'Clockwise%d' % slen, *[
                    'short%d' % ((start + i) % 12)
                    for i in range(slen + 1)]))
            gesseq.append((
                'CounterClockwise%d' % slen, *[
                    'short%d' % ((start - i) % 12)
                    for i in range(slen + 1)]))
    return gesseq

def main():
    gesseq = generateall()
    filter_field = ('<SIL>', 'Hush', 'Click1', 'Click2', 'Click3', 'LongPress')
    ex_field = ('LongPress')
    #gesseq = [ges for ges in gesseq if ges[0] in filter_field]
    #gesseq = [ges for ges in gesseq if ges[0] not in ex_field]
    lexiconout(gesseq)
    phonesout(gesseq)
    ngramsout(gesseq)

if __name__ == '__main__':
    main()

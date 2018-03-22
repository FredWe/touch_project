import logging
import argparse
import collections

def main():
    parser = argparse.ArgumentParser(description="stats sentence error rate by 3 threshold")
    parser.add_argument("FILEPATH", help="per_utt file path")
    parser.add_argument("INS_THRESHOLD", help="insertion count threshold")
    parser.add_argument("DEL_THRESHOLD", help="deletion count threshold")
    parser.add_argument("SUB_THRESHOLD", help="substitution count threshold")
    args = parser.parse_args()
    logging.debug(args)
    FILEPATH = args.FILEPATH
    THRESHOLD = {
        'ins': int(args.INS_THRESHOLD),
        'del': int(args.DEL_THRESHOLD),
        'sub': int(args.SUB_THRESHOLD)        
    }
    count = dict.fromkeys(['total', 'wrong', 'ins', 'del', 'sub'], 0)
    trans = {
        'I': 'ins',
        'D': 'del',
        'S': 'sub'
    }
    with open(FILEPATH, 'r') as file_data:
        for line in file_data:
            arr = line.strip().split()
            if arr[1] == 'op':
                count['total'] += 1
                counter = collections.Counter(arr[2:])
                logging.debug(counter)
                wrong_flag = False
                for abbv, key in trans.items():
                    if counter[abbv] > THRESHOLD[key]:
                        count[key] += 1
                        wrong_flag = True
                if wrong_flag:
                    count['wrong'] += 1
    print(count)
    print('%.2f%%' % (count['wrong'] / count['total'] * 100))

if __name__ == '__main__':
    logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.WARN)
    main()

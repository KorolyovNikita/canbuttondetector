from itertools import groupby
from collections import deque, Counter
import argparse
import re

from bitmask import BitMask
from printanswer import printAnswer


class MessegeGroup:
    def __init__(self, ID):
        self.ID = ID
        self.data = []
        self.timeline = []

    def __len__(self):
        return len(self.data)

    def add(self, byte_n, msg, period):
        self.byte_n = (0 if self.data and self.byte_n != byte_n
                       else byte_n)
        self.data.append(msg)
        self.timeline.append(period)

    def byteIterator(self):
        for n in range(self.byte_n):
            yield n, tuple(msg[n] for msg in self.data)


class Button:
    def __init__(self, args):
        sequence = re.findall(r'\b[01]+', args.input_file)
        assert sequence, 'invalid file name'
        sequence = Counter(sequence[-1])

        self.fix = True if len(sequence) == 2 else False
        self.count = sequence['1']
        self.timeout = args.t if args.t > -1 else 1000 if self.fix else 500

    def checkFront(self, i, timeline, gr):
        timeline.append(next(gr)[1])
        durations = i and timeline[-1] - timeline[-2] < self.timeout

        return durations if self.fix else i % 2 and (tuple(gr) or durations)


def get_args():
    arg_parser = argparse.ArgumentParser(description='Hello Author!')
    arg_parser.add_argument('input_file')
    arg_parser.add_argument('-t', metavar='--timeout',
                            type=int, default=-1,
                            help='delay between clicks. \
Default: 1000ms for fix, 500ms for moment')
    return arg_parser.parse_args()


def parse_log(filepath):
    log = {}
    with open(filepath, 'r') as file:
        file.readline()
        for line in file:
            line = line.split()

            ID = int(line[3], 16)
            byte_n = int(line[4])
            msg = list(map(lambda x: int(x, 16), line[5:-1]))
            period = int(line[-1])

            if ID not in log:
                log[ID] = MessegeGroup(ID)
            log[ID].add(byte_n, msg, period)
    return log


def findButton(msgGroup, button):
    result = []
    for n, data in msgGroup.byteIterator():
        mask_queue = deque([BitMask(0xFF)])

        while(mask_queue):
            mask = mask_queue.popleft()
            values = [val & mask.get() for val in data]

            timeline, pair = [], deque(maxlen=2)
            for i, gr in enumerate(groupby(zip(values, msgGroup.timeline),
                                           lambda x: x[0])):
                val = gr[0]
                if i > 1 and val not in pair:
                    mask_queue.extend(mask.split())
                    break
                pair.appendleft(val)

                if button.checkFront(i, timeline, gr[1]):
                    break
            else:
                if i == button.count * 2:
                    result.append((msgGroup.ID, mask.get(), n, pair, timeline))
    return result


def main():
    args = get_args()
    log = parse_log(args.input_file)
    button = Button(args)

    candidates = []
    for ID, group in log.items():
        candidates.extend(findButton(group, button))

    printAnswer(candidates)


if __name__ == "__main__":
    main()

from itertools import groupby, cycle
from collections import deque
import argparse
import re

from bitmask import BitMask
from printanswer import printAnswer


def get_args():
    arg_parser = argparse.ArgumentParser(description='Hello Author!')
    arg_parser.add_argument('input_file')
    arg_parser.add_argument('-t', metavar='--timeout',
                            type=int, default=(700, 100), nargs=2,
                            help='Default: for low 700ms, for high 100ms')
    return arg_parser.parse_args()


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


def findButton(msgGroup, sequence_len, timeout):
    if len(msgGroup) < sequence_len:
        return

    for byte_n in range(msgGroup.byte_n):
        mask_queue = deque([BitMask(0xFF)])

        while(mask_queue):
            mask = mask_queue.popleft()
            values = (msg[byte_n] & mask.get() for msg in msgGroup.data)

            timeline = []
            pair = deque(maxlen=2)

            for i, gr in enumerate(groupby(zip(values, msgGroup.timeline),
                                           lambda x: x[0]), start=1):
                val, period = next(gr[1])

                if i > 2 and val not in pair:
                    mask_queue.extend(mask.split())
                    break

                pair.appendleft(val)
                timeline.append(period)
            else:
                check_timeout = map(lambda prev, curr, t: (curr - prev) > t,
                                    timeline, timeline[1:],
                                    cycle(timeout))

                if i == sequence_len and all(check_timeout):
                    yield msgGroup.ID, mask.get(), byte_n, pair, timeline


def main():
    args = get_args()
    log = parse_log(args.input_file)

    sequence = re.findall(r'\b[01]+', args.input_file)[-1]
    assert sequence, 'invalid file name'

    sequence_len = (len(sequence)
                    if '0' in sequence
                    else len(sequence) * 2 + 1)

    candidates = []
    for ID, group in log.items():
        candidates.extend(findButton(group, sequence_len, args.t))

    printAnswer(candidates)


if __name__ == "__main__":
    main()

from prettytable import PrettyTable
from itertools import cycle, islice


def printAnswer(candidates):
    if not candidates:
        print('Not found')
        return

    table = PrettyTable()
    table.field_names = ['id', 'N байта', 'Маска', 'Рав-во',
                         'Значение', 'Статус', 'Интервалы (мс)']
    for c in candidates:
        ID, mask, byte_n, pair, timeline = c
        release, press = pair

        val = max(release, press)
        byte_n = f'd{byte_n}'

        equality = ['==', '!=']
        if press < release:
            equality.reverse()
        status = ['"активно"', '"неактивно"']

        maxlen = len(str(timeline[-1]))
        maxlen = maxlen if maxlen > 5 else 5
        timeline = [' '.join('0x{:<{}X}'.format(i, maxlen - 2)
                    for i in islice(cycle((release, press)),
                                    len(timeline))),
                    ' '.join('{:<{}}'.format(t, maxlen) for t in timeline)]

        for i in range(2):
            table.add_row([f'0x{ID:X}', byte_n, f'0x{mask:X}', equality[i],
                           f'0x{val:X}', status[i], timeline[i]])
        table.add_row([''] * 7)
    table.del_row(-1)

    print(table)

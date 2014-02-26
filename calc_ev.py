import collections
import csv
import os

BulkValue = collections.namedtuple('BulkValue', ['cutoff', 'value'])

BULK_VALUES = {
    'L': BulkValue(0.5, 0.00),
    'FL': BulkValue(0.5, 0.05),
    'C': BulkValue(0.5, 0.001),
    'FC': BulkValue(0.5, 0.05),
    'U': BulkValue(0.5, 0.001),
    'FU': BulkValue(0.5, 0.05),
    'R': BulkValue(1.0, 0.10),
    'FR': BulkValue(1.0, 0.20),
    'M': BulkValue(1.0, 0.20),
    'FM': BulkValue(1.0, 1.00),
}

DEFAULT_FOIL_MULTIPLIER = 2.0

DATA_DIR = os.path.join('.', 'data')
SETS_FILENAME = os.path.join(DATA_DIR, 'sets.csv')


def cell_to_float(cell_string):
    if '/' in cell_string:
        n, d = cell_string.split('/')
    else:
        n, d = cell_string, '1'
    return float(n) / float(d)


def parse_pack_distributions():
    sets_data = {}
    with open(SETS_FILENAME, 'rb') as sets_datafile:
        sets_reader = csv.DictReader(sets_datafile)
        for row in sets_reader:
            set_name = row.pop('Set')
            set = collections.defaultdict(lambda: 0.0)
            foil_multiplier = cell_to_float(row.pop('F', 0.0))
            for rarity, frequency in row.items():
                frequency = cell_to_float(frequency)
                set[rarity] = frequency
                set['F%s' % rarity] = foil_multiplier * frequency
            sets_data[set_name] = set
    return sets_data


def price_or_bulk(rarity, price):
    if rarity not in BULK_VALUES:
        return price
    bulkvalue = BULK_VALUES[rarity]
    if price < bulkvalue.cutoff:
        return bulkvalue.value
    else:
        return price


def parse_set_data(set_code):
    set_filename = os.path.join(DATA_DIR, '%s.csv' % set_code)
    if not os.path.exists(set_filename):
        return collections.defaultdict(lambda: 0.0)
    counts = collections.defaultdict(lambda: 0)
    sums = collections.defaultdict(lambda: 0.0)
    with open(set_filename, 'rb') as set_datafile:
        set_reader = csv.DictReader(set_datafile)
        for row in set_reader:
            rarity = row['Rarity'].strip()
            frarity = 'F%s' % rarity

            price = float(row['Mid'].strip().replace('$', ''))
            if 'Foil Mid' in row:
                fprice = float(row['Foil Mid'].strip().replace('$', ''))
            elif 'Foil' in row:
                fprice = float(row['Foil'].strip().replace('$', ''))
            else:
                fprice = DEFAULT_FOIL_MULTIPLIER * price

            counts[rarity] += 1
            counts[frarity] += 1
            sums[rarity] += price_or_bulk(rarity, price)
            sums[frarity] += price_or_bulk(frarity, fprice)
    averages = collections.defaultdict(lambda: 0.0)
    for rarity, sum in sums.items():
        averages[rarity] = sum / float(counts[rarity])
    return averages


def get_pack_ev(set_distribution, set_averages):
    sum = 0.0
    for rarity, frequency in set_distribution.items():
        sum += frequency * set_averages[rarity]
    return sum


def main():
    set_distributions = parse_pack_distributions()
    set_averages = {
            set_code: parse_set_data(set_code) for set_code in set_distributions}
    pack_evs = {}
    for set_code, set_distribution in set_distributions.items():
        set_average = parse_set_data(set_code)
        pack_evs[set_code] = get_pack_ev(set_distribution, set_average)

    print 'Pack values'
    for set_code, ev in pack_evs.items():
        print ' > %s - $%0.2f' % (set_code, ev)


if __name__ == '__main__':
        main()

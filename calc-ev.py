import csv
from decimal import Decimal


NUMBER_BOXES = 6
NUMBER_PACKS = NUMBER_BOXES*36
BULK_LOT_PRICE = 25.00

def _default_dict():
    return {'C': 0, 'U': 0, 'R': 0, 'M': 0,}

def main():
    r = csv.reader(open('theros-tcg.csv', 'rb'), delimiter=';')
    r.next()
    total_price = _default_dict()
    total_foil_price = 0
    set_count = _default_dict()
    average_price = _default_dict()

    for row in r:
        rarity = row[4].strip()
        if rarity in total_price:
            total_price[rarity] += Decimal(row[6].strip()[1:])
            total_foil_price += Decimal(row[6].strip()[1:]) * Decimal(2.25)
            set_count[rarity] += 1

    for k,v in total_price.iteritems():
        average_price[k] = Decimal(v/set_count[k])
    
    mythics_pulled = Decimal(float(1) / float(8)) * NUMBER_PACKS
    mythics_price = mythics_pulled * average_price['M']
    
    rares_pulled = (NUMBER_PACKS - mythics_pulled)
    rares_price = rares_pulled * average_price['R']

    uncommons_pulled = 3 * NUMBER_PACKS
    uncommons_price =  uncommons_pulled * average_price['U']
    
    commons_pulled = 9 * NUMBER_PACKS
    commons_price = commons_pulled * average_price['C']
    
    average_foil_price = Decimal(total_foil_price/sum(set_count.values()))
    foils_pulled = Decimal(float(1) / float(6)) * NUMBER_PACKS
    foils_price = foils_pulled * average_foil_price

    uncommon_bulk_pulled = ((float(1) / float(set_count['U'])) * float(uncommons_pulled - foils_pulled)) / 4
    bulk_uncommon_playsets = Decimal(BULK_LOT_PRICE * uncommon_bulk_pulled)

    total_box_ev = (mythics_price + rares_price + foils_price + bulk_uncommon_playsets)/NUMBER_BOXES

    print "     >>> Foils Pulled: {0:0.0f} at an average price of ${1:0.2f}".format(foils_pulled, average_foil_price)
    print "     >>> Mythics Pulled: {0:0.0f} at an average price of ${1:0.2f}".format(mythics_pulled, average_price['M'])
    print "     >>> Rares Pulled: {0:0.0f} at an average price of ${1:0.2f}".format(rares_pulled, average_price['R'])
    #print "     >>> Uncommons Pulled: {0:0.0f} at an average price of ${1:0.2f}".format(uncommons_pulled, average_price['U'])
    #print "     >>> Commons Pulled: {0:0.0f} at an average price of ${1:0.2f}".format(commons_pulled, average_price['C'])
    print "     >>> Bulk Uncommon/Common Play Sets: {0:0.2f} at an average price of ${1:0.2f}".format(uncommon_bulk_pulled, BULK_LOT_PRICE)
    print "     >>> Total Box Estimated Value: ${:0.2f}".format(total_box_ev)

if __name__ == '__main__':
    main()
import json
import os
from pprint import pprint

from deal import Deal


rules_instr = (1.5, 6, False, 'Any2', 3, True, True, True)

for up_card_index in range(10):
    dlr_cds = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    dlr_cds[up_card_index] += 1

    for pc1_index in range(10):
        for pc2_index in range(10):
            plr_cds = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            plr_cds[pc1_index] += 1
            plr_cds[pc2_index] += 1

            dinstr = (tuple(dlr_cds), False, '', 0, False, False)
            pinstr = (tuple(plr_cds), False, '', 0, False, False)
            d = Deal(rules=rules_instr, dealer=dinstr, player=pinstr)

            print(d.implied_name)
            # print(d.fpath)

            if os.path.isfile(d.fpath):
                with open(d.fpath, 'r') as fp:
                    data = json.load(fp)
                print(data['valuation'][0])

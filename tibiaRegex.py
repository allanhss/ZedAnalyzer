import re
import pandas as pd
import datetime

RGX_boss_name = re.compile(r'(?P<hour>\d\d:\d\d(?::\d\d)?) The following items? dropped by (?P<name>.*) (?:are|is) available in your reward chest: (?P<items>.*)', flags=re.IGNORECASE)
RGX_boss_items = re.compile(r'(?P<qnt>an|a|the|\d+) (?P<item>[^,.\n]*)', flags=re.IGNORECASE)
RGX_boss_boosted = re.compile(r'(\(Boss Bonus\)).*', re.IGNORECASE)

def GetLootfBoss(line, char):
    try:
        log = RGX_boss_boosted.split(line)
        if len(log) > 1:
            boosted = True
        else:
            boosted = False
        boss = re.match(RGX_boss_name, log[0])
        dictOfItems = {'Boss': [boss['name']]}
        dictOfItems.update({'Char':[char[0]]})
        dictOfItems.update({'BossPoints':[char[1]]})
        time = datetime.datetime.now()
        dictOfItems.update({'Time':[f'{time.day}/{time.month}/{time.year}']})
        dictOfItems.update({'Boosted': [boosted]})
        for items in re.findall(RGX_boss_items, boss['items']):
            dictOfItems.update({
                items[1] : [int(re.sub('an|a|the', '1', items[0]))]
            })
        #return dictOfItems
        return pd.DataFrame(dictOfItems)
    
    except Exception as e:
        print(e)
        return 0

if __name__ == '__main__':
    ...

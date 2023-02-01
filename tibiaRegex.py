import re
import pandas as pd
import numpy as np
import datetime
import requests
from bs4 import BeautifulSoup

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
        dictOfItems = {'Boss':[boss['name']]}
        dictOfItems.update({'Char':[char[0]]})
        dictOfItems.update({'BossPoints':[char[1]]})
        time = datetime.datetime.now()
        dictOfItems.update({'Time':[f'{time.day}/{time.month}/{time.year}']})
        dictOfItems.update({'Boosted': [boosted]})
        items = re.findall(RGX_boss_items, boss['items'])
        itms = []
        for item in items:
            itms.append(list(item))
            for itm in itms:
                if itm[0] in ['a', 'an', 'the']:
                    itm[0] = '1'
                while itm[1][-1] in [' ']:
                    itm[1] = itm[1].rstrip(itm[1][-1])
                if itm[1][-1] in ['s']:
                    if int(itm[0]) > 1:
                        itm[1] = itm[1].rstrip(itm[1][-1])
        dictOfItems.update({i[1] : [int(i[0])] for i in itms})
        dfLoot = pd.DataFrame(dictOfItems)
        return dfLoot
    
    except Exception as e:
        print(e)
        return 0
    

def GetPriceData(item):
    #item = '_'.join([i.capitalize() for i in item.split(' ')])
    #url = f'https://tibia.fandom.com/wiki/{item}'
    itm = item.replace(' ','+')
    url = f'https://tibia.fandom.com/wiki/Special:Search?query={itm}&scope=internal&contentType=&ns%5B0%5D=0&ns%5B1%5D=112&ns%5B2%5D=2900go%3DIr&go=Ir'
    #url = f'tibiawiki.com.br/index.php?search={itm}&title=Especial%3ABusca&go=Ir'
    #https://www.tibiawiki.com.br/index.php?search=wand+of+defiance
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'})
    html = BeautifulSoup(response.text, 'html.parser')
    try:
        for str in html.select('div[data-source=npcvalue]')[0].text.split('\n'):
            if 'gp' in str:
                Price = float(str.replace('gp','').replace(',','.'))
                break
            else:
                for str in html.select('div[data-source=value]')[0].text.split('\n'):
                    if 'gp' in str:
                        tst = str.replace('gp','').replace(',','').replace(' ','')
                        Price = float(tst.split('-')[0])
                        break
                    else:
                        Price = 0
        return Price
    except Exception:
        return 0


def PutPriceInLootDf(df):
    for items in df.columns:
        if items in ['Boss','Char', 'BossPoints', 'Time', 'Boosted']:
            continue
        if 'Value' in df[items].index:
            if df[items]['Value'] in ['']:
                dfDummy = pd.DataFrame({items : GetPriceData(items)}, index = ['Value'])
            elif np.isnan(df[items]['Value']):
                dfDummy = pd.DataFrame({items : GetPriceData(items)}, index = ['Value'])
        else:
            dfDummy = pd.DataFrame({items : GetPriceData(items)}, index = ['Value'])
        try: 
            dfPrice = dfPrice.merge(dfDummy, left_index=True, right_index=True)
        except:
            dfPrice = dfDummy
    dfPrice = dfPrice.merge(pd.DataFrame({'Boss':['Value']}),left_index=True, right_on='Boss')
    return pd.concat([df,dfPrice], ignore_index=True)


def OrderLootIndex(df):
    valIndex=[]
    valIndex.append(df.loc[df['Boss'] == 'Value'].index[0])
    for idx in [x for x in range(df.index.stop)]:
        if idx not in valIndex:
            valIndex.append(idx)
    return df.reindex(valIndex)


def OrderLootByValue(df):
    order = ['Boss','Char','Time','BossPoints','Boosted']
    valueIndex = df.loc[df['Boss'] == 'Value'].index
    order.extend(df.drop(columns=order).sort_values(by=valueIndex, axis=1, ascending=False).columns.to_list())
    return df[order]
    


if __name__ == '__main__':
    ...

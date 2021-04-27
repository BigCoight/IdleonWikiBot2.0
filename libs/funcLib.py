import csv
from os import execv
import re
def unScience(val):
    if val:
        if '.' in val:
            return val
        else:
            try:
                return str(int(float(val))) 
            except:
                return val
    return val

def repU(val,t=False):
    try:
        if t:
            return val.replace('|',' ').replace('_',' ')
        else:
            return val.replace('|',' ').replace('_',' ').title()
    except:
        return val

def camelCaseSplitter(string):
    return re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', string)).split()




def nameDic(val):
    with open('./input/raw/Names.csv', mode='r') as infile:
        reader = csv.reader(infile)
        res = {rows[0]:rows[1].lstrip().replace('|',' ').replace('_',' ') for rows in reader if rows[1].lstrip().replace('|',' ').replace('_',' ') not in ["ERROR"]}
    return res.get(val.replace('\n',''),val)

def nameDicR(val):
    with open('./input/raw/Names.csv', mode='r') as infile:
        reader = csv.reader(infile)
        res = {rows[1].lstrip().replace('|',"_").replace('_',' '):rows[0].lstrip() for rows in reader}
    return res.get(val.lstrip().replace('|',"_").replace('_',' '),val)


def enemyInternal():
    with open('./input/raw/rawMapEnemies.txt', mode='r') as inMapEnemies:
        MapEnemies = inMapEnemies.readlines()
    return [x.replace('_', ' ').replace('\n', '') for x in MapEnemies if x != '\n']


def alchVials():
    with open('./input/raw/rawVialData.txt', mode='r') as inVials:
        Vials = inVials.readlines()
    return [x.title().replace('_', ' ').replace('\n', '') for x in Vials if x != '\n']

def mapName():
    with open('./input/raw/rawMapNames.txt', mode='r') as inMapNames:
        mapNames = inMapNames.readlines()
    return [x.replace('_', ' ').replace('\n', '') for x in mapNames if x != '\n']


def nameToMap():
    res = {}
    for i in range(len(mapName())):
        if enemyInternal()[i] in res.keys():
            temp = enemyInternal()[i] + '2'
        else:
            temp = enemyInternal()[i]
        res[temp] = mapName()[i].replace('_', " ")
    return res






# Item functions
def toInt(val):
    try:
        return str(int(val) + 1)
    except:
        return val


def doBonus(val):
    try:
        return val[0].split(",")[0]
    except:
        return "None"

def stampTypeID(val):
    if val[:2] == "10" and len(val) > 2:
        return "Skills"
    elif val[:2] == "20" and len(val) > 2:
        return "Misc"
    else:
        return "Combat"

def fix(val,replaceNull = [],repU = False):
    if val:
        for rep in replaceNull:
            val = val.replace(rep,'')
        if repU:
            val = val.replace('_', ' ')
            if val[0] != '|':
                val = val.replace('|',' ')
        return unScience(val.lstrip().rstrip())
    return unScience(val) 
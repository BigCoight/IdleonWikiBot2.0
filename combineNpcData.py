import json
import numpy as np
from libs.funcLib import fix, nameDic, repU
from libs.jsonEncoder import CompactJSONEncoder


def writeJSON(fn, dicti):
    with open(fr'./output/modified/json/{fn}.json', mode='w') as outfile:
        outfile.write(CompactJSONEncoder(indent=4).encode(dicti))


def openJSON(fn):
    with open(fr'./output/base/json/{fn}.json', mode='r') as jsonFile:
        return json.load(jsonFile)


def openCSV(fn):
    res = []
    with open(fr'./output/base/csv/{fn}.csv', mode='r') as csvFile:
        lines = csvFile.readlines()
        single = len(lines[0].split(";")) == 1
        if single:
            for line in lines:
                res.append(fix(line))
        else:
            for line in lines:
                res.append(fix(line).split(";"))
    return res


def formatDio(line, quest):
    pass


def formatQuest(line):
    pass


def main():
    newNpcs = {}
    npcData = openJSON("Npcs")

    for name, npc in npcData.items():
        newNpcs[name] = {"Quests": [], "Dialogue": []}

        for line in npc:
            if line["Type"] == 'None':
                newNpcs[name]["Dialogue"].append(formatDio(line, False))

            else:
                newNpcs[name]["Quests"].append(formatQuest(line))
                newNpcs[name]["Dialogue"].append(formatDio(line, True))


if __name__ == '__main__':
    main()

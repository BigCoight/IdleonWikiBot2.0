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


def main():
    newTalents = {}
    talents = openJSON("Talents")
    activeInfo = openJSON("ActiveDetails")

    for category, talents in talents.items():
        newTalents[repU(category)] = {}
        for name, talent in talents.items():
            newTalents[repU(category)][repU(name)] = {}
            for atr, var in talent.items():
                newTalents[repU(category)][repU(name)][atr] = repU(var, True)

    for activeTalentName, activeTalent in activeInfo.items():
        for _, catTalents in newTalents.items():
            for name, subTalends in catTalents.items():
                if activeTalentName == name:
                    subTalends["ActiveData"] = activeTalent
    writeJSON("Talents", newTalents)


if __name__ == "__main__":
    main()

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
    temp = {}
    if dtext := line.get("DialogueText"):
        temp["text"] = dtext
    if quest:
        if name := line.get("Name"):
            temp["associated"] = name
    return temp


def formatQuest(line):
    symbols = {
        "GreaterEqual": ">=",
        "": "",
        "": "",
    }
    temp = {}
    temp["rewards"] = []
    for i in range(len(line["Rewards"]), 0, 2):
        temp["rewards"].append((line["Rewards"][i], line["Rewards"][i+1]))

    if line["Type"] == "Custom":
        current = line["CustomArray"]
        tempReq = ''
        tempReq += f"{current[0]} {symbols[current[2]]} {current[1]}. Starting at {current[3]}. "
        if len(current) > 4:
            tempReq += f"{current[4]} {symbols[current[6]]} {current[5]}. Starting at {current[7]}. "

    elif line["Type"] == "ItemsAndSpaceRequired":
        tempReq = []
        for n, v in zip(line["ItemNumReq"], line["ItemTypeReq"]):
            tempReq.append([nameDic(v), n])
    temp["requirements"] = tempReq
    return temp


def main():
    newNpcs = {}
    npcData = openJSON("Npcs")

    for name, npc in npcData.items():
        if name == "Mecha_Pete":
            continue
        newNpcs[name] = {"Quests": [], "Dialogue": []}

        for line in npc:
            if line["Type"] in ['None', "LevelReq", "SpaceRequired"]:
                newNpcs[name]["Dialogue"].append(formatDio(line, False))

            else:
                newNpcs[name]["Quests"].append(formatQuest(line))
                newNpcs[name]["Dialogue"].append(formatDio(line, True))

    writeJSON("Npcs", newNpcs)


if __name__ == '__main__':
    main()

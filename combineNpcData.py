import json
import numpy as np
from libs.funcLib import fix, nameDic, repU
from libs.jsonEncoder import CompactJSONEncoder


def writeJSON(fn, dicti):
    with open(fr"./output/modified/json/{fn}.json", mode="w") as outfile:
        outfile.write(CompactJSONEncoder(indent=4).encode(dicti))


def openJSON(fn):
    with open(fr"./output/base/json/{fn}.json", mode="r") as jsonFile:
        return json.load(jsonFile)


def openCSV(fn):
    res = []
    with open(fr"./output/base/csv/{fn}.csv", mode="r") as csvFile:
        lines = csvFile.readlines()
        single = len(lines[0].split(";")) == 1
        if single:
            for line in lines:
                res.append(fix(line))
        else:
            for line in lines:
                res.append(fix(line).split(";"))
    return res


def getTalentName(qty):
    talentName = openCSV("TalentNames")
    no = int(qty[0])
    index = int(qty[1 : no + 1])
    return repU(talentName[index])


def getSmithingRecipe(name, qty):
    recipes = openJSON("Recipes")
    tab = int(name[-1]) - 1
    index = int(qty)
    for name, item in recipes[tab].items():
        if int(item["no"]) == index:
            return nameDic(name), tab


def formatDio(line, quest):
    temp = {}
    if dtext := line.get("DialogueText"):
        temp["text"] = dtext
    if quest:
        if name := line.get("Name"):
            temp["associated"] = name
    return temp


def formatQuest(line):
    lvlType = ["Class", "Mining", "Smithing", "Chopping", "Fishing", "Alchemy", "Catching"]
    symbols = {
        "GreaterEqual": ">=",
        "": "",
        "": "",
    }
    newQuest = {}
    currentRew = []
    lineRew = line["Rewards"]
    for i in range(0, len(lineRew), 2):
        currentRewName = nameDic(lineRew[i])
        if lineRew[i][:10] == "Experience":
            currentRewName = lvlType[int(lineRew[i][-1])] + ";Experience"
        elif lineRew[i][:-1] == "TalentBook":
            currentRewName = getTalentName(lineRew[i + 1]) + ";Talent Book"
            lineRew[i + 1] = "1"
        elif lineRew[i][:-1] == "SmithingRecipes":
            recipData = getSmithingRecipe(lineRew[i], lineRew[i + 1])
            lineRew[i + 1] = "1"
            currentRewName = f"{recipData[0]};Recipe;{recipData[1]}"

        currentRew.append((currentRewName, lineRew[i + 1]))

    newQuest["rewards"] = currentRew

    if line["Type"] == "Custom":
        current = line["CustomArray"]
        tempReq = []
        tempReq.append(f"{current[0]} {symbols[current[2]]} {current[1]}. Starting at {current[3]}.")
        if len(current) > 4:
            tempReq.append(f"{current[4]} {symbols[current[6]]} {current[5]}. Starting at {current[7]}.")
        tempReq = repU(tempReq, True)
    elif line["Type"] == "ItemsAndSpaceRequired":
        tempReq = []
        for n, v in zip(line["ItemNumReq"], line["ItemTypeReq"]):
            tempReq.append([nameDic(v), n])
    newQuest["requirements"] = tempReq

    newQuest["consumed"] = "Yes" if line["ConsumeItems"] == "!0" else "No"
    newQuest["dialogueText"] = line["DialogueText"]
    newQuest["difficulty"] = line["Difficulty"]
    newQuest["name"] = line["Name"]
    dTextSplit = line["DialogueText"].split(":")
    if len(dTextSplit) > 1:
        newQuest["questText"] = dTextSplit[1]
        newQuest["DialogueText"] = dTextSplit[0]

    questName = newQuest["name"]
    return questName, newQuest


def main():
    newNpcs = {}
    npcData = openJSON("Npcs")
    nameConflicts = {"Ghost": "Ghost_(Event)", "Dog_Bone": "Dog_Bone_(NPC)"}

    for name, npc in npcData.items():
        if name == "Mecha_Pete":
            continue
        name = nameConflicts.get(name, name)
        newNpcs[name] = {"Quests": {}, "Dialogue": []}

        for line in npc:
            if line["Type"] in ["None", "LevelReq", "SpaceRequired"]:
                newNpcs[name]["Dialogue"].append(formatDio(line, False))

            else:
                questName, questData = formatQuest(line)
                newNpcs[name]["Quests"][questName] = questData
                newNpcs[name]["Dialogue"].append(formatDio(line, True))

    writeJSON("Npcs", newNpcs)


if __name__ == "__main__":
    main()

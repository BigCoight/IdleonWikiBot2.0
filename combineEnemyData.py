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


def getSmithingRecipe(recipes, name, qty):
    tab = int(name[-1]) - 1
    index = int(qty) + 1
    for name, item in recipes[tab].items():
        if int(item["no"]) == index:
            return nameDic(name), tab


def getTalentName(talentName, qty):
    no = int(qty[0])
    index = int(qty[1 : no + 1])
    return repU(talentName[index])


def updateDrops(drops, recipes, talentNames):
    newDrops = []
    for drop in drops:
        if drop[2] == "0" or drop[1] == "0":
            continue
        drop[0] = nameDic(drop[0])
        if drop[0][:-1] == "SmithingRecipes":
            recipData = getSmithingRecipe(recipes, drop[0], drop[2])
            dname = f"{recipData[0]};Recipe;{recipData[1]}"
            newDrops.append([dname, drop[1], "1", drop[3]])
        elif drop[0][:-1] == "TalentBook":
            dname = getTalentName(talentNames, drop[2]) + ";Talent Book"
            newDrops.append([dname, drop[1], "1", drop[3]])
        else:
            newDrops.append(drop)
    return newDrops


def defFor0Dmg(monsterDmg):
    y = int(monsterDmg)

    def f1(x):
        return x ** 2.5 + 500 * y * x ** 0.8 - 200 * y ** 2 + 100 * y

    def f2(x):
        return 2.5 * x ** 1.5 + 400 * y * x ** -0.2

    z = 1
    eps = 1e-1
    n = 0
    while abs(f1(z) / f2(z)) > eps:
        z = z - f1(z) / f2(z)
        n += 1
    return round(z, 2)


def updateOrder(name, enemy, enemies, order):
    if name in order:
        spot = order.index(name)
        if spot != 0:
            enemy["Prev"] = enemies[order[spot - 1]]["Name"]
        if spot != len(order) - 1:
            enemy["Next"] = enemies[order[spot + 1]]["Name"]


def openNotes(fn):
    with open(fr"./output/notes/{fn}.json", mode="r") as jsonFile:
        return json.load(jsonFile)


def main():
    worldToCrystal = {"Blunder Hills": "Crystal0", "Yum Yum Desert": "Crystal1", "Frostbite Tundra": "Crystal2"}
    enemies = openJSON("Enemies")
    recipes = openJSON("Recipes")
    subTables = openJSON("Droptables")
    talentNames = openCSV("TalentNames")
    cardData = openJSON("CardData")
    mapEnem = openCSV("MapEnemies")
    mapName = openCSV("MapNames")
    notes = openNotes("Enemies")
    custDTs = openJSON("CustomDropTables")
    mapEnemToName = {}
    for i in range(len(mapEnem)):
        if mapEnem[i] in mapEnemToName.keys():
            continue
        mapEnemToName[mapEnem[i]] = mapName[i]
    order = []
    for world, cards in cardData.items():
        if "Resources" in world:
            continue
        for name in cards.keys():
            if name == "Blank" or name not in enemies.keys():
                continue
            enemies[name]["hasCard"] = "Yes"
            if crystal := worldToCrystal.get(world):
                enemies[name]["World"] = world
                if crystal in enemies.keys():
                    enemies[name]["Crystal"] = enemies[crystal]["Name"]
                enemies[name]["hasCrystal"] = "Yes"
            if name != "Bandit_Bob":
                order.append(name)

    for name, enemy in enemies.items():
        # Update the order navigation
        updateOrder(name, enemy, enemies, order)
        enemy["Damages"] = enemy["Damages"][0]
        enemy["Image"] = enemy["Name"] + " Walking.gif"

        if area := mapEnemToName.get(name):
            enemy["Area"] = repU(area, True)
        # update drops esp recipe drops and talent books
        if drops := enemy.get("Drops"):
            enemies[name]["Drops"] = updateDrops(drops, recipes, talentNames)
        else:
            enemies[name]["Drops"] = []
        if mType := enemy.get("Type"):
            enemy["Type"] = mType.split(".")[1]

        enemy["defFor0"] = defFor0Dmg(enemy["Damages"])
    for name, table in subTables.items():
        subTables[name] = updateDrops(table, recipes, talentNames)
    for name, table in custDTs.items():
        custDTs[name] = updateDrops(table, recipes, talentNames)
    skillDTS = {"ORE_TYPE": {}, "TREE_TYPE": {}, "FISH_TYPE": {}, "BUG_TYPE": {}, "Colloseum": {}}
    toDel = []
    for name, enemy in enemies.items():
        tables = "None"
        if enemy["Type"] != "MONSTER_TYPE":  # For skills
            tables = skillDTS.get(enemy["Type"], "None")
        elif "Chest" == name[:5]:  # For Colosseum
            tables = skillDTS["Colloseum"]

        if tables != "None":
            tables[enemy["Name"]] = enemy.get("Drops")
            toDel.append(name)

    for dele in toDel:
        del enemies[dele]

    for name, note in notes.items():
        if name in enemies.keys():
            enemies[name]["notes"] = note

    writeJSON("SkillingDT", skillDTS)
    writeJSON("Enemies", enemies)
    writeJSON("DropTables", subTables)
    writeJSON("CustomDroptables", custDTs)


if __name__ == "__main__":
    main()

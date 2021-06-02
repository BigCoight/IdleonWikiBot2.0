from libs.jsonEncoder import CompactJSONEncoder
import deepdiff
from deepdiff.helper import CannotCompare
import extractInfo
import json
import re


def writeJSON(fn, dicti):
    with open(fr"./output/changelog/{fn}.json", mode="w") as outfile:
        outfile.write(CompactJSONEncoder(indent=4).encode(dicti))


def openJSON(subc, fn):
    with open(fr"./output/{subc}/json/{fn}.json", mode="r") as jsonFile:
        return json.load(jsonFile)


def compareTwo(x, y, level=None):
    if not isinstance(x, list) or not isinstance(y, list):
        raise CannotCompare() from None
    if len(x) != 2 or len(y) != 2:
        raise CannotCompare() from None
    try:
        return x[0] == y[0] and x[1] == y[1]
    except Exception:
        raise CannotCompare() from None


def compareDrops(x, y, level=None):
    if not isinstance(x, list) or not isinstance(y, list):
        raise CannotCompare() from None
    if len(x) != 4 or len(y) != 4:
        raise CannotCompare() from None
    try:
        return x[0] == y[0] and x[1] == y[1] and x[2] == y[2] and x[3] == y[3]
    except Exception:
        raise CannotCompare() from None


def compareItem(x, y, level=None):
    try:
        return x["quantity"] == y["quantity"] and x["item"] == y["item"] and x["no"] == y["no"]
    except Exception:
        raise CannotCompare() from None


def compare(old, new, name, compareFunc=None, excludeReges=""):
    def getMatch(match):
        if match[0] == "":
            return match[1]
        else:
            return match[0]

    regex = r"\['([\w \-\.']*)'\]|\[([0-9]*)\]"
    formattedChanges = {"Changes": {}, "New": {}, "Removed": {}}
    difference = deepdiff.DeepDiff(old, new, ignore_order=False, exclude_regex_paths=excludeReges, iterable_compare_func=compareFunc, ignore_numeric_type_changes=True)
    print(difference.keys())
    if changes := difference.get("values_changed"):
        for change, changed in changes.items():
            matches = re.findall(regex, change)
            if not matches:
                continue
            current = formattedChanges["Changes"]
            for match in matches[:-1]:
                if getMatch(match) in current.keys():
                    current = current[getMatch(match)]
                else:
                    current[getMatch(match)] = {}
                    current = current[getMatch(match)]
            current[getMatch(matches[-1])] = (changed["old_value"], changed["new_value"])
    if changes := difference.get("iterable_item_removed"):
        for change, changed in changes.items():
            if not matches:
                continue
            current = formattedChanges["Changes"]
            for match in matches[:-1]:
                if getMatch(match) in current.keys():
                    current = current[getMatch(match)]
                else:
                    current[getMatch(match)] = {}
                    current = current[getMatch(match)]
            current[getMatch(matches[-1])] = (changed, "Removed")
    if changes := difference.get("iterable_item_added"):
        for change, changed in changes.items():
            matches = re.findall(regex, change)
            if not matches:
                continue
            current = formattedChanges["Changes"]
            for match in matches[:-1]:
                if getMatch(match) in current.keys():
                    current = current[getMatch(match)]
                else:
                    current[getMatch(match)] = {}
                    current = current[getMatch(match)]
            current[getMatch(matches[-1])] = (" ", changed)
    if changes := difference.get("dictionary_item_added"):
        for newValue in changes:
            matches = re.findall(regex, newValue)
            current = formattedChanges["New"]
            tempToAdd = new
            for match in matches[:-1]:
                if getMatch(match) in current.keys():
                    current = current[getMatch(match)]
                else:
                    current[getMatch(match)] = {}
                    current = current[getMatch(match)]
                tempToAdd = tempToAdd[getMatch(match)]

            for toDel in excludeReges:
                if toDel in tempToAdd.keys():
                    del tempToAdd[toDel]

            if isinstance(tempToAdd[getMatch(matches[-1])], dict):
                for toDel in excludeReges:
                    if toDel in tempToAdd[getMatch(matches[-1])].keys():
                        del tempToAdd[getMatch(matches[-1])][toDel]

            current[getMatch(matches[-1])] = tempToAdd[getMatch(matches[-1])]
    if changes := difference.get("dictionary_item_removed"):
        for newValue in changes:
            matches = re.findall(regex, newValue)
            current = formattedChanges["Removed"]
            tempToAdd = old
            for match in matches[:-1]:
                if getMatch(match) in current.keys():
                    current = current[getMatch(match)]
                else:
                    current[getMatch(match)] = {}
                    current = current[getMatch(match)]
                tempToAdd = tempToAdd[getMatch(match)]

            for toDel in excludeReges:
                if toDel in tempToAdd.keys():
                    del tempToAdd[toDel]
            current[getMatch(matches[-1])] = tempToAdd[getMatch(matches[-1])]
    if changes := difference.get("type_changes"):
        print(changes)
    writeJSON(name, formattedChanges)


def main(oldVer, newVer):
    extractInfo.main(fr"./input/codefile/idleon{oldVer}.txt")

    dropTableOld = openJSON("modified", "DropTables")
    enemiesOld = openJSON("modified", "Enemies")
    itemsOld = openJSON("modified", "Items")
    npcsOld = openJSON("modified", "Npcs")
    skillingDTOld = openJSON("modified", "SkillingDT")
    talentsOld = openJSON("modified", "Talents")

    postOfficeOld = openJSON("base", "PostOffice")
    cauldrenOld = openJSON("base", "Cauldrens")
    shopsOld = openJSON("base", "ShopData")

    extractInfo.main(fr"./input/codefile/idleon{newVer}.txt")

    dropTableNew = openJSON("modified", "DropTables")
    enemiesNew = openJSON("modified", "Enemies")
    itemsNew = openJSON("modified", "Items")
    npcsNew = openJSON("modified", "Npcs")
    skillingDTNew = openJSON("modified", "SkillingDT")
    talentsNew = openJSON("modified", "Talents")

    postOfficeNew = openJSON("base", "PostOffice")
    cauldrenNew = openJSON("base", "Cauldrens")
    shopsNew = openJSON("base", "ShopData")

    compare(dropTableOld, dropTableNew, "Droptables", compareDrops)
    compare(enemiesOld, enemiesNew, "Enemies", compareDrops, ["Area", "Prev", "Next", "Image", "AFKtype", "MonsterFace", "MonsterOffsetX", "MonsterOffsetY", "HeightOfMonster", "MonsterMoving", "MovingFrame", "DeathFrame", "Type", "SpecialType", "hasCard", "World", "Crystal", "hasCrystal"])
    compare(itemsOld, itemsNew, "Items", compareTwo, ["detdrops", "sources", "detrecipe", "detRecipeTotals", "shopData", "uses", "questAss", "hascard"])
    compare(npcsOld, npcsNew, "Npcs", compareTwo, ["Dialogue"])
    compare(skillingDTOld, skillingDTNew, "SkillingDTs", compareDrops)
    compare(talentsOld, talentsNew, "Talents", excludeReges=["Active Data"])
    compare(postOfficeOld, postOfficeNew, "PostOffice")
    compare(cauldrenOld, cauldrenNew, "Alchemy", compareTwo)
    compare(shopsOld, shopsNew, "Shops", compareItem)


if __name__ == "__main__":
    main("120", "120b")

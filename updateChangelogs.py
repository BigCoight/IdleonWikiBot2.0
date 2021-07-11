import json
from libs.funcLib import fix, nameDic, repU


def openChangeJSON(fn):
    with open(fr"./output/changelog/{fn}.json", mode="r") as jsonFile:
        return json.load(jsonFile)


def openJSON(fn):
    with open(fr"./output/modified/json/{fn}.json", mode="r") as jsonFile:
        return json.load(jsonFile)


def writePatchnote(typ, a, b):
    return "{{patchnote|" f"{typ}|{a}|{b}" + "}}\n"


def writepHead(title):
    return "{{patchnote/head|changed=" + title + "}}\n"


def writepTail():
    return "|}\n\n"


def writepBold(title):
    return f"|-\n|'''{title}'''\n"


def writepItalic(title):
    return f"|-\n|''{title}''\n"


def writepItem(title):
    return "{{patchnote/item|" + title + "}}\n"


def writecChangeHead(title):
    return f'__NOTOC__<div style = "display:flex;"><div style = "flex:50%;"> \n==Changed {title}==\n'


def writecNewHead(title):
    return f'</div><div style = "flex:50%;"> \n==New {title}==\n'


def writecTail():
    return "</div></div>\n"


def doRecipeData(new, data):
    def craftReq(recipeSub):
        return recipeSub[1] + "x {{CraftReq|" + recipeSub[0] + "}}"

    result = writepBold("Recipe Data")
    for dataName, recipeData in data.items():
        if new:
            if dataName == "recipe":
                for n, recipe in enumerate(recipeData):
                    result += writePatchnote(f"Item {n+1}", "", craftReq(recipe))
            else:
                result += writePatchnote(dataName, " ", recipeData)
        else:
            if dataName == "recipe":
                for changeNo, recipeChanges in recipeData.items():
                    if len(recipeChanges[0]) < 2:
                        return ""
                    result += writePatchnote(f"Item {changeNo}", craftReq(recipeChanges[0]), craftReq(recipeChanges[1]))
            else:
                result += writePatchnote(dataName, recipeData[0], recipeData[1])

    return result + "\n"


def temp(new, data):
    return ""


def doCardData(new, data):
    cardChangeNames = ["Section", "Cards Needed", "Bonus", "Base Val", "Id", "Enemy"]
    result = writepBold("Card Data")
    if new:
        for n, cardData in enumerate(data):
            result += writePatchnote(cardChangeNames[n], " ", cardData)
        return result + "\n"

    for datIndex, cardData in data.items():
        result += writePatchnote(cardChangeNames[int(datIndex)], cardData[0], cardData[1])
    return result + "\n"


def doFishingData(new, data):
    result = writepBold("Fishing Data")
    if new:
        for atr, val in enumerate(data):
            result += writePatchnote(atr, " ", val)
        return result + "\n"

    for atr, val in enumerate(data):
        result += writePatchnote(atr, val[0], val[1])
    return result + "\n"


def doStampData(new, data):
    stampChangeNames = ["Bonus", "func", "x1", "x2", "i4", "material", "i6", "i7", "i8", "i9", "i10", "Bonus", "i12"]
    result = writepBold("Stamp Data")
    if new:
        for n, stampData in enumerate(data):
            result += writePatchnote(stampChangeNames[n], " ", stampData)
        return result + "\n"

    for datIndex, stampData in data.items():
        result += writePatchnote(stampChangeNames[int(datIndex)], stampData[0], stampData[1])
    return result + "\n"


def doStatueData(new, data):
    stampChangeNames = ["Name", "Bonus", "X1", "Increment"]
    result = writepBold("Statue Data")
    if new:
        for n, stampData in enumerate(data):
            result += writePatchnote(stampChangeNames[n], " ", stampData)
        return result + "\n"

    for datIndex, stampData in data.items():
        result += writePatchnote(stampChangeNames[int(datIndex)], stampData[0], stampData[1])
    return result + "\n"


def doDescData(new, data):
    result = writepBold("Description")
    if new:
        for n, descLine in enumerate(data):
            result += writePatchnote(f"Description Line {n + 1}", " ", descLine)
        return result + "\n"
    for datIndex, descLine in data.items():
        result += writePatchnote(f"Description Line {int(datIndex) + 1}", descLine[0], descLine[1])
    return result + "\n"


def doDrops(new, data):
    def dropReq(drop):
        if len(drop) < 3:
            return " "
        if "Drop" in drop[0]:
            return f"{drop[0]}: qty:{drop[2]}, chance:{drop[1]}"
        else:
            return "{{CraftReq|" + drop[0] + "}}: " + f"qty:{drop[2]}, chance:{drop[1]}"

    result = writepBold("Droptable")
    if new:
        for changeNo, dropChanges in enumerate(data):
            result += writePatchnote(f"Item {int(changeNo) + 1}", " ", dropReq(dropChanges))
        return result + "\n"
    else:
        for changeNo, dropChanges in data.items():
            result += writePatchnote(f"Item {int(changeNo) + 1}", dropReq(dropChanges[0]), dropReq(dropChanges[1]))
        return result + "\n"


def doRequirements(new, data):
    def craftReq(reqSub):
        return reqSub[1] + "x {{CraftReq|" + reqSub[0] + "}}"

    result = writepItalic("Requirements")
    if new:
        for n, value in enumerate(data):
            if isinstance(value, list):
                result += writePatchnote(f"Req {int(n)+1}", " ", craftReq(value))
            else:
                result += writePatchnote(f"Req {int(n)+1}", " ", value.replace(">=", ">"))
        return result + "\n"
    else:
        for n, value in data.items():
            if isinstance(value[0], list):
                result += writePatchnote(f"Req {int(n)+1}", craftReq(value[0]), craftReq(value[1]))
            else:
                result += writePatchnote(f"Req {int(n)+1}", value[0].replace(">=", ">"), value[1].replace(">=", ">"))
        return result + "\n"


def doRewards(new, data):
    def craftReq(reqSub):
        print(reqSub)
        if ";" in reqSub[0]:
            return reqSub[1] + "x " + reqSub[0]
        return reqSub[1] + "x {{CraftReq|" + reqSub[0] + "}}"

    result = writepItalic("Rewards")
    if new:
        for n, value in enumerate(data):
            result += writePatchnote(f"Reward {int(n)+1}", " ", craftReq(value))
        return result + "\n"
    else:
        for n, value in data.items():
            if value[0] == " ":
                result += writePatchnote(f"Reward {int(n)+1}", " ", craftReq(value[1]))
                continue
            result += writePatchnote(f"Reward {int(n)+1}", craftReq(value[0]), craftReq(value[1]))
        return result + "\n"


def doReqAlchemy(new, data):
    def craftReq(reqSub):
        if "Liquid" == reqSub[0][:-1]:
            return reqSub[1] + "x {{Liquid|" + reqSub[0][-1] + "}}"
        return reqSub[1] + "x {{CraftReq|" + nameDic(reqSub[0]) + "}}"

    result = writepItalic("Requirements")
    if new:
        for n, value in enumerate(data):
            result += writePatchnote(f"Req {int(n)+1}", " ", craftReq(value))
        return result + "\n"
    else:
        for n, value in data.items():
            result += writePatchnote(f"Req {int(n)+1}", craftReq(value[0]), craftReq(value[1]))
        return result + "\n"


def addToDict(dic, key, value):
    dic[key] = dic.get(key, "") + value


def writeItemsOut(changeLog):
    def getItemType(internalName):
        return items[internalName].get("Type", "Other")

    changeToFunction = {"recipeData": doRecipeData, "Fishing": doFishingData, "cardData": doCardData, "description": doDescData, "stampData": doStampData, "statueData": doStatueData}
    items = openJSON("Items")
    changedItems = {}
    currentChangelogOut = ""

    for internalName, itemChange in changeLog["Changes"].items():
        itemType = getItemType(internalName)
        addToDict(changedItems, itemType, writepItem(nameDic(internalName)))
        for atrChange, valChange in itemChange.items():
            if func := changeToFunction.get(atrChange):
                addToDict(changedItems, itemType, func(False, valChange))
            else:
                addToDict(changedItems, itemType, writePatchnote(atrChange, valChange[0], valChange[1]))

    currentChangelogOut += writecChangeHead("Items")
    for typeChange, changes in changedItems.items():
        currentChangelogOut += writepHead(typeChange)
        currentChangelogOut += changes
        currentChangelogOut += writepTail()

    newItems = {}
    for internalName, itemChange in changeLog["New"].items():
        itemType = getItemType(internalName)
        addToDict(newItems, itemType, writepItem(nameDic(internalName)))
        for atrChange, valChange in itemChange.items():
            if func := changeToFunction.get(atrChange):
                addToDict(newItems, itemType, func(True, valChange))
            else:
                addToDict(newItems, itemType, writePatchnote(atrChange, " ", valChange))

    currentChangelogOut += writecNewHead("Items")
    for typeChange, changes in newItems.items():
        currentChangelogOut += writepHead(typeChange)
        currentChangelogOut += changes
        currentChangelogOut += writepTail()

    currentChangelogOut += writecTail()
    with open(r"./output/wiki/changelog/items.txt", mode="w") as outfile:
        outfile.write(currentChangelogOut.replace("_", " "))


def writeEnemiesOut(changeLog):
    changeToFunction = {"Drops": doDrops}
    changedEnemies = {}
    currentChangelogOut = ""

    for internalName, enemyChange in changeLog["Changes"].items():
        for atrChange, valChange in enemyChange.items():
            if func := changeToFunction.get(atrChange):
                addToDict(changedEnemies, nameDic(internalName), func(False, valChange))
            else:
                addToDict(changedEnemies, nameDic(internalName), writePatchnote(atrChange, valChange[0], valChange[1]))

    currentChangelogOut += writecChangeHead("Enemies")
    for enemyChange, changes in changedEnemies.items():
        currentChangelogOut += writepHead(enemyChange)
        currentChangelogOut += changes
        currentChangelogOut += writepTail()

    newEnemies = {}
    for internalName, enemyChange in changeLog["New"].items():
        for atrChange, valChange in enemyChange.items():
            if func := changeToFunction.get(atrChange):
                addToDict(newEnemies, nameDic(internalName), func(True, valChange))
            else:
                addToDict(newEnemies, nameDic(internalName), writePatchnote(atrChange, " ", valChange))

    currentChangelogOut += writecNewHead("Enemies")
    for enemyChange, changes in newEnemies.items():
        currentChangelogOut += writepHead(enemyChange)
        currentChangelogOut += changes
        currentChangelogOut += writepTail()

    currentChangelogOut += writecTail()

    with open(r"./output/wiki/changelog/enemies.txt", mode="w") as outfile:
        outfile.write(currentChangelogOut.replace("_", " "))


def writeNPCsOut(changeLog):
    changeToFunction = {"requirements": doRequirements, "rewards": doRewards}
    changedNPCs = {}
    currentChangelogOut = ""

    for internalName, enemyChange in changeLog["Changes"].items():
        for atrChange, valChange in enemyChange["Quests"].items():
            addToDict(changedNPCs, internalName, writepBold(atrChange))
            if isinstance(valChange, list):
                addToDict(changedNPCs, internalName, writePatchnote(atrChange, valChange[0], valChange[1]))
                continue
            for changeType, changeValue in valChange.items():
                if func := changeToFunction.get(changeType):
                    addToDict(changedNPCs, internalName, func(False, changeValue))
                else:
                    addToDict(changedNPCs, internalName, writePatchnote(changeType, changeValue[0], changeValue[1]))

    currentChangelogOut += writecChangeHead("Npcs")
    for npcChange, changes in changedNPCs.items():
        currentChangelogOut += writepHead(npcChange)
        currentChangelogOut += changes
        currentChangelogOut += writepTail()

    newNpcs = {}
    for internalName, enemyChange in changeLog["New"].items():
        for atrChange, valChange in enemyChange["Quests"].items():
            addToDict(newNpcs, internalName, writepBold(atrChange))
            for changeType, changeValue in valChange.items():
                if func := changeToFunction.get(changeType):
                    addToDict(newNpcs, internalName, func(True, changeValue))
                else:
                    addToDict(newNpcs, internalName, writePatchnote(changeType, " ", changeValue))

    currentChangelogOut += writecNewHead("Npcs")
    for enemyChange, changes in newNpcs.items():
        currentChangelogOut += writepHead(enemyChange)
        currentChangelogOut += changes
        currentChangelogOut += writepTail()

    currentChangelogOut += writecTail()

    with open(r"./output/wiki/changelog/npcs.txt", mode="w") as outfile:
        outfile.write(currentChangelogOut.replace("_", " "))


def writeDroptablesOut(changeLog):
    def dropReq(drop):
        if len(drop) < 3:
            return " "
        if "Drop" in drop[0]:
            return f"{drop[0]}: qty:{drop[2]}, chance:{drop[1]}"
        else:
            return "{{CraftReq|" + drop[0] + "}}: " + f"qty:{drop[2]}, chance:{drop[1]}"

    changedDroptables = {}
    currentChangelogOut = ""

    for internalName, dropChange in changeLog["Changes"].items():
        for atrChange, valChange in dropChange.items():
            addToDict(changedDroptables, nameDic(internalName), writePatchnote(f"Drop {atrChange}", dropReq(valChange[0]), dropReq(valChange[1])))

    currentChangelogOut += writecChangeHead("Droptables")
    for enemyChange, changes in changedDroptables.items():
        currentChangelogOut += writepHead(enemyChange)
        currentChangelogOut += changes
        currentChangelogOut += writepTail()

    newDroptables = {}
    for internalName, dropChange in changeLog["New"].items():
        for atrChange, valChange in enumerate(dropChange):
            addToDict(newDroptables, nameDic(internalName), writePatchnote(f"Drop {atrChange}", " ", dropReq(valChange)))

    currentChangelogOut += writecNewHead("Droptables")
    for enemyChange, changes in newDroptables.items():
        currentChangelogOut += writepHead(enemyChange)
        currentChangelogOut += changes
        currentChangelogOut += writepTail()

    currentChangelogOut += writecTail()

    with open(r"./output/wiki/changelog/droptables.txt", mode="w") as outfile:
        outfile.write(currentChangelogOut.replace("_", " "))


def writeAlchemyOut(changeLog):
    changeToFunction = {"requirements": doReqAlchemy}
    changedCauldren = {}
    currentChangelogOut = ""

    for caulName, cauldrenChange in changeLog["Changes"].items():
        for bubbleName, bubbleChange in cauldrenChange.items():
            addToDict(changedCauldren, caulName, writepBold(bubbleName))
            for atrChange, valChange in bubbleChange.items():
                if func := changeToFunction.get(atrChange):
                    addToDict(changedCauldren, caulName, func(False, valChange))
                else:
                    addToDict(changedCauldren, caulName, writePatchnote(atrChange, repU(valChange[0], True), repU(valChange[1], True)))

    currentChangelogOut += writecChangeHead("Alchemy")
    for typeChange, changes in changedCauldren.items():
        currentChangelogOut += writepHead(typeChange)
        currentChangelogOut += changes
        currentChangelogOut += writepTail()

    newCauldrens = {}
    for caulName, cauldrenChange in changeLog["New"].items():
        for bubbleName, bubbleChange in cauldrenChange.items():
            addToDict(newCauldrens, caulName, writepBold(bubbleName))
            for atrChange, valChange in bubbleChange.items():
                if func := changeToFunction.get(atrChange):
                    addToDict(newCauldrens, caulName, func(True, valChange))
                else:
                    addToDict(newCauldrens, caulName, writePatchnote(atrChange, " ", repU(valChange, True)))

    currentChangelogOut += writecNewHead("Alchemy")
    for typeChange, changes in newCauldrens.items():
        currentChangelogOut += writepHead(typeChange)
        currentChangelogOut += changes
        currentChangelogOut += writepTail()

    currentChangelogOut += writecTail()
    with open(r"./output/wiki/changelog/alchemy.txt", mode="w") as outfile:
        outfile.write(currentChangelogOut.replace("_", " "))


def writeShopsOut(changeLog):
    def writeItem(itemSlot):
        if isinstance(itemSlot, dict):
            res = "{{CraftReq|" + nameDic(itemSlot["item"]) + "}} "
            res += f"qty: {itemSlot['quantity']}"
            return res
        else:
            return " "

    changedShops = {}
    currentChangelogOut = ""

    for internalName, shopChange in changeLog["Changes"].items():
        for n, valChange in shopChange.items():
            addToDict(changedShops, internalName, writePatchnote(f"Item {int(n)+1}", writeItem(valChange[0]), writeItem(valChange[1])))

    currentChangelogOut += writecChangeHead("Shops")
    for shopChange, changes in changedShops.items():
        currentChangelogOut += writepHead(shopChange)
        currentChangelogOut += changes
        currentChangelogOut += writepTail()

    newShops = {}
    for internalName, shopChange in changeLog["New"].items():
        for n, valChange in enumerate(shopChange):
            addToDict(newShops, internalName, writePatchnote(f"Item {n+1}", " ", writeItem(valChange)))

    currentChangelogOut += writecNewHead("Shops")
    for shopChange, changes in newShops.items():
        currentChangelogOut += writepHead(shopChange)
        currentChangelogOut += changes
        currentChangelogOut += writepTail()

    currentChangelogOut += writecTail()

    with open(r"./output/wiki/changelog/shops.txt", mode="w") as outfile:
        outfile.write(currentChangelogOut.replace("_", " "))


def writeTalentOut(changeLog):
    changedTalents = {}
    currentChangelogOut = ""

    for caulName, talentPageChange in changeLog["Changes"].items():
        for bubbleName, talentChange in talentPageChange.items():
            addToDict(changedTalents, caulName, writepBold(bubbleName))
            for atrChange, valChange in talentChange.items():
                addToDict(changedTalents, caulName, writePatchnote(atrChange, repU(valChange[0], True), repU(valChange[1], True)))

    currentChangelogOut += writecChangeHead("Talent")
    for typeChange, changes in changedTalents.items():
        currentChangelogOut += writepHead(typeChange)
        currentChangelogOut += changes
        currentChangelogOut += writepTail()

    newTalents = {}
    for caulName, talentPageChange in changeLog["New"].items():
        for bubbleName, talentChange in talentPageChange.items():
            addToDict(newTalents, caulName, writepBold(bubbleName))
            for atrChange, valChange in talentChange.items():
                addToDict(newTalents, caulName, writePatchnote(atrChange, " ", repU(valChange, True)))

    currentChangelogOut += writecNewHead("Talent")
    for typeChange, changes in newTalents.items():
        currentChangelogOut += writepHead(typeChange)
        currentChangelogOut += changes
        currentChangelogOut += writepTail()

    currentChangelogOut += writecTail()
    with open(r"./output/wiki/changelog/talent.txt", mode="w") as outfile:
        outfile.write(currentChangelogOut.replace("_", " "))


def main():
    itemChanges = openChangeJSON("Items")
    writeItemsOut(itemChanges)
    enemyChanges = openChangeJSON("Enemies")
    writeEnemiesOut(enemyChanges)
    npcChanges = openChangeJSON("Npcs")
    writeNPCsOut(npcChanges)
    droptableChanges = openChangeJSON("Droptables")
    writeDroptablesOut(droptableChanges)
    alchemyChanges = openChangeJSON("Alchemy")
    writeAlchemyOut(alchemyChanges)
    shopChanges = openChangeJSON("Shops")
    writeShopsOut(shopChanges)
    talentChanges = openChangeJSON("Talents")
    writeTalentOut(talentChanges)


if __name__ == "__main__":
    main()

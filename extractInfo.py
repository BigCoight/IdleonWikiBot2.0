from os import replace
from libs.funcLib import fix, repU
import re
import numpy as np
import csv
from libs.codeReader import CodeReader
from libs.jsonEncoder import CompactJSONEncoder
import combineEnemyData
import combineItemData
import combineNpcData
import combineSkillData
import getNotes


# This is to rename chests eg: chestA3 to Dewdrop Gold Chest
COLNAMES = ["Dewdrop", "Sandstone", "Frostbite", "NYI", "NYI", "NYI", "NYI", "NYI", "NYI"]


def writeJSON(fn, dicti):
    ENCODER = CompactJSONEncoder(indent=4)
    with open(fr"./output/base/json/{fn}.json", mode="w") as outfile:
        outfile.write(ENCODER.encode(dicti))


def strToArray(string):
    return [fix(x) for x in fix(string, ["[", "]", '"', "return", ";"]).split(",") if fix(x)]


def writeCSV(fn, lst):
    if isinstance(lst[0], list) or isinstance(lst[0], tuple):
        with open(fr"./output/base/csv/{fn}.csv", mode="w", newline="") as outfile:
            csv.writer(outfile, delimiter=";").writerows(lst)
    else:
        with open(fr"./output/base/csv/{fn}.csv", mode="w", newline="") as outfile:
            for i in lst:
                outfile.write(str(i) + "\n")


def readSections(codefile):
    reader = CodeReader(codefile)
    reader.addSection('__name__ = "scripts.ItemDefinitions";', "addNewItem = function", "Items")
    reader.addSection("dialogueDefs = new", "finishDialogue", "Quests")
    reader.addSection("scripts.MonsterDefinitions", "};", "Enemies")
    reader.addSection("ItemToCraftNAME = function () {", "}", "AnvilItems")
    reader.addSection("ItemToCraftCostTYPE = function ()", "}", "Recipes")
    reader.addSection("ItemToCraftEXP = function ()", "}", "RecipeLevel")
    reader.addSection("SceneNPCquestInfo = function ()", "}", "QuestNames")
    reader.addSection("MonsterDrops = function ()", "}", "EnemyDropTables")
    reader.addSection("DropTables = function ()", "}", "DropTables")
    reader.addSection("AnvilProductionInfo = function", "}", "Production")
    reader.addSection("ShopNames = function ()", "}", "ShopItems")
    reader.addSection("ShopQTY = function () ", "}", "ShopQTY")
    reader.addSection("ShopLocations = function ()", "}", "ShopLocations")
    reader.addSection("MapDispName = function", "}", "MapNames")
    reader.addSection("MapAFKtarget = function ()", "}", "MapEnemies")
    reader.addSection("PostOfficePossibleOrders = function ()", "}", "PostOffice")
    reader.addSection("FishToolkitInfo = function ()", "}", "FishToolkit")
    reader.addSection("AlchemyDescription = function", "}", "Bubbles")
    reader.addSection("TalentOrder = function ()", "}", "TalentOrder")
    reader.addSection("TalentIconNames = function ()", "}", "TalentNames")
    reader.addSection("TalentDescriptions = function ()", "};", "TalentData")
    reader.addSection("ClassNames = function ()", "}", "ClassNames")
    reader.addSection("atkMoveMap = new ", "};", "ActiveSkill")
    reader.addSection("StatueInfo = function ()", "}", "StatueInfo")
    reader.addSection("CardStuff = function ()", "}", "CardInfo")
    reader.addSection("TaskUnlocks = function ()", "}", "TaskUnlocks")
    reader.readCode()
    return reader


def changeChestNames(intName, name):
    # Changes the colloseum chest names to be more descriptive.
    if intName[:5] == "Chest":
        col = int(intName[6]) - 1
        return f"{COLNAMES[col]}_{name}"
    else:
        return name


def writeMapNamesCSV(reader):
    mapNames = re.findall(r'"([ a-zA-Z0-_\'\n]*)"\.', reader.getSection("MapNames"))[0].split(" ")
    writeCSV("MapNames", mapNames)
    return mapNames


def writeEnemiesNamesCSV(reader):
    mapEnemies = re.findall(r'"([ a-zA-Z0-_\'\n]*)"\.', reader.getSection("MapEnemies"))[0].split(" ")
    writeCSV("MapEnemies", mapEnemies)
    return mapEnemies


def writeShopsJSON(reader, MAPNAMES):
    reElemets = r'"([a-zA-Z0-_ ]*)"\.'
    shopItemData = reader.getSection("ShopItems")
    shopsItems = [x.split(" ") for x in re.findall(reElemets, shopItemData)]
    shopQTYData = reader.getSection("ShopQTY")
    shopsQTYSs = re.findall(reElemets, shopQTYData)
    fixedShopQTY = []
    for shopQTYSs in shopsQTYSs:
        if " " not in shopQTYSs:
            fixedShopQTY.append(list(shopQTYSs))
        else:
            fixedShopQTY.append(shopQTYSs.split(" "))
    shopLocations = reader.getSection("ShopLocations")
    shopsLocations = [MAPNAMES[int(x)] for x in re.findall(r"\[([a-zA-Z0-_ ,]*)\]", shopLocations)[0].split(", ")]
    shopData = {}
    for i in range(len(shopsItems)):
        currentLocation = repU(shopsLocations[i], True)
        for j in range(len(shopsItems[i])):
            if currentLocation in shopData.keys():
                shopData[currentLocation].append({"quantity": fixedShopQTY[i][j], "item": shopsItems[i][j], "no": j})
            else:
                shopData[currentLocation] = [{"quantity": fixedShopQTY[i][j], "item": shopsItems[i][j], "no": j}]
    writeJSON("ShopData", shopData)


def writeRecipesJSON(reader):
    reItems = r'"([a-zA-Z0-_ ]*)"\.'
    anvItemNameData = reader.getSection("AnvilItems")
    anvItemNames = [x.split(" ") for x in re.findall(reItems, anvItemNameData)]
    recipes = []
    recipeData = fix(reader.getSection("Recipes"), ["\n", "  "])
    recipeSections = ["[[" + x + "]]" for x in re.split(r"\],?\],?],\[\[\[", recipeData)]
    levelData = fix(reader.getSection("RecipeLevel"), ["\n", "  "])
    levelSections = ["[[" + x + "]]" for x in re.split(r"\],?],\[\[", levelData)]
    for i, (recipeSection, levelSection) in enumerate(zip(recipeSections, levelSections)):
        if i >= len(anvItemNames):
            break
        temp = {}
        recipeItems = ["[[" + x + "]]" for x in re.split(r"\],?\],\[\[", recipeSection)]
        levelItems = ["[[" + x + "]]" for x in re.split(r"\],\[", levelSection)]
        for j, (item, level) in enumerate(zip(recipeItems, levelItems)):
            recipe = re.findall(r'\["([a-zA-Z0-9_]*)", "([0-9]*)"', item)
            lvlData = re.findall(r'\["([0-9]*)", "([0-9]*)"', level)
            temp[anvItemNames[i][j]] = {
                "recipe": recipe,
                "levelReqToCraft": lvlData[0][0],
                "expGiven": lvlData[0][1],
                "no": j + 1,
                "tab": f"Anvil Tab {i+1}",
            }
        recipes.append(temp.copy())
    # Overrides
    recipes[0]["PeanutG"] = {
        "recipe": [["Peanut", "100"], ["GoldBar", "50"]],
        "levelReqToCraft": 1,
        "expGiven": 1,
        "no": 51,
        "tab": 1,
    }
    recipes[1]["Bullet"] = {
        "recipe": [["ForestTree", "10"], ["Bug1", "10"]],
        "levelReqToCraft": 16,
        "expGiven": 1,
        "no": 43,
        "tab": 2,
    }
    if len(recipes) > 2:
        del recipes[2]["Bullet"]

    writeJSON("Recipes", recipes)


def addQuestNames(reader):
    reNames = r'\["([^ ]*)", "([^ ]*)", "([^ ]*)", "([^ ]*)"\],'
    questNameData = reader.getSection("QuestNames")
    questNames = re.findall(reNames, questNameData)
    return questNames


def addDroptables(reader):
    reEnemies = r'.\.setReserved\("([a-zA-Z0-9_]*)", [a-zA-Z0-9_$]*\)'
    reDrops = r'\["([^ ]*)", "([^ ]*)", "([^ ]*)", "([^ ]*)"\],'
    droptableData = reader.getSection("EnemyDropTables")
    droptables = re.split(reEnemies, droptableData)
    tables = {}
    for i in range(0, len(droptables) - 1, 2):
        tables[droptables[i + 1]] = re.findall(reDrops, droptables[i])
    return tables


def writeProductionCSV(reader):
    reProd = r'\["([^ ]*)", "([^ ]*)", "([^ ]*)", "([^ ]*)"\],'
    prodData = reader.getSection("Production")
    writeCSV("Production", re.findall(reProd, prodData))


def writeItemJSON(reader):
    reNames = r'.\.addNew[a-zA-Z0-9_]*\("([a-zA-Z0-9_]*)", ..?\);'
    reData = r'..\.setReserved\("([a-zA-Z0-9_]*)", ?"?([^\s"]*)"?\)'
    items = {}
    itemText = fix(reader.getSection("Items"), ["\n", "  "])
    itemData = re.split(reNames, itemText)
    for i in range(0, len(itemData), 2):
        if data := re.findall(reData, itemData[i]):
            itemName = itemData[i + 1]
            items[itemName] = {}
            item = items[itemName]
            for atr, val in data:
                item[atr] = fix(val)
            item["displayName"] = repU(item["displayName"], True)
            item["Type"] = repU(item["Type"])
            if "Class" in item.keys():
                item["Class"] = item["Class"].title()
    items["Quest5"]["displayName"] = "Golden Jam (Quest)"
    writeJSON("Items", items)


def writeQuestJSON(reader):
    reNpcs = r'..\.addDialogueFor\("([a-zA-Z0-9_]*)", [^\s"]*\)'
    reQuest = r"\.addLine_([a-zA-Z]*)\({"
    reQData = r" ?,?([a-zA-Z]*): "
    npcs = {}
    questText = fix(reader.getSection("Quests"), ["\n"])
    questData = re.split(reNpcs, questText)

    for i in range(1, len(questData), 2):
        if quests := re.split(reQuest, questData[i + 1]):
            npcName = repU(questData[i], True)
            npcs[npcName] = []
            for j in range(1, len(quests), 2):
                if data := re.split(reQData, quests[j + 1]):
                    temp = {"Type": quests[j]}
                    for k in range(1, len(data), 2):
                        atr = fix(data[k])
                        val = fix(data[k + 1], ['"', ",})", " })", ";"])
                        val = strToArray(val) if "[" in val else fix(val, [","])
                        temp[atr] = repU(val, True)
                    npcs[npcName].append(temp.copy())

    for questName, npc, diff, index in addQuestNames(reader):
        if index == "f":
            continue
        index = int(index)
        npcName = repU(npc, True)
        npcs[npcName][index]["Name"] = repU(questName, True)
        npcs[npcName][index]["Difficulty"] = diff
    writeJSON("Npcs", npcs)


def writeEnemiesJSON(reader):
    reName = r'..\.addNewMonster\("([a-zA-Z0-9_]*)", {'
    reData = r'([a-zA-Z0-9_]*): "?([a-zA-Z0-9_.\]\[, ]*)"?,'
    enemies = {}
    enemiesText = reader.getSection("Enemies")
    enemiesData = re.split(reName, enemiesText)
    droptables = addDroptables(reader)
    for i in range(1, len(enemiesData), 2):
        intName = enemiesData[i]
        enemies[intName] = {}
        data = enemiesData[i + 1]
        splitData = re.findall(reData, data)
        for atr, val in splitData:  # add every attribute to the dictionary
            val = strToArray(val) if "[" in val else fix(val, [","])
            enemies[intName][fix(atr)] = val
        # IF the enemy has a drotpable, it should but lava (tm)
        if droptable := droptables.get(intName):
            enemies[intName]["Drops"] = droptable.copy()
        if intName[:5] == "Chest":  # If we need to change the name of the cols
            enemies[intName]["Name"] = changeChestNames(intName, enemies[intName]["Name"])
        enemies[intName]["Name"] = repU(enemies[intName]["Name"], True)

    # for toIgnore in ["ForgeA","ForgeB","Bandit_Bob","SoulCard1","SoulCard2","SoulCard3","SoulCard4","SoulCard5","SoulCard6","CritterCard1","CritterCard2","CritterCard3","CritterCard4","CritterCard5","CritterCard6","CritterCard7","CritterCard8","CritterCard9"]:
    #     del enemies[toIgnore]
    writeJSON("Enemies", enemies)


def writeDroptablesJSON(reader):
    reEnemies = r'.\.setReserved\("([a-zA-Z0-9_]*)", [a-zA-Z0-9_$]*\)'
    reDrops = r'\["([^ ]*)", "([^ ]*)", "([^ ]*)", "([^ ]*)"\],'
    droptableData = reader.getSection("DropTables")
    droptables = re.split(reEnemies, droptableData)
    tables = {}
    for i in range(0, len(droptables) - 1, 2):
        tables[droptables[i + 1]] = re.findall(reDrops, droptables[i])
    obols = []
    for i in range(12):  # Obolsu
        if i < 4:
            obols.append([f"ObolBronze{i}", str(0.0006 * (1 + 1 / 20)), "1", "N/A"])
        elif i < 8:
            obols.append([f"ObolSilver{i-4}", str(0.0006 * (1 + 1 / 20)), "1", "N/A"])
        elif i == 8:
            obols.append([f"ObolSilverMoney", str(0.027 * (1 + 1 / 20)), "1", "N/A"])
        elif i == 9:
            obols.append([f"ObolSilverDamage", str(0.027 * (1 + 1 / 20)), "1", "N/A"])
        elif i == 10:
            obols.append([f"ObolGold3", str(0.021 * (1 + 1 / 20)), "1", "N/A"])
        elif i == 11:
            obols.append([f"ObolSilverLuck", str(0.021 * (1 + 1 / 20)), "1", "N/A"])
        if i < 4:
            tables[f"DropTable{i+1}"].insert(-1, obols[i])
        elif i < 8:
            tables[f"DropTable{i+2}"].insert(-1, obols[i])
        elif i < 10:
            tables[f"SuperDropTable1"].insert(-1, obols[i])
        elif i < 12:
            tables[f"SuperDropTable2"].insert(-1, obols[i])
    writeJSON("Droptables", tables)


def writePostOfficeJSON(reader):
    postNames = ["Simple Shippin", "Plan-it Express", "Dudes Next Door"]
    # DO LATER SIMILAR TO addRecipes()
    postData = fix(reader.getSection("PostOffice"), ["\n", "  "])
    postOfficeData = {}
    postOffices = ["[[" + x + "]]" for x in re.split(r"\],?\],?],\[\[\[", postData)]
    for j, postOffice in enumerate(postOffices):
        if j >= len(postNames):
            break
        category = ["[[" + x + "]]" for x in re.split(r",?\],?],\[\[", postOffice)]
        temp = {}
        for n, v in enumerate(["Orders", "Rewards"]):
            itemData = re.split(r"]\,\[", category[n])
            temp[v] = {}
            for i in itemData:
                data = strToArray(i)
                if len(data) > 3:
                    temp[v]["COIN"] = data
                else:
                    temp[v][data[0]] = {"Base": data[1], "Increment": data[2]}
        postOfficeData[postNames[j]] = temp.copy()

    writeJSON("PostOffice", postOfficeData)


def writeFishingTKJSON(reader):
    dataNames = ["Name", "Depth1", "Depth2", "Depth3", "Depth4", "FishingExp", "FishingSpeed", "FishingPower"]
    fishingTK = {}
    fishingTKData = fix(reader.getSection("FishToolkit"), ["  ", "\n"])
    section = re.split(r"\],\[", fishingTKData)
    for n, v in enumerate(["Weight", "Line"]):
        datas = re.findall(r'"([a-zA-Z0-9_ ]*)"\.', section[n])
        fishingTK[v] = []
        for data in datas:
            fishingTK[v].append(dict(zip(dataNames, data.split(" "))))
    writeJSON("FishingTK", fishingTK)


def writeBubbleJSON(reader):
    bubbleNames = ["Power Cauldron", "Quicc Cauldron", "High-IQ Cauldron", "Kazam Cauldron", "Vials", "Liquid Shop", "??"]
    cauldrens = {}
    bubbleData = reader.getSection("Bubbles").split("],")
    reEverything = r'"([a-zA-Z0-9_ +{}\',.\-%!$:`?;\n\]\(\)]*)"\.'
    for n, v in enumerate(bubbleData):
        bubbles = re.findall(reEverything, v)
        cauldrens[bubbleNames[n]] = {}
        for bubble in bubbles:
            bubData = bubble.split(" ")
            bubData[0] = repU(bubData[0])
            if bubData[0] not in cauldrens[bubbleNames[n]].keys() and bubData[-1] != "Filler":
                if len(bubData) < 9:
                    continue
                cauldrens[bubbleNames[n]][bubData[0]] = {
                    "x1": bubData[1],
                    "x2": bubData[2],
                    "func": bubData[3],
                    "description": bubData[9],
                }
                cauldrens[bubbleNames[n]][bubData[0]]["requirements"] = []
                for i, j in zip([5, 6, 7, 8], [11, 12, 13, 14]):
                    if bubData[i] == "Blank":
                        break
                    if len(bubData) >= 14:
                        cauldrens[bubbleNames[n]][bubData[0]]["requirements"].append([bubData[i], bubData[j]])
                    else:
                        cauldrens[bubbleNames[n]][bubData[0]]["requirements"].append([bubData[i], "L"])
    writeJSON("Cauldrens", cauldrens)


def writeTalentJSON(reader):
    talents = {}
    talentDescNames = ["Description", "X1", "X2", "FuncX", "Y1", "Y2", "FuncY", "Level Up Text", "Active Skill"]
    reEverything = r'"([a-zA-Z0-9_ +{}\',.\-%!$:`?;\n\]\(\)]*)"\.'
    talentOrder = [int(x) for x in strToArray(reader.getSection("TalentOrder"))]
    talentNames = re.findall(reEverything, reader.getSection("TalentNames"))[0].split(" ")
    reTalentDesc = r'\[\["(.*)"\], "(.*)"\.split\(" "\), \["(.*)"\], \["(.*)"\]\]'
    talentDescs = [" ".join(x).split(" ") for x in re.findall(reTalentDesc, reader.getSection("TalentData"))]
    classNames = re.findall(reEverything, reader.getSection("ClassNames"))[0].split(" ")[1:]
    specialTalents = []
    for n, i in enumerate([41, 42, 43, 44, 45], 1):
        specialTalents.append(f"Special Talent {n}")
    writeCSV("ClassNames", classNames)
    writeCSV("TalentDescriptions", talentDescs)
    writeCSV("TalentNames", talentNames)
    writeCSV("TalentOrder", talentOrder)

    # Active skill information
    activeDict = {}
    activeData = reader.getSection("ActiveSkill")
    activeDataSplit = re.split(r'..\.addAtkMoveDef\("([a-zA-Z0-9_ +{}\',.\-%!$:`?;\n\]\(\)]*)"', activeData)[1:]
    reData = r'([\w]*): ([\w."\-]*)'
    for i in range(0, len(activeDataSplit) - 1, 2):
        activeDict[activeDataSplit[i]] = {}
        activeDetails = re.findall(reData, activeDataSplit[i + 1])
        for atr, val in activeDetails:
            activeDict[activeDataSplit[i]][atr] = fix(val, ['"'])
    writeJSON("ActiveDetails", activeDict)

    def doTalents(arr, off, mod):
        for n, name in enumerate(arr):
            if name == "_":
                continue
            talents[name] = {}
            for i in range(mod):
                skillI = int(talentOrder[off + n * mod + i])
                talentName, talentDesc = talentNames[skillI], talentDescs[skillI]
                if talentName == "_":
                    continue
                talents[name][talentName] = {}
                for atr, val in zip(talentDescNames, talentDesc):
                    if val not in ["_", "txt"] and atr != "Active Skill":
                        talents[name][talentName][atr] = val
                if activeD := activeDict.get(talentName):
                    talents[name][talentName]["Active Data"] = activeD

    doTalents(classNames[:41], 0, 15)
    doTalents(specialTalents, 615, 13)
    writeJSON("Talents", talents)


def writeCustomSourcesJSON():
    custSources = {}
    custSources["[[Gem Shop]]"] = [
        "CardPack2",
        "CardPack1",
        "ResetBox",
        "ClassSwap",
        "ResetCompletedS",
        "ResetCompleted",
        "InvBag21",
        "InvBag22",
        "InvBag23",
        "InvBag24",
        "InvBag25",
        "InvStorage31",
        "InvStorage32",
        "InvStorage33",
        "InvStorage34",
        "InvStorage35",
        "InvStorage36",
        "InvStorage37",
        "InvStorage38",
        "InvStorage39",
        "InvStorage40",
        "InvStorage41",
        "InvStorage42",
        "Timecandy1",
        "Timecandy2",
        "Timecandy3",
        "Timecandy4",
        "EquipmentRingsChat1",
        "EquipmentRingsChat2",
        "EquipmentRingsChat4",
        "EquipmentRingsChat5",
        "EquipmentRingsChat6",
        "EquipmentRingsChat3",
        "EquipmentRingsChat9",
        "EquipmentHats35",
        "EquipmentHats50",
        "EquipmentHats49",
        "Ht",
        "EquipmentHats48",
        "EquipmentHats47",
        "EquipmentHats46",
        "StonePremSTR",
        "StonePremWIS",
        "StonePremLUK",
        "StonePremAGI",
        "StonePremRestore",
        "EquipmentHats31",
        "EquipmentHats34",
        "EquipmentHats33",
        "EquipmentHats38",
        "EquipmentHats32",
        "EquipmentHats37",
        "EquipmentHats40",
        "EquipmentHats36",
        "CardPack3",
        "EquipmentRingsChat8",
        "EquipmentHats43",
        "EquipmentHats45",
        "EquipmentHats57",
        "EquipmentHats62",
    ]
    custSources["Starter Hat"] = ["EquipmentHats14", "EquipmentHats11", "EquipmentHats13", "EquipmentHats12"]
    custSources["[[Alchemy#Level up Gift|Level up Gift]]"] = ["EquipmentHats21", "PremiumGem", "Timecandy1", "Timecandy2", "Timecandy3", "Timecandy4", "Timecandy5", "Line6", "StoneZ1", "FoodPotYe1", "FoodPotYe2", "FoodPotYe3", "StampC9", "Quest25", "EquipmentStatues1", "EquipmentStatues2", "EquipmentStatues3", "EquipmentStatues4", "EquipmentStatues5", "EquipmentStatues6", "EquipmentStatues7", "EquipmentStatues8"]
    custSources["[[Guild Giftbox]]"] = ["Trophy9", "FoodPotYe3", "FoodPotYe2", "PremiumGem", "StoneA3b", "StoneW2", "StoneA2", "StonePremLUK", "StoneHelm6", "StoneW6", "ExpBalloon1", "ExpBalloon2", "ExpBalloon3", "ResetFrag", "Timecandy4", "Timecandy3", "Timecandy2", "Timecandy1"]
    custSources["Start"] = ["StampA1", "StampA2"]
    custSources["[[Alchemy#Liquid Shop|Mediocre Obols]]"] = ["ObolBronze0", "ObolBronze1", "ObolBronze2", "ObolBronze3", "ObolBronzeMining", "ObolBronzeChoppin", "ObolBronzeDamage"]
    custSources["[[Alchemy#Liquid Shop|Decent Obols]]"] = ["ObolBronze0", "ObolBronze1", "ObolBronze2", "ObolBronze3", "ObolSilverDamage", "ObolBronzeFishing", "ObolBronzeCatching", "ObolSilverFishing", "ObolSilverChoppin", "ObolSilverCatching", "ObolSilverMining", "ObolSilver0", "ObolSilver1", "ObolSilver2", "ObolSilver3"]
    custSources["[[Alchemy#Liquid Shop|Weak UPG Stone]]"] = ["StoneW1", "StoneA1", "StoneT1", "StoneHelm1", "StoneA1b"]
    custSources["[[Trapping]]"] = ["CritterCard1", "CritterCard2", "CritterCard3", "CritterCard4", "CritterCard5", "CritterCard6", "CritterCard7"]
    custSources["[[Worship]]"] = ["SoulCard1", "SoulCard2", "SoulCard3", "SoulCard4", "SoulCard5"]
    custSources["[[Construction#Refinery|Refinery]]"] = ["Refinery1", "Refinery2", "Refinery3", "Refinery4"]
    custSources["[[Tiki Chief#Three Strikes, you're Out!|Three Strikes, you're Out!]]"] = ["Quest11"]
    custSources["Has a 1/1M chance to drop from active kills if the Blue Hedgehog [[Star Signs|Starsign]] is equipped."] = ["EquipmentRings15"]
    custSources["[[Alchemy#Level up Gift|Level up Gift (however this item has no use anymore)]]"] = ["Quest26"]
    # custSources["[[Picnic Stowaway#Afternoon Tea in a Jiffy|Afternoon Tea in a Jiffy]]"] = ["Quest10"]

    writeJSON("CustomSources", custSources)


def writeCardJSON(reader):
    cardNames = {"A": "Blunder Hills", "B": "Yum Yum Desert", "C": "Easy Resources", "D": "Medium Resources", "E": "Frostfire Tyundra", "F": "Hard Resources", "Z": "Bosses", "Y": "Event"}
    cardDict = {x: {} for x in cardNames.values()}
    cardData = fix(reader.getSection("CardInfo"), ["\n", "  "])
    for n, section in enumerate(["[[" + x + "]]" for x in re.split(r",?\],?],\[\[", cardData)]):
        for m, data in enumerate(["[[" + x + "]]" for x in re.split(r",?],\[", section)]):
            arrayData = strToArray(data)
            cardSection = arrayData[1][0]
            cardDict[cardNames[cardSection]][arrayData[0]] = [repU(x, True).replace("{", "") for x in arrayData[1:]] + [str(m)]
    writeJSON("CardData", cardDict)


def writeStatueCSV(reader):
    res = []
    statueData = reader.getSection("StatueInfo").split("\n")[1:-1]
    for data in statueData:
        res.append(strToArray(data))

    writeCSV("StatueData", res)


def writeTaskUnlocks(reader):
    TaskUnlocks = []
    unlockData = fix(reader.getSection("TaskUnlocks"), ["\n", "  "])
    taskUnlocks = ["[[" + x + "]]" for x in re.split(r"\],?\],?],\[\[\[", unlockData)]
    for j, taskUnlock in enumerate(taskUnlocks):
        if j >= 3:
            break
        categories = ["[[" + x + "]]" for x in re.split(r",?\],?],\[\[", taskUnlock)]
        temp = []
        for category in categories:
            items = ["[" + x + "]" for x in re.split(r",?],\[", category)]
            for ite in items:
                ite = strToArray(ite)
                temp.append(ite[0])
        TaskUnlocks.append(temp[:])
    writeJSON("TaskUnlocks", TaskUnlocks)


def main(codefile):
    reader = readSections(codefile)
    MAPNAMES = writeMapNamesCSV(reader)
    MAPENEMIES = writeEnemiesNamesCSV(reader)
    writeProductionCSV(reader)
    writeShopsJSON(reader, MAPNAMES)
    writeItemJSON(reader)
    writeQuestJSON(reader)
    writeEnemiesJSON(reader)
    writeDroptablesJSON(reader)
    writeRecipesJSON(reader)
    writePostOfficeJSON(reader)
    writeFishingTKJSON(reader)
    writeBubbleJSON(reader)
    writeTalentJSON(reader)
    writeCustomSourcesJSON()
    writeCardJSON(reader)
    writeStatueCSV(reader)
    writeTaskUnlocks(reader)

    combineItemData.main()
    combineEnemyData.main()
    combineNpcData.main()
    combineSkillData.main()


if __name__ == "__main__":
    main(r"./input/codefile/idleon120b.txt")


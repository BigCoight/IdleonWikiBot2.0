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


# This is to rename chests eg: chestA3 to Dewdrop Gold Chest
COLNAMES = ["Dewdrop", "Sandstone", "Chillsnap", "NYI", "NYI", "NYI", "NYI", "NYI", "NYI"]


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
    reader.addSection("RefineryInfo = function ()", "}", "RefineryCost")
    reader.addSection("TowerInfo = function () {", "};", "BuildingData")
    reader.addSection("SaltLicks = function () {", "};", "SaltLicks")
    reader.addSection("MTXinfo = function () {", "};", "GemShop")
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
    reNames = r'.\.addNew[a-zA-Z0-9_]*\("([a-zA-Z0-9_]*)", ..?.?\);'
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


def writeTowerJson(reader: CodeReader):
    towerData = fix(reader.getSection("BuildingData"), ["  ", "\n"])
    buildings = re.findall(r'"([ a-zA-Z0-_\'\n\(\)@,!$+\{\}%:\.]*)"\.', towerData)
    buildings = [x.split(" ") for x in buildings]
    buildingData = {}
    for building in buildings:
        curBuilding = repU(building[0], True)
        buildingData[curBuilding] = {}
        current = buildingData[curBuilding]
        data = building[1:]
        data[0] = repU(data[0], True)
        desc = data[0].split("@")
        current["desc"] = data[0].split("@")[0]
        if len(desc) > 2:
            current["currentBonus"] = desc[2]
        current["lvlUpReq"] = [[data[3], data[5]], [data[4], data[6]]]
        current["maxLvl"] = data[7]
        current["costIncrement"] = data[8]
        current["lvlInc"] = data[1:3]
        current["dunno"] = data[-1]
    writeJSON("BuildingData", buildingData)


def writeSaltLickCSV(reader: CodeReader):
    saltLickData = fix(reader.getSection("SaltLicks"), ["  ", "\n"])
    saltLicks = re.findall(r'"([ a-zA-Z0-_\'\n\(\)@,!$+\{\}%:\.]*)"\.', saltLickData)
    saltLicks = [x.split(" ") for x in saltLicks]
    writeCSV("SaltLicks", saltLicks)


def writeEnemiesJSON(reader):
    reName = r'..\.addNewMonster\("([a-zA-Z0-9_]*)", {'
    reData = r'([a-zA-Z0-9_]*): "?([a-zA-Z0-9_.\]\[, \$]*)"?,'
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
    for i in range(12):  # Obols1
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

    tables["DropTable14"].insert(-1, [f"ObolBronzeWorship", str(9e-4 * (1 + 1 / 20)), "1", "N/A"])
    tables["DropTable15"].insert(-1, [f"ObolBronzeTrapping", str(9e-4 * (1 + 1 / 20)), "1", "N/A"])
    tables["DropTable16"].insert(-1, [f"ObolBronzeCons", str(9e-4 * (1 + 1 / 20)), "1", "N/A"])
    tables["SuperDropTable1"].insert(-1, [f"ObolBronzeEXP", str(0.029 * (1 + 1 / 20)), "1", "N/A"])
    tables["SuperDropTable3"].insert(-1, [f"ObolBronzeKill", str(0.029 * (1 + 1 / 20)), "1", "N/A"])
    tables["SuperDropTable2"].insert(-1, [f"ObolBronzeDef", str(0.029 * (1 + 1 / 20)), "1", "N/A"])

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


def getGemShopObols():
    gold = "ObolSilver0 7 ObolSilver1 14 ObolSilver2 21 ObolSilver3 28 ObolSilverCard 32 ObolSilverCatching 37 ObolSilverChoppin 42 ObolSilverFishing 47 ObolSilverMining 52 ObolSilverDamage 60 ObolSilverDef 64 ObolSilverEXP 65 ObolSilverMoney 67 ObolGold0 70 ObolGold1 73 ObolGold2 76 ObolGold3 78 ObolGoldMoney 79 ObolGoldCard 80 ObolGoldKill 82 ObolGoldChoppin 84 ObolGoldMining 86 ObolGoldLuck 88 ObolGoldCatching 90 ObolGoldFishing 92 ObolGoldEXP 93 ObolGoldDef 95 ObolGoldDamage 100".split(" ")
    plat = "ObolGold0 7 ObolGold1 14 ObolGold2 21 ObolGold3 28 ObolGoldMoney 32 ObolGoldCard 34 ObolGoldKill 36 ObolGoldChoppin 41 ObolGoldMining 46 ObolGoldLuck 47 ObolGoldCatching 52 ObolGoldFishing 57 ObolGoldDamage 63 ObolGoldEXP 64 ObolGoldDef 65 ObolPlatinum0 67 ObolPlatinum1 69 ObolPlatinum2 71 ObolPlatinum3 73 ObolPlatinumCard 74 ObolPlatinumCatching 76 ObolPlatinumChoppin 78 ObolPlatinumDamage 81 ObolPlatinumDef 82 ObolPlatinumEXP 83 ObolPlatinumFishing 85 ObolPlatinumKill 86 ObolPlatinumMining 88 ObolPlatinumPop 89 ObolPlatinumLuck 90 ObolPink0 91 ObolPink1 92 ObolPink2 93 ObolPink3 94 ObolPinkCard 94.5 ObolPinkCatching 95 ObolPinkDamage 96 ObolPinkDef 95.5 ObolPinkEXP 97 ObolPinkFishing 98 ObolPinkKill 98.4 ObolPinkLuck 99.2 ObolPinkMining 99.8 ObolPinkPop 100".split(
        " "
    )
    dtGold = []
    prev = 0.0
    for i in range(0, len(gold), 2):
        dtGold.append([gold[i], str((float(gold[i + 1]) - prev) / 100), "1", "N/A"])
        prev = float(gold[i + 1])
    dtPlat = []
    prev = 0
    for i in range(0, len(plat), 2):
        dtPlat.append([plat[i], str((float(plat[i + 1]) - prev) / 100), "1", "N/A"])
        prev = float(plat[i + 1])
    return dtGold, dtPlat


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
    custSources["[[Alchemy#Level up Gift|Level up Gift]]"] = ["StampA23", "EquipmentHats21", "PremiumGem", "Timecandy1", "Timecandy2", "Timecandy3", "Timecandy4", "Timecandy5", "Line6", "StoneZ1", "FoodPotYe1", "FoodPotYe2", "FoodPotYe3", "StampC9", "Quest25", "EquipmentStatues1", "EquipmentStatues2", "EquipmentStatues3", "EquipmentStatues4", "EquipmentStatues5", "EquipmentStatues6", "EquipmentStatues7", "EquipmentStatues8"]
    custSources["[[Guild Giftbox]]"] = ["Trophy9", "FoodPotYe3", "FoodPotYe2", "PremiumGem", "StoneA3b", "StoneW2", "StoneA2", "StonePremLUK", "StoneHelm6", "StoneW6", "ExpBalloon1", "ExpBalloon2", "ExpBalloon3", "ResetFrag", "Timecandy4", "Timecandy3", "Timecandy2", "Timecandy1"]
    custSources["Start"] = ["StampA1", "StampA2", "StampB1", "StampB2"]
    custSources["[[Alchemy#Liquid Shop|Mediocre Obols]]"] = ["ObolBronze0", "ObolBronze1", "ObolBronze2", "ObolBronze3", "ObolBronzeMining", "ObolBronzeChoppin", "ObolBronzeDamage"]
    custSources["[[Alchemy#Liquid Shop|Decent Obols]]"] = ["ObolBronze0", "ObolBronze1", "ObolBronze2", "ObolBronze3", "ObolSilverDamage", "ObolBronzeFishing", "ObolBronzeCatching", "ObolSilverFishing", "ObolSilverChoppin", "ObolSilverCatching", "ObolSilverMining", "ObolSilver0", "ObolSilver1", "ObolSilver2", "ObolSilver3"]
    custSources["[[Alchemy#Liquid Shop|Grand Obols]]"] = ["ObolSilverDamage", "ObolBronze0", "ObolBronze1", "ObolBronze2", "ObolBronzeCons", "ObolBronzeKill", "ObolBronzeDef", "ObolBronzeTrapping", "ObolBronzeWorship", "ObolSilverTrapping", "ObolSilverWorship", "ObolSilverCons", "ObolSilver0", "ObolSilver1", "ObolSilver2", "ObolGold", "ObolGoldCard"]
    custSources["[[Alchemy#Liquid Shop|Weak UPG Stone]]"] = ["StoneW1", "StoneA1", "StoneT1", "StoneHelm1", "StoneA1b"]
    custSources["[[Trapping]]"] = ["CritterCard1", "CritterCard2", "CritterCard3", "CritterCard4", "CritterCard5", "CritterCard6", "CritterCard7"]
    custSources["[[Worship]]"] = ["SoulCard1", "SoulCard2", "SoulCard3", "SoulCard4", "SoulCard5"]
    custSources["[[Tiki Chief#Three Strikes, you're Out!|Three Strikes, you're Out!]]"] = ["Quest11"]
    custSources["Has a 1/1M chance to drop from active kills if the Blue Hedgehog [[Star Signs|Starsign]] is equipped."] = ["EquipmentRings15"]
    custSources["[[Alchemy#Level up Gift|Level up Gift (however this item has no use anymore)]]"] = ["Quest26"]
    custSources["[[TP Pete]]"] = ["NPCtoken15"]
    custSources["[[Krunk]]"] = ["NPCtoken10"]

    dtGold, dtPlat = getGemShopObols()
    custDropTables = {"Quality Obol Stack": dtGold, "Marvelous Obol Stack": dtPlat}

    for custDropTable, drops in custDropTables.items():
        custSources[f"[[Gem Shop#{custDropTable}|{custDropTable}]]"] = []
        current = custSources[f"[[Gem Shop#{custDropTable}|{custDropTable}]]"]
        for drop in drops:
            current.append(drop[0])

    custRecipeFrom = {}
    custRecipeFrom["Start"] = [
        "EquipmentPunching1",
        "TestObj1",
        "EquipmentBows1",
        "EquipmentWands1",
        "EquipmentHats1",
        "EquipmentShirts1",
        "EquipmentPants1",
        "EquipmentShoes9",
        "EquipmentTools2",
        "MaxCapBag1",
        "EquipmentToolsHatchet3",
        "MaxCapBag7",
        "EquipmentHats15",
        "EquipmentPunching2",
        "MaxCapBag8",
        "MaxCapBagM2",
        "EquipmentHats17",
        "EquipmentShirts11",
        "EquipmentPants2",
        "EquipmentShoes1",
        "EquipmentTools3",
        "MaxCapBag2",
        "EquipmentToolsHatchet1",
        "MaxCapBag9",
        "EquipmentHats18",
        "EquipmentShirts12",
        "EquipmentPants3",
        "EquipmentSmithingTabs2",
        "WorshipSkull2",
        "MaxCapBagS1",
        "TrapBoxSet2",
        "MaxCapBagTr1",
        "EquipmentHats28",
        "EquipmentShirts13",
        "EquipmentPants4",
        "EquipmentShoes3",
        "MaxCapBagF3",
        "MaxCapBagM4",
        "EquipmentHats19",
        "EquipmentShirts14",
        "EquipmentPants5",
        "EquipmentShoes4",
        "EquipmentSmithingTabs3",
        "Quest13",
        "EquipmentHats53",
        "EquipmentShirts15",
        "EquipmentPants6",
        "EquipmentShoes5",
        "MaxCapBagF5",
        "MaxCapBagM6",
        "EquipmentHats54",
        "EquipmentShirts27",
        "EquipmentPants21",
        "EquipmentShoes22",
    ]
    custRecipeFrom["[[Scripticus#Champion of the Grasslands|Champion of the Grasslands]]"] = ["BadgeG1", "BadgeG2", "BadgeG3", "NPCtoken1", "NPCtoken2", "NPCtoken3"]
    custRecipeFrom["[[Picnic Stowaway#Brunchin' with the Blobs|Brunchin' with the Blobs]]"] = ["Peanut"]

    writeJSON("CustomSources", custSources)
    writeJSON("CustomRecipeFrom", custRecipeFrom)
    writeJSON("CustomDropTables", custDropTables)


def writeCardJSON(reader):
    cardNames = ["Blunder Hills", "Yum Yum Desert", "Easy Resources", "Medium Resources", "Frostbite Tundra", "Hard Resources", "Bosses", "Event"]
    cardDict = {x: {} for x in cardNames}
    cardData = fix(reader.getSection("CardInfo"), ["\n", "  "])
    for n, section in enumerate(["[[" + x + "]]" for x in re.split(r",?\],?],\[\[", cardData)]):
        for m, data in enumerate(["[[" + x + "]]" for x in re.split(r",?],\[", section)]):
            arrayData = strToArray(data)
            cardDict[cardNames[n]][arrayData[0]] = [repU(x, True).replace("{", "") for x in arrayData[1:]] + [str(m)]
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


def writeGemShopCSV(reader: CodeReader):
    gemShopData = fix(reader.getSection("GemShop"), ["  ", "\n"])
    gemShops = re.findall(r'"([ a-zA-Z0-_\'\n\(\)@,!$+\{\}%:\.]*)"\.', gemShopData)
    gemShops = [x.split(" ") for x in gemShops]
    for gemShop in gemShops:
        gemShop[1] = repU(gemShop[1])
        gemShop[2] = repU(gemShop[2], True)
    writeCSV("GemShop", gemShops)


def writeRefineryCost(reader):
    refCosts = reader.getSection("RefineryCost")
    refSlots = re.findall(r'"([ a-zA-Z0-_\'\n]*)"\.', refCosts)
    refSlots = [x.split(" ") for x in refSlots]
    refineryCosts = {}
    for refSlot in refSlots:
        slotName = refSlot[12]
        refineryCosts[slotName] = []
        for i in range(6):
            if refSlot[i] == "Blank":
                continue
            refineryCosts[slotName].append([refSlot[i], refSlot[i + 6]])

    writeJSON("RefineryCosts", refineryCosts)


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
    writeRefineryCost(reader)
    writeTowerJson(reader)
    writeSaltLickCSV(reader)
    writeGemShopCSV(reader)

    combineItemData.main()
    combineEnemyData.main()
    combineNpcData.main()
    combineSkillData.main()


if __name__ == "__main__":
    main(r"./input/codefile/idleon122d.txt")


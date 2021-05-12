import json
import numpy as np
from libs.funcLib import fix, repU
from libs.jsonEncoder import CompactJSONEncoder
import getNotes


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


def combineDescription(data):
    # Add in all the desc lines to one attribute
    # Checks if we first have a description to merge
    start = 1
    if 'desc_line1' not in data.keys():
        if 'desc_line2' not in data.keys():
            return
        else:
            start = 2
    # Now merges
    desc = []
    for i in range(start, 9):
        if data[f'desc_line{i}'] != "Filler":
            desc.append(repU(data[f'desc_line{i}'], True))
        del data[f'desc_line{i}']
    data['description'] = desc


def addAtrToDesc(data):
    # Replaces [ with amount and ] with cooldown
    if 'description' not in data.keys():
        return
    if data["Type"] == "Golden Food":
        return
    newDesc = []
    for line in data['description']:
        added = False
        if '[' in line:
            newDesc.append(line.replace('[', data['Amount']))
            del data['Amount']
            added = True
        if ']' in line:
            newDesc.append(line.replace(']', data['Cooldown']))
            del data['Cooldown']
            added = True
        if '*' in line:
            newDesc.append(line.replace('*', data["Amount"]))
            del data["Amount"]
            added = True
        if '#' in line and "Trigger" in data.keys():
            newDesc.append(line.replace('#', data["Trigger"]))
            del data["Trigger"]
            added = True
        if not added:
            newDesc.append(line)

    data['description'] = newDesc


def splitStampData(data):
    stampTypes = ["Combat", "Skills", "Misc"]
    # Split the stamp data into a sub atribute
    stampData = data['description'][0].split(',')
    del data['description']
    num = data['ID']
    ind = 0
    if len(num) > 2:
        ind = int(num[0])

    data['Type'] = stampTypes[ind]
    data['ID'] = str(int(num[-2:])+1)
    data['stampData'] = [getDisp(fix(x)) for x in stampData]


def addUpgradeData(data):
    upgrades = data["Effect"].split('.')
    upgrades.reverse()
    del data["Effect"]
    for upgrade in upgrades:
        up, no = upgrade.split(',')
        data['description'].insert(1, f'+{no} {repU(up)}')


def allItemsStart(items):
    typeToSource = {
        "bOre": "Mining",
        'bBar': "Forging",
        'bLog': "Choppin",
        'bLeaf': "Choppin",
        'dFish': "Fishing",
        'dBugs': "Catching",
        'dCritters': "Trapping",
        'dSouls': "Worshiping?",
    }
    for name, data in items.items():
        data['sources'] = []
        data['detdrops'] = []
        data['uses'] = []
        combineDescription(data)
        addAtrToDesc(data)
        typeGen = data["typeGen"]
        if typeGen == "aStamp":
            splitStampData(data)
        elif typeGen == "dStone":
            addUpgradeData(data)
        if source := typeToSource.get(typeGen):
            data["sources"].append(source)
        if "UQ1val" in data.keys() and "UQ1txt" in data.keys():
            if data["UQ1val"] != '0':
                data["miscUp1"] = data["UQ1val"] + repU(data["UQ1txt"])
                del data["UQ1val"]
                del data["UQ1txt"]
            if data["UQ2val"] != '0':
                data["miscUp2"] = data["UQ2val"] + repU(data["UQ2txt"])
                del data["UQ2val"]
                del data["UQ2txt"]


def allItemsEnd(items):
    for name, data in items.items():
        if data["typeGen"] == "aStamp":
            if item := items.get(data["stampData"][5]):
                item["uses"].append((f'[[{nameDic[name]}]]', "Lots", "Stamps"))
        elif data['typeGen'] == "aCarryBag":
            materialBagDesc(data)
        elif data["typeGen"] != 'aWeapon':
            if "Speed" in data.keys() or "Reach" in data.keys():
                del data["Speed"]
                del data["Reach"]
        if data["detdrops"]:
            res = []
            done = set()
            for drop in data["detdrops"]:
                if drop[0] not in done:
                    res.append(drop)
                    done.add(drop[0])
            data["detdrops"] = res
        if 'Amarok' in data["displayName"] and "recipeData" in data.keys():
            data["recipeData"]["recipeFrom"] = "[[Tasks/Blunder_Hills#Merit_Shop|Blunder Hills Merit Shop]]"
        elif 'Efaunt' in data["displayName"] and "recipeData" in data.keys():
            data["recipeData"]["recipeFrom"] = "[[Tasks/Yum_Yum_Desert#Merit_Shop|Yum Yum Desert Merit Shop]]"

        if data["typeGen"] == 'aStorageChest':
            data["description"] = [
                f"Hold down to permanently add +{data['lvReqToCraft']} Slots to your Storage Chest. Can only be used once."]
        elif data["typeGen"] == 'aInventoryBag':
            data["description"] = [
                f"Hold down to permanently add +{data['lvReqToCraft']} Slots to your Inventory. Can only be used once."]

        if "lvReqToCraft" in data.keys():
            del data["lvReqToCraft"]

        toDel = ["common", "consumable", "equip"]
        for atr, val in data.items():
            if val in [0, '0'] and atr != 'ID':
                toDel.append(atr)
        for dele in toDel:
            if dele in data.keys():
                del data[dele]

    # Remove unused arrays
    for name, data in items.items():
        if not data["detdrops"]:
            del data["detdrops"]
        if not data["sources"]:
            del data["sources"]
        if not data["uses"]:
            del data["uses"]


def configureDetailedRecipe(items, citem):
    # puts sub recipes into recipes recursively.
    if citem["detrecipe"] != []:
        return
    for req, no in citem["recipeData"]["recipe"]:
        if item := items.get(req):
            if "recipeData" in item.keys():
                if item["detrecipe"] == []:
                    configureDetailedRecipe(items, item)
                citem["detrecipe"].append([0] + [req, no])
                citem["detrecipe"] += [[x[0] + 1, x[1],
                                        str(int(x[2])*int(no))] for x in item["detrecipe"]]
            else:
                citem["detrecipe"].append([0] + [req, no])


def getDetailedTotals(item):
    i = 0
    counter = 0
    totals = {}
    detrecipe = item["detrecipe"]
    currentDepth = -1

    def addToTotals(item, number):
        totals[item] = totals.get(item, 0) + int(number)
    while counter != 4:
        if i == len(detrecipe):
            addToTotals(detrecipe[i-1][1], detrecipe[i-1][2])
            break
        # If we see an item with a higher depth that means there is a sub recipe
        if currentDepth < detrecipe[i][0]:
            # we set this to our current depth untill we find the smallest subrecipe
            currentDepth = detrecipe[i][0]
        # This means we are in the subrecipe
        elif currentDepth == detrecipe[i][0]:
            # We add it, since this is our subrecipe
            addToTotals(detrecipe[i-1][1], detrecipe[i-1][2])
        else:  # If we reach the end of the sub recipe
            addToTotals(detrecipe[i-1][1], detrecipe[i-1][2])
            currentDepth = -1
            counter += 1
        i += 1
    item["detRecipeTotals"] = [(n, v) for n, v in totals.items()]


def deleteFiller(items):
    toDelete = [
        "EXP", "Blank", "LockedInvSpace", "COIN", "TalentBook1", "TalentBook2", "TalentBook3", "TalentBook4", "TalentBook5",
        "SmithingRecipes1", "SmithingRecipes2", "SmithingRecipes3", "SmithingRecipes4",
    ]
    for name, data in items.items():
        if data["displayName"] in ['Filler', 'FILLER', 'Blank']:
            toDelete.append(name)
    for name in toDelete:
        del items[name]


def droptableToEnem(enemies, droptables, skillSources):
    dtToEnem = {}

    def addElement(key, element):
        if key in dtToEnem.keys():
            dtToEnem[key].append(element)
        else:
            dtToEnem[key] = [element]
    for name, enem in enemies.items():
        if skillsS := skillSources.get(enem["Type"].split('.')[1]):
            enemName = skillsS(enem['Name'])
        else:
            enemName = enem["Name"]
        if drops := enem.get("Drops"):
            for drop in drops:
                if drop[0][:9] == "DropTable":
                    addElement(drop[0], [f'[[{enemName}]]'] + drop[1:3])
    for name, droptable in droptables.items():
        for drop in droptable:
            if drop[0][:5] == "Super":
                if dt := dtToEnem.get(name):
                    for d in dt:
                        addElement(drop[0], [d[0], float(
                            d[1])*float(drop[1]), float(d[2])*float(drop[2])])
    return dtToEnem


def getSmithingRecipe(recipes, name, qty):
    tab = int(name[-1]) - 1
    index = int(qty)
    for name, item in recipes[tab].items():
        if int(item["no"]) == index:
            return name


def materialBagDesc(item):
    pouches = {
        "Mining": ["Ores", "Bars", "Barrels"],
        "Chopping": ["Logs", "Leaves"],
        "Foods": ["Health Food", "Boost Food", "Golden Food"],
        "Bcraft": ["Monster Parts", "Smithing Production Items"],
        "Fishing": ["Fish"],
        "Bugs": ["Bugs"],
    }
    def baseDesc(
        x): return f'Hold down on this bag to increase the Carry Capacity of the following items to {x}: '
    increases = ', '.join(pouches[item["Class"]]) + '.'
    item['description'] = [baseDesc(item["lvReqToEquip"]) + increases]
    keep = ["displayName", "sellPrice", "Type", "uses", "recipeData", "detrecipe",
            "detRecipeTotals", "sources", "detdrops", "typeGen", 'description']
    delete = [x for x in item.keys() if x not in keep]
    for key in delete:
        del item[key]


def configureSellPrice(items, item):
    sellPrice = 0
    detRecipeTotals = item["detRecipeTotals"]
    for total in detRecipeTotals:
        if ite := items.get(total[0]):
            sellPrice += int(ite["sellPrice"])*total[1]
    item["sellPrice"] = sellPrice


def getDisp(key):
    return nameDic.get(key, key)


def main():
    # Get all the information saved from jsons
    skillSources = {
        "ORE_TYPE": lambda x: f"Mining#Drops|Mining {x}",
        "TREE_TYPE": lambda x: f"Choppin#Drops|Choppin {x}",
        "FISH_TYPE": lambda x: f"Fishing#Drops|Fishing {x}",
        "BUG_TYPE": lambda x: f"Catching#Drops|Catching {x}",
    }
    items = openJSON("Items")
    deleteFiller(items)
    global nameDic
    nameDic = {name: item["displayName"] for name, item in items.items()}
    cardData = openJSON("CardData")
    fishingTK = openJSON("FishingTK")
    enemies = openJSON("Enemies")
    droptables = openJSON("Droptables")
    dtToEnemies = droptableToEnem(enemies, droptables, skillSources)
    npcs = openJSON("Npcs")
    recipes = openJSON("Recipes")
    postOffices = openJSON("PostOffice")
    shopData = openJSON("ShopData")
    cauldrons = openJSON("Cauldrens")
    processing = openCSV("Production")
    statueData = openCSV("StatueData")
    taskUnlocks = openJSON("TaskUnlocks")

    # This loop is for specific types of the items
    allItemsStart(items)
    # Adding in the fishing toolkit data
    for typ, datas in fishingTK.items():
        for i, data in enumerate(datas):
            if item := items.get(f"{typ}{i}"):
                item["Fishing"] = data
    # Adding in production data
    for n, (name, time, lvl, exp) in enumerate(processing, 1):
        if item := items.get(name):
            item['sources'].append(
                '[[Smithing#Production items|Anvil Production]]')
            item['prodInfo'] = [n, time, lvl, exp]
    # Adding in shop data and the source
    for vendor, data in shopData.items():
        for ite in data:
            if item := items.get(ite["item"]):
                if "shopData" not in item.keys():
                    item["shopData"] = []
                item["sources"].append(f'[[Vendors#{vendor}|{vendor} Vendor]]')
                item["shopData"].append({
                    "vendor": vendor,
                    "quantity": ite['quantity'],
                    "no": ite['no']
                })
    # Adding in the mob drops as sources for all items
    for name, enemy in enemies.items():
        if drops := enemy.get("Drops"):
            for drop in drops:
                if item := items.get(drop[0]):
                    enemName = ''
                    if name[0:5] == "Chest":
                        enemName = f"Colosseum#{enemy['Name']}|{enemy['Name']}"
                    elif skillsS := skillSources.get(enemy["Type"].split('.')[1]):
                        enemName = skillsS(enemy['Name'])
                    else:
                        enemName = enemy['Name']

                    item["sources"].append(f"[[{enemName}]]")
                    item["detdrops"].append(
                        [f"[[{enemName}]]", drop[1], drop[2]])
    # Adding in the sources from post office shipping rewards and uses from shipping
    for name, po in postOffices.items():
        for req in po["Orders"].keys():
            if item := items.get(req):
                item["uses"].append(
                    (f'[[Post Office#{name}|{name}]]', "Lots", 'Post Office'))
        for rew in po["Rewards"].keys():
            if item := items.get(rew):
                item["sources"].append(f'[[Post Office#{name}|{name}]]')
    # Adding in all recipes data to the items and adding in uses.
    for tab in recipes:
        for name, recipe in tab.items():
            if item := items.get(name):
                item["recipeData"] = recipe
                item["detrecipe"] = []
            for sub in recipe["recipe"]:
                if subItem := items.get(sub[0]):
                    subItem["uses"].append(
                        (f'[[{nameDic[name]}]]', sub[1], "Crafting"))
    # Configure the detailed recipe
    for tab in recipes:
        for name, recipe in tab.items():
            if item := items.get(name):
                configureDetailedRecipe(items, item)
                getDetailedTotals(item)
                configureSellPrice(items, item)
    # Adding in uses and sources from npcs and quests
    for npc, qdata in npcs.items():
        for dline in qdata:
            # Add in the requirements to the uses of the itmes
            if dline["Type"] == "ItemsAndSpaceRequired":
                requirements = zip(dline['ItemTypeReq'], dline['ItemNumReq'])
                for req, num in requirements:
                    if item := items.get(req):
                        item["uses"].append(
                            (f'[[{npc}#{dline["Name"]}|{dline["Name"]}]]', num, "Quests"))
                        if item['typeGen'] == 'dQuest':
                            item['questAss'] = f'[[{npc}#{dline["Name"]}|{dline["Name"]}]]'
            # Add in sources for rewards and smithing recipe.
            if dline["Type"] not in ["None", "SpaceRequired", "LevelReq"]:
                rewards = dline['Rewards']
                for i in range(len(rewards)):  # TalentBook
                    if rewards[i][:-1] == "SmithingRecipes":
                        if item := items.get(getSmithingRecipe(recipes, rewards[i], rewards[i+1])):
                            item["recipeData"]["recipeFrom"] = npc
                    elif item := items.get(rewards[i]):
                        item["sources"].append(
                            f'[[{npc}#{dline["Name"]}|{dline["Name"]}]]')
    # Add in the cauldrens to used in
    for cname, bubbles in cauldrons.items():
        if name == "Liquid Shop":
            break
        for bname, bubble in bubbles.items():
            for req, n in bubble["requirements"]:
                if item := items.get(req):
                    item["uses"].append(
                        (f'[[{cname}#{bname}|{bname}]]', "Lots", "Alchemy"))
    # add in card data
    for section, cards in cardData.items():
        for name, card in cards.items():
            itemName = "Cards" + card[0]
            if item := items.get(itemName):
                if desc := item.get("description"):
                    if subItem := items.get(desc[0]):
                        item["displayName"] = subItem["displayName"] + " Card"
                        subItem['hascard'] = True
                        item["cardData"] = [section] + \
                            card[1:] + [subItem["displayName"]]
                    elif enem := enemies.get(name):
                        item["displayName"] = enem["Name"] + " Card"
                        enem['hascard'] = True
                        item["cardData"] = [section] + \
                            card[1:] + [enem["Name"]]
    items["CardsB13"]["displayName"] = "Crystal Crabal Card"
    items["CardsA0"]["displayName"] = "Green Mushroom Card"
    items["CardsA1"]["displayName"] = "Red Mushroom Card"
    # Add in statue data
    for n, data in enumerate(statueData):
        itemN = f"EquipmentStatues{n+1}"
        if item := items.get(itemN):
            if data[1][0] == '%':
                data[1] = data[1].replace("%@", "+ %@ ")
            else:
                data[1] = data[1].replace("@", "+ @ ")
            item["statueData"] = [repU(x) for x in data]
    # add in subtables sources
    for name, drops in droptables.items():
        for drop in drops:
            if item := items.get(drop[0]):
                item["sources"].append(f"[[{name}]]")
                if detdrops := dtToEnemies.get(name):
                    for detdrop in detdrops:
                        item['detdrops'].append([
                            detdrop[0],
                            np.format_float_positional(
                                float(drop[1])*float(detdrop[1]), trim='-'),
                            str(float(drop[2])*float(detdrop[2]))
                        ])
    # Renames the internal to external name

    for tab in recipes:
        for name, recipe in tab.items():
            if item := items.get(name):
                recipe["recipe"] = [[nameDic[x], y]
                                    for x, y in recipe["recipe"]]
                item["recipeData"] = recipe
                item["detrecipe"] = [[x, nameDic[y], z]
                                     for x, y, z in item["detrecipe"]]
                item["detRecipeTotals"] = [[nameDic[y], z]
                                           for y, z in item["detRecipeTotals"]]
    # Adding in recipe source from the task unlocks
    for taskUnlock in taskUnlocks:
        for ite in taskUnlock:
            if item := items.get(ite):
                if ite == "PremiumGem":
                    continue
                item["recipeData"]["recipeFrom"] = "[[Tasks/Unlocks|Tasks]]"
    allItemsEnd(items)
    writeJSON("Items", items)
    getNotes.main()


if __name__ == '__main__':
    main()

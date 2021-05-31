# import pywikibot
import json
from libs.funcLib import camelCaseSplitter, nameDic
from libs.jsonEncoder import CompactJSONEncoder

# from pywikibot import Page, Site
import re


def writeFile(fn, out):
    with open(fn, mode="w") as outfile:
        outfile.write(out)


def writeOLD(fn, out):
    with open(rf"./output/old/items/{fn}.txt", mode="w") as outfile:
        outfile.write(out)


def checkOld(fn, check):
    """
    Returns true if they are the same.
    """
    with open(rf"./output/old/items/{fn}.txt", mode="r") as infile:
        if check != infile.read():
            print(infile.read())
        return check == infile.read()


def writeJSON(fn, dicti):
    with open(fn, mode="w") as outfile:
        outfile.write(CompactJSONEncoder(indent=4).encode(dicti))


def resetOutFiles(itemTypes):
    for itemType in itemTypes:
        open(rf"./output/wiki/items/{itemType}.txt", "w").close()


def addToType(itemType, out):
    with open(rf"./output/wiki/items/{itemType}.txt", "a") as outfile:
        outfile.write(out)


def doSkill(name, item):
    if skill := isSkill(name, item):
        return skill.lower()
    return ""


def doDescription(name, item):
    if description := item.get("description"):
        return " ".join(description)
    else:
        return ""


def doSource(name, item):
    if source := item.get("sources"):
        return ", ".join(source)
    else:
        return ""


def doRarity(name, item):
    if item["typeGen"][:5] != "aObol":
        return ""
    return item["displayName"].split(" ")[0]


def doTier(name, item):
    if item["typeGen"] == "dStone":
        try:
            return item["displayName"].split("Upgrade Stone ")[1]
        except IndexError:
            return item["displayName"].split(" Upgrade Stone")[0].split(" ")[0]


def doWepPower(name, item):
    if "Weapon_Power" not in item.keys():
        return ""
    if isSkill(name, item):
        return ""
    return item["Weapon_Power"]


def doBonus(name, item):
    if item["typeGen"] == "aStamp":
        return item["stampData"][-2].split("{}")[1]
    return ""


def doSkillPower(name, item):
    if "Weapon_Power" not in item.keys():
        return ""
    if isSkill(name, item):
        return item["Weapon_Power"]
    return ""


def isSkill(name, item):
    skillNames = ["Catching", "Fishing", "Choppin", "Mining"]
    toolSkills = {
        "aHatchet": "Choppin",
        "aFishingRod": "Fishing",
        "aBugNet": "Catching",
        "aPick": "Mining",
    }
    skill = camelCaseSplitter(name)[-1]
    if skill in skillNames:
        return skill
    if skill := toolSkills.get(item["typeGen"]):
        return skill
    return ""


def writeItem(name, item):
    mapIntToWiki = {
        "class": "Class",
        "level": "lvReqToEquip",
        "skill": doSkill,
        "type": "Type",
        "speed": "Speed",
        "weaponpower": doWepPower,
        "skillpower": doSkillPower,
        "bonus": doBonus,
        "str": "STR",
        "agi": "AGI",
        "wis": "WIS",
        "luck": "LUK",
        "misc": "miscUp1",
        "reach": "Reach",
        "upgrade": "Upgrade_Slots_Left",
        "defence": "Defence",
        "quest": "questAss",
        "description": doDescription,
        "sellprice": "sellPrice",
        "rarity": doRarity,
        "tier": doTier,
        "source": doSource,
        "notes": "notes",
    }
    itemData = "{{InfoItem\n"
    for wiki, atr in mapIntToWiki.items():
        if isinstance(atr, str):
            if artibute := item.get(atr):
                itemData += f"|{wiki}={artibute}\n"
        else:
            if artibute := atr(name, item):
                itemData += f"|{wiki}={artibute}\n"
    itemData += "}}\n"

    itemData += writeSubData(name, item)
    return itemData


def writeStampInfo(name, item):
    itemData = "{{InfoStamp\n"
    mapIntToWiki = {
        "number": "ID",
        "type": "Type",
        "bonus": doBonus,
        "material": 5,
        "sellprice": "sellPrice",
        "source": doSource,
    }
    for wiki, atr in mapIntToWiki.items():
        if isinstance(atr, str):
            if artibute := item.get(atr):
                itemData += f"|{wiki}={artibute}\n"
        elif isinstance(atr, int):
            artibute = item["stampData"][atr]
            itemData += f"|{wiki}={artibute}\n"
        else:
            if artibute := atr(name, item):
                itemData += f"|{wiki}={artibute}\n"
    itemData += "}}\n"
    return itemData


def writeFish(name, item):
    mapIntToWikiFishing = {
        "depth1": "Depth1",
        "depth2": "Depth2",
        "depth3": "Depth3",
        "depth4": "Depth4",
        "fishingexp": "FishingExp",
        "fishingspeed": "FishingSpeed",
        "fishingpower": "FishingPower",
        "source": doSource,
        "type": "Type",
        "sellprice": "sellPrice",
    }
    itemData = "{{Fishingaccessory\n"
    for wiki, atr in mapIntToWikiFishing.items():
        if isinstance(atr, str):
            if artibute := item.get(atr):
                itemData += f"|{wiki}={artibute}\n"
            elif artibute := item["Fishing"].get(atr):
                if artibute not in ["0", 0]:
                    itemData += f"|{wiki}={artibute}\n"
        else:
            if artibute := atr(name, item):
                itemData += f"|{wiki}={artibute}\n"
    itemData += "}}\n"

    itemData += writeSubData(name, item)
    return itemData


def writeCard(name, item):
    mapIntToWikiCard = {
        "title": 5,
        "order": 4,
        "category": 0,
        "effect": 2,
        "bonus": 3,
        "reqtier": 1,
        "source": doSource,
    }
    if "cardData" not in item.keys():
        return ""
    itemData = "{{InfoCard\n"
    for wiki, atr in mapIntToWikiCard.items():
        if isinstance(atr, int):
            artibute = item["cardData"][atr]
            itemData += f"|{wiki}={artibute}\n"
        else:
            if artibute := atr(name, item):
                itemData += f"|{wiki}={artibute}\n"
    itemData += "}}\n"

    itemData += writeSubData(name, item)
    return itemData


def writeSubData(name, item):
    itemData = ""
    if item["Type"] == "Golden Food":
        itemData += writeGoldFood(name, item)
    elif item["Type"] == "Stamp":
        itemData += writeStamp(name, item)
    elif item["Type"] == "Statue":
        itemData += writeStatue(name, item)

    if "recipeData" in item.keys():
        itemData += writeRecipe(name, item)
    elif "shopData" in item.keys():
        itemData += writeVendors(name, item)
    elif "detdrops" in item.keys():
        itemData += writeDetdrops(name, item)

    if "prodInfo" in item.keys():
        itemData += writeProccessing(name, item)
    if "uses" in item.keys():
        itemData += writeUses(name, item)
    if "detrecipe" in item.keys():
        itemData += writeDetrecipe(name, item)

    return itemData


def writeGoldFood(name, item):
    head = "{{"
    tail = "}}\n"
    amount = item["Amount"]
    desc = item["description"][0] + " " + item["description"][1]
    return f"{head}gfoodbonus|{amount}|{desc}{tail}"


def writeStamp(name, item):
    mapStampToWiki = ["stype", "ftype", "x1", "x2", "i4", "material", "i6", "i7", "i8", "i9", "i10", "i11", "i12"]
    head = "{{"
    tail = "}}\n"
    res = f"{head}stampdata"
    for v, a in zip(item["stampData"], mapStampToWiki):
        res += f"|{a}={v}"
    res += tail
    return res


def writeRecipe(name, item):
    mapRecipeData = {
        "anvtab": "tab",
        "craftnum": "no",
        "levelreq": "levelReqToCraft",
        "expgiven": "expGiven",
    }
    head = "{{"
    tail = "}}\n"
    recipData = item["recipeData"]
    res = f"{head}ForgeSlot\n"
    for wiki, atr in mapRecipeData.items():
        res += f"|{wiki}={recipData[atr]}\n"
    res += f'|recipefrom={recipData.get("recipeFrom","Start")}\n'
    for i, (n, q) in enumerate(recipData["recipe"], 1):
        res += f"|resource{i}={n}|quantity{i}={q}\n"
    return res + tail


def writeVendors(name, item):
    mapShopData = {"number": "no", "vendor": "vendor", "stock": "quantity"}
    res = "{{Vendoritem/head}}\n"
    shopDatas = item["shopData"]
    for shopData in shopDatas:
        res += "{{Vendoritem/tablerow"
        for wiki, atr in mapShopData.items():
            res += f"|{wiki}={shopData[atr]}"
        res += f"|buyprice={int(item['sellPrice'])*4}" + "}}\n"
    return res + "|}\n"


def writeStatue(name, item):
    statueData = item["statueData"]
    return "{{Statuedata" + f"|{statueData[3]}|{statueData[1]}" + "}}\n"


def writeDetdrops(name, item):
    detdrops = item["detdrops"]
    res = "{{detdrops/head}}\n"
    for detdrop in detdrops:
        res += "{{detdrops|" + f"{detdrop[0]}|{detdrop[1]}|{detdrop[2]}" + "}}\n"
    return res + "|}\n"


def writeDetrecipe(name, item):
    detRecipe = item["detrecipe"]
    res = "{{detrecipe/head}}\n"
    for sub in detRecipe:
        indent = 3 if sub[0] == 0 else int(sub[0]) * 40
        res += "{{detrecipe" + f"|{indent}|{sub[1]}|{sub[2]}" + "}}\n"
    res += "{{!}}-\n{{!}}style=\"text-align:right\"{{!}}'''Totals'''\n{{!}} \n"
    detRecipeTotals = item["detRecipeTotals"]
    for sub in detRecipeTotals:
        res += "{{detrecipe/totals" + f"|{sub[0]}|{sub[1]}" + "}}\n"
    return res + "|}\n"


def writeUses(name, item):
    uses = item["uses"]
    res = "{{usedin/head}}\n"
    uses = sorted(uses, key=lambda x: x[1] == "Lots")
    for use in uses:
        res += "{{" + f"usedin/row|{use[0]}|{use[1]}|{use[2]}" + "}}\n"
    return res + "|}\n"


def writeProccessing(name, item):
    proccessing = item["prodInfo"]
    return "{{" + f"ProductionSlot|lvlreq={proccessing[2]}|num={proccessing[0]}|expcraft={proccessing[3]}|time={proccessing[1]}" + "}}\n"


def main(OLD, UPLOAD):
    if OLD and UPLOAD:
        print("You cannot have old and upload set to true")
        return
    toWiki = {
        "dCard": writeCard,
        "dFishToolkit": writeFish,
        "aStamp": writeStampInfo,
    }

    with open(fr"./output/modified/json/Items.json", mode="r") as jsonFile:
        items = json.load(jsonFile)

    allItems = {}
    for name, item in items.items():
        func = toWiki.get(item["typeGen"], writeItem)
        if out := func(name, item):
            allItems[name] = out

    if OLD:
        for name, data in allItems.items():
            writeOLD(name, data)

    itemTypes = {x["typeGen"][1:] for x in items.values()}
    resetOutFiles(itemTypes)
    for name, data in allItems.items():
        addToType(items[name]["typeGen"][1:], items[name]["displayName"] + "\n" + data)

    if UPLOAD:
        for name, data in allItems.items():
            if checkOld(name, data) == False:
                pass


if __name__ == "__main__":
    main(True, True)

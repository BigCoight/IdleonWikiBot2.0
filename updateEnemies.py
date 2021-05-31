import json
import re


def writeDrops(drops, subtable, caption, collapsible):
    res = ""
    addition = ""
    if caption != "":
        addition += "|Droptable for " + caption
    if collapsible:
        addition += "|collapsed=Yes"
    res += "{{DropTable/head" + addition + "}}\n"
    for drop in drops:
        if subtable:
            if drop[0] == "COIN":
                pass
            if "Super" not in drop[0]:
                drop[1] = "{{#expr: {{{chance}}}*" + drop[1] + "}}"
            elif "Super" in drop[0]:
                res += "{{#vardefine:chance1|{{#expr:{{{chance" + "}}}*" + drop[1] + "}}}}{{" + drop[0] + "|chance={{#var:chance1}}}}"
        if drop[0] == "COIN" and drop[1] != "0":
            res += "{{DropTable/coin|" + drop[2] + "|" + drop[1] + "}}\n"
        elif "Drop" in drop[0]:
            res += "{{" + drop[0] + "|chance=" + drop[1] + "}}\n"
        elif drop[1] != "0" and drop[0]:
            if drop[3] == "N/A":
                drop.pop()
            else:
                drop[3] = "([[" + re.sub(r"\d+", "", drop[3]) + "]])"
            splitDrop = drop[0].split(";")
            if len(splitDrop) > 1:
                if splitDrop[1] == "Talent Book":
                    res += "{{DropTable/talent" + splitDrop[0] + f"|{drop[1]}" + "}}"
                elif splitDrop[1] == "Recipe":
                    res += "{{DropTable/recipe" + f"{splitDrop[2]}|{splitDrop[0]}|{drop[1]}"
            elif "Card" in drop[0]:
                res += "{{" + f"DropTable/card|{drop[1]}"
            else:
                res += "{{DropTable/row" + "|" + "|".join(drop)
            res += "}}\n"
    res += "|}\n"
    return res


def writeEnemyOut(enemy, data):
    with open(rf"./output/wiki/enemies/{enemy}.txt", mode="w") as outfile:
        outfile.write(data)


def writeDTOut(dt, data):
    with open(rf"./output/wiki/droptables/{dt}.txt", mode="w") as outfile:
        outfile.write(data)


def writeDTS(dts):
    res = ""
    for name, dt in dts.items():
        if dt:
            res += writeDrops(dt, False, f"Drops for {name}", True)
    return res


def writeEnemy(enemy):
    enemyData = "{{InfoEnemy\n"
    intToWiki = {
        "image": "Image",
        "attack": "Damages",
        "health": "MonsterHPTotal",
        "defence": "Defence",
        "speed": "MoveSPEED",
        "world": "World",
        "area": "Area",
        "exp": "ExpGiven",
        "respawn": "RespawnTime",
        "defence0": "defFor0",
        "crystal": "hasCrystal",
        "crystalname": "Crystal",
        "hascard": "hasCard",
    }
    for wiki, atr in intToWiki.items():
        if isinstance(atr, str):
            if artibute := enemy.get(atr):
                enemyData += f"|{wiki}={artibute}\n"

    enemyData += "}}\n"

    enemyData += writeSubData(enemy)
    return enemyData


def writeSubData(enemy):
    res = ""
    res += "{{EnemyNavigation|" + enemy.get("Prev", "") + "|" + enemy.get("Next", "") + "}}\n"
    if (drops := enemy.get("Drops")) :
        res += writeDrops(drops, False, "", False)
    return res


def writeOLD(cat, fn, out):
    with open(rf"./output/old/{cat}/{fn}.txt", mode="w") as outfile:
        outfile.write(out)


def checkOld(cat, fn, check):
    """
    Returns true if they are the same.
    """
    with open(rf"./output/old/{cat}/{fn}.txt", mode="r") as infile:
        if check != infile.read():
            print(infile.read())
        return check == infile.read()


def main(OLD, UPLOAD):
    if OLD and UPLOAD:
        print("You cannot have old and upload set to true")
        return
    with open(fr"./output/modified/json/SkillingDT.json", mode="r") as jsonFile:
        skillingDTS = json.load(jsonFile)

    with open(fr"./output/modified/json/Enemies.json", mode="r") as jsonFile:
        enemies = json.load(jsonFile)

    with open(fr"./output/modified/json/DropTables.json", mode="r") as jsonFile:
        dropTables = json.load(jsonFile)

    allEnemies = {}
    allDroptables = {}

    for name, enemy in enemies.items():
        allEnemies[name] = writeEnemy(enemy)
        writeEnemyOut(name, allEnemies[name])
        if OLD:
            writeOLD("enemies", name, allEnemies[name])

    for name, dt in skillingDTS.items():
        writeDTOut(name, writeDTS(dt))

    for name, dt in dropTables.items():
        allDroptables[name] = writeDrops(dt, True, "", False)
        writeDTOut(name, allDroptables[name])
        if OLD:
            writeOLD("droptables", name, allDroptables[name])

    if UPLOAD:
        for name, data in allEnemies.items():
            if checkOld("enemies", name, data) == False:
                pass

        for name, data in allDroptables.items():
            if checkOld("droptables", name, data) == False:
                pass


if __name__ == "__main__":
    main(True, False)

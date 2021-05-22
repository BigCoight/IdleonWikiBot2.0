
import json


def writeDrops(drops):
    res = ''
    for drop in drops:
        pass



def writeEnemy(enemy):
    enemyData = "{{InfoEnemy"
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
                enemyData += (f"|{wiki}={artibute}\n")
    
    enemyData += '}}\n'

    enemyData += writeSubData(enemy)
    return enemyData

def writeSubData(enemy):
    res = ''
    res += "{{EnemyNavigation|"+enemy.get("Prev","")+"|"+enemy.get("Next","")+"}}\n"
    pass



def main():
    skillingDTS = json.load(r"./output/modified/json/skillingDT.json")
    enemies = json.load(r"./output/modified/json/Enemies.json")
    dropTables = json.load(r"./output/modified/json/DropTables.json")


if __name__ == "__main__":
    main()

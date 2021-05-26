import json
from random import choice, randint


def doStarsign():
    return choice(["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"])


def doMMM():
    return choice(["Anderson", "Ashwoon", "Aikin", "Bateman", "Bongard", "Bowers", "Boyd", "Cannon", "Cast", "Deitz", "Dewalt", "Ebner", "Frick", "Hancock", "Haworth", "Hesch", "Hoffman", "Kassing", "Knutson", "Lawless", "Lawicki", "Mccord", "McCormack", "Miller", "Myers", "Nugent", "Ortiz", "Orwig", "Ory", "Paiser", "Pak", "Pettigrew", "Quinn", "Quizoz", "Ramachandran", "Resnick", "Sagar", "Schickowski", "Schiebel", "Sellon", "Severson", "Shaffer", "Solberg", "Soloman", "Sonderling", "Soukup", "Soulis", "Stahl", "Sweeney", "Tandy", "Trebil", "Trusela", "Trussel", "Turco", "Uddin", "Uflan", "Ulrich", "Upson", "Vader", "Vail", "Valente", "Van Zandt", "Vanderpoel", "Ventotla", "Vogal", "Wagle", "Wagner", "Wakefield", "Weinstein", "Weiss", "Woo", "Yang", "Yates", "Yocum", "Zeaser", "Zeller", "Ziegler", "Bauer", "Baxster", "Casal", "Cataldi", "Caswell", "Celedon", "Chambers", "Chapman", "Christensen", "Darnell", "Davidson", "Davis", "DeLorenzo", "Dinkins", "Doran", "Dugelman", "Dugan", "Duffman", "Eastman", "Ferro", "Ferry", "Fletcher", "Fietzer", "Hylan", "Hydinger", "Illingsworth", "Ingram", "Irwin", "Jagtap", "Jenson", "Johnson", "Johnsen", "Jones", "Jurgenson", "Kalleg", "Kaskel", "Keller", "Leisinger", "LePage", "Lewis", "Linde", "Lulloff", "Maki", "Martin", "McGinnis", "Mills", "Moody", "Moore", "Napier", "Nelson", "Norquist", "Nuttle", "Olson", "Ostrander", "Reamer", "Reardon", "Reyes", "Rice", "Ripka", "Roberts", "Rogers", "Root", "Sandstrom", "Sawyer", "Schlicht", "Schmitt", "Schwager", "Schutz", "Schuster", "Tapia", "Thompson", "Tiernan", "Tisler"])


def doBirthweight():
    return randint(100, 1000)/100


def writeNpcOut(name, data):
    with open(rf"./output/wiki/npcs/{name}.txt", mode='w') as outfile:
        outfile.write(data)


def writeOLD(cat, fn, out):
    with open(rf'./output/old/{cat}/{fn}.txt', mode='w') as outfile:
        outfile.write(out)


def writeNpc(npc):
    infoNpc = "{{InfoNpc\n"
    intToWiki = {
        "location": "fillme",
        "noquests": "fillme",
        "repeatable": "Unknonwn",
        "starsign": doStarsign,
        "mmm": doMMM,
        "birthweight": doBirthweight,
        "notes": "fillme"
    }

    for wiki, atr in intToWiki.items():
        if isinstance(atr, str):
            infoNpc += (f"|{wiki}={atr}\n")
        else:
            infoNpc += (f"|{wiki}={atr()}\n")

    infoNpc += "}}\n"
    infoNpc += writeQuests(npc)
    infoNpc += writeDiologue(npc)
    return infoNpc


def doReq(quest):
    if isinstance(quest["requirements"], str):
        return quest["requirements"]
    else:
        res = []
        for v, n in quest["requirements"]:
            res.append(n + "x {{CraftReq|" + v + "}}")
        return ", ".join(res)


def doRew(quest):
    res = []
    for v, n in quest["rewards"]:
        splitRew = v.split(';')
        if len(splitRew) > 1:
            if splitRew[1] == "Experience":
                res.append(n + " " + splitRew[0] + " " + splitRew[1])
            elif splitRew[1] == "Talent Book":
                res.append("{{Talentbook" + f"|{splitRew[0]}" + "}}")
            elif splitRew[1] == "Recipe":
                res.append("{{Recipe" + f"|{splitRew[2]}|{splitRew[0]}" + "}}")
        else:
            res.append(n + "x {{CraftReq|" + v + "}}")

    return ", ".join(res)


def writeQuests(npc):
    infoQuest = '{{Quest/head}}\n'
    intToWiki = {
        "name": "name",
        "text": "questText",
        "difficulty": "difficulty",
        "requirements": doReq,
        "consumed": "consumed",
        "rewards": doRew,
        "notes": "notes",

    }
    for quest in npc["Quests"]:
        infoQuest += "{{Quest\n"
        for wiki, atr in intToWiki.items():
            if isinstance(atr, str):
                if artibute := quest.get(atr):
                    infoQuest += (f"|{wiki}={artibute}\n")
            else:
                infoQuest += (f"|{wiki}={atr(quest)}\n")
        infoQuest += '}}\n'
    infoQuest += "|}\n"
    return infoQuest


def writeDiologue(npc):
    infoDiologue = '{{dialogue/head}}\n'
    intToWiki = {
        "text": "text",
        "quest": "associated",

    }
    for quest in npc["Dialogue"]:
        infoDiologue += "{{dialogue/row\n"
        for wiki, atr in intToWiki.items():
            if artibute := quest.get(atr):
                infoDiologue += (f"|{wiki}={artibute}\n")
        infoDiologue += '}}\n'
    infoDiologue += "|}\n"
    return infoDiologue


def main(OLD, UPLOAD):
    with open(fr'./output/modified/json/Npcs.json', mode='r') as jsonFile:
        npcs = json.load(jsonFile)

    allNpcs = {}
    for name, npc in npcs.items():
        allNpcs[name] = writeNpc(npc)
        writeNpcOut(name, allNpcs[name])
        if OLD:
            writeOLD("npcs", name, allNpcs[name])


if __name__ == '__main__':
    main(True, True)

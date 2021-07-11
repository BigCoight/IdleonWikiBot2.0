from pywikibot import Page, Site
import re
import json
from libs.jsonEncoder import CompactJSONEncoder


def writeJSON(fn, dicti):
    with open(fn, mode="w") as outfile:
        outfile.write(CompactJSONEncoder(indent=4).encode(dicti))


def searchNotes(wesbite, siteName):
    if siteName not in ["", " "]:
        page = Page(wesbite, siteName)
        notes = re.findall(r"\|notes=(.*)", page.text)
        return notes[0] if notes else ""
    return ""


def getHead(website, siteName):
    if siteName not in ["", " "]:
        toSplit = "{{Quest/head}}"
        page = Page(website, siteName)
        splitText = page.text.split(toSplit)
        if len(splitText) > 1:
            searchText = page.text.split(toSplit)[0]
            return searchText
    return ""


def writeHead(name, head):
    with open(fr"./output/notes/npcHeads/{name}.txt", mode="w") as outfile:
        outfile.write(head)


def searchNotesNpc(wesbite, siteName):
    toSplit = "{{Quest/head}}"
    page = Page(wesbite, siteName)
    splitText = page.text.split(toSplit)
    if len(splitText) > 1:
        searchText = page.text.split(toSplit)[1]
        notes = re.findall(r"\|notes=(.*)", searchText)
        return notes if notes else " "
    return ""


def main(doItems, doNpcs, doEnemy):
    with open(fr"./output/modified/json/Items.json", mode="r") as jsonFile:
        items = json.load(jsonFile)
    with open(fr"./output/modified/json/Npcs.json", mode="r") as jsonFile:
        npcs = json.load(jsonFile)
    with open(fr"./output/modified/json/Enemies.json", mode="r") as jsonFile:
        enemies = json.load(jsonFile)
    website = Site()
    if doItems:
        itemNotes = {}
        for name, item in items.items():
            if notes := searchNotes(website, item["displayName"]).replace('"', ""):
                itemNotes[name] = notes
        writeJSON(fr"./output/notes/Items.json", itemNotes)

    if doEnemy:
        enemyNotes = {}
        for name, enemy in enemies.items():
            if notes := searchNotes(website, enemy["Name"]).replace('"', ""):
                enemyNotes[name] = notes
        writeJSON(fr"./output/notes/Enemies.json", enemyNotes)

    if doNpcs:
        questNotes = {}
        for name, npc in npcs.items():
            if head := getHead(website, name):
                writeHead(name, head)
            notes = searchNotesNpc(website, name)
            for note, quest in zip(notes, npc["Quests"].keys()):
                questNotes[quest] = note.replace('"', r"'")
        writeJSON(fr"./output/notes/Quest.json", questNotes)


if __name__ == "__main__":
    main(True, True, True)

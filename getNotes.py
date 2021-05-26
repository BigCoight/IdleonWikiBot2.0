from pywikibot import Page, Site
import re
import json
from libs.jsonEncoder import CompactJSONEncoder


def writeJSON(fn, dicti):
    with open(fn, mode='w') as outfile:
        outfile.write(CompactJSONEncoder(indent=4).encode(dicti))


def searchNotes(wesbite, siteName):
    page = Page(wesbite, siteName)
    notes = re.findall(r'\|notes=(.*)}}', page.text)
    return notes if notes else ''


def searchNotesNpc(wesbite, siteName):
    toSplit = "{{quest/head}}"
    page = Page(wesbite, siteName)
    searchText = page.text.split(toSplit)[1]
    notes = re.findall(r'\|notes=(.*)}}', searchText)
    return notes if notes else ''


def main():
    with open(fr'./output/modified/json/Items.json', mode='r') as jsonFile:
        items = json.load(jsonFile)
    with open(fr'./output/modified/json/Npcs.json', mode='r') as jsonFile:
        npcs = json.load(jsonFile)
    website = Site()
    for name, item in items.items():
        item["notes"] = searchNotes(
            website, item["displayName"])[0].replace('"', '')
    for name, npc in npcs.items():
        notes = searchNotes(website, name)
        for note, quest in zip(notes, npc["Quests"]):
            quest["notes"] = note

    writeJSON(fr'./output/modified/json/Items.json', items)


if __name__ == '__main__':
    main()

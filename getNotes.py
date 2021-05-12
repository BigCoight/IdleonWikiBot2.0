from pywikibot import Page, Site
import re
import json
from libs.jsonEncoder import CompactJSONEncoder


def writeJSON(fn, dicti):
    with open(fn, mode='w') as outfile:
        outfile.write(CompactJSONEncoder(indent=4).encode(dicti))


def searchNotes(wesbite, name, item):
    page = Page(wesbite, item["displayName"])
    notes = re.findall(r'\|notes=(.*)\n', page.text)
    if notes:
        return notes[0]
    return ''


def main():
    with open(fr'./output/modified/json/Items.json', mode='r') as jsonFile:
        items = json.load(jsonFile)
    website = Site()
    for name, item in items.items():
        item["notes"] = searchNotes(website, name, item).replace('"', '')

    writeJSON(fr'./output/modified/json/Items.json', items)


if __name__ == '__main__':
    main()

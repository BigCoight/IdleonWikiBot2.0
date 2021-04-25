import pywikibot
import json


def doSkill(item):
	return ''

def doMisc(item):
	return ''

def doQuest(item):
	return ''

def doDescription(item):
	if description := item.get("description"):
		return ' '.join(description)
	else:
		return ''

def doSource(item):
	if source := item.get("sources"):
		return ', '.join(source)
	else:
		return ''

def doRarity(item):
	return ''

def doTier(item):
	return ''


head = '{{InfoItem\n'
tail = '}}'

mapIntToWiki = {
	"class":"Class",
	"level":"lvReqToEquip",
	"skill": doSkill,
	"type": "Type",
	"speed": "Speed",
	"weaponpower":"Weapon_Power",
	"skillpower":"Weapon_Power",
	"bonus": "dk",
	"str": "STR",
	"agi": "AGI",
	"wis":"WIS",
	"luck":"LUK",
	"misc": doMisc,
	"reach": "Reach",
	"upgrade": "Upgrade_Slots_Left",
	"defence": "Defence",
	"quest": doQuest,
	"description": doDescription,
	"sellprice": "sellPrice",
	"rariry": doRarity,
	"tier": doTier,
	"source": doSource

}


def writeItem(item):
	dispName = item["displayName"]
	with open(fr'./output/wiki/items/{dispName}.txt' ,mode='w') as outfile:
		outfile.write(head)
		for wiki,atr in mapIntToWiki.items():
			if isinstance(atr, str):
				if artibute := item.get(atr):
					outfile.write(f"|{wiki}={artibute}\n")
			else:
				if artibute := atr(item):
					outfile.write(f"|{wiki}={artibute}\n")
		outfile.write(tail)




with open(fr'./output/modified/json/Items.json' ,mode='r') as jsonFile:
		items = json.load(jsonFile)

for name,item in items.items():
	writeItem(item)

import pywikibot
import json
from libs.funcLib import camelCaseSplitter, nameDic

def doSkill(name,item):
	if skill := isSkill(name):return skill.lower()
	return ''


def doDescription(name,item):
	if description := item.get("description"):
		return ' '.join(description)
	else:
		return ''

def doSource(name,item):
	if source := item.get("sources"):
		return ', '.join(source)
	else:
		return ''

def doRarity(name,item):
	if item["typeGen"][:5] != "aObol": return ""
	return item["displayName"].split(' ')[0]

def doTier(name,item):
	return ''

def doWepPower(name,item):
	if "Weapon_Power" not in item.keys(): return ''
	if isSkill(name):return ''
	return item["Weapon_Power"]

def doSkillPower(name,item):
	if "Weapon_Power" not in item.keys(): return ''
	if isSkill(name):return item["Weapon_Power"]
	return ''

head = '{{InfoItem\n'
tail = '}}'

mapIntToWiki = {
	"class":"Class",
	"level":"lvReqToEquip",
	"skill": doSkill,
	"type": "Type",
	"speed": "Speed",
	"weaponpower": doWepPower,
	"skillpower": doSkillPower,
	"bonus": "dk",
	"str": "STR",
	"agi": "AGI",
	"wis":"WIS",
	"luck":"LUK",
	"misc": "miscUp1",
	"reach": "Reach",
	"upgrade": "Upgrade_Slots_Left",
	"defence": "Defence",
	"quest": "questAss",
	"description": doDescription,
	"sellprice": "sellPrice",
	"rariry": doRarity,
	"tier": doTier,
	"source": doSource
}

skillNames = ['Catching','Fishing','Choppin','Mining']
def isSkill(name):
	skill = camelCaseSplitter(name)[-1]
	if skill in skillNames:
		return skill
	return ''

def writeItem(name,item):
	dispName = item["displayName"]

	with open(fr'./output/wiki/items/{dispName}.txt' ,mode='w') as outfile:
		outfile.write(head)
		for wiki,atr in mapIntToWiki.items():
			if isinstance(atr, str):
				if artibute := item.get(atr):
					outfile.write(f"|{wiki}={artibute}\n")
			else:
				if artibute := atr(name,item):
					outfile.write(f"|{wiki}={artibute}\n")
		outfile.write(tail)
	




with open(fr'./output/modified/json/Items.json' ,mode='r') as jsonFile:
	items = json.load(jsonFile)

altpyes = set()
for name,item in items.items():
	altpyes.add(item["typeGen"])
	writeItem(name,item)

print(altpyes)
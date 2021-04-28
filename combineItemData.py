import json 
import numpy as np
from libs.funcLib import fix, repU
from libs.jsonEncoder import CompactJSONEncoder


def writeJSON(fn,dicti):
	with open(fr'./output/modified/json/{fn}.json' ,mode='w') as outfile:
		outfile.write(CompactJSONEncoder(indent=4).encode(dicti))

def openJSON(fn):
	with open(fr'./output/base/json/{fn}.json' ,mode='r') as jsonFile:
		return json.load(jsonFile)

def openCSV(fn):
	res = []
	with open(fr'./output/base/csv/{fn}.csv' ,mode='r') as csvFile:
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
	#Add in all the desc lines to one attribute
	#Checks if we first have a description to merge
	start = 1
	if 'desc_line1' not in data.keys(): 
		if 'desc_line2' not in data.keys():
			return
		else:
			start = 2
	#Now merges
	desc = []
	for i in range(start,9):
		if data[f'desc_line{i}'] != "Filler":
			desc.append(repU(data[f'desc_line{i}'],True))
		del data[f'desc_line{i}']
	data['description'] = desc

def addAtrToDesc(data):
	#Replaces [ with amount and ] with cooldown
	if 'description' not in data.keys(): return
	if data["Type"] == "Golden Food": return
	newDesc = []
	for line in data['description']:
		added = False
		if '[' in line:
			newDesc.append(line.replace('[',data['Amount']))
			del data['Amount']
			added = True
		if ']' in line:
			newDesc.append(line.replace(']',data['Cooldown']))
			del data['Cooldown']
			added = True
		if '*' in line:
			newDesc.append(line.replace('*',data["Amount"]))
			del data["Amount"]
			added = True
		if '#' in line and "Trigger" in data.keys():
			newDesc.append(line.replace('#',data["Trigger"]))
			del data["Trigger"]
			added = True
		if not added:
			newDesc.append(line)
		
	data['description'] = newDesc

def splitStampData(data):
	#Split the stamp data into a sub atribute
	stampData = data['description'][0].split(',')
	del data['description']
	data['stampData'] = [fix(x) for x in stampData]

def addUpgradeData(data):
	upgrades = data["Effect"].split('.')
	upgrades.reverse()
	del data["Effect"]
	for upgrade in upgrades:
		up, no = upgrade.split(',')
		data['description'].insert(1,f'+{no} {up}')
		
def allItemsStart(items):
	typeToSource = {
		"bOre":"Mining",
		'bBar':"Forging",
		'bLog':"Choppin",
		'bLeaf':"Choppin",
		'dFish':"Fishing",
		'dBugs':"Catching",
		'dCritters':"Trapping",
		'dSouls':"Worshiping?",
	}
	for name,data in items.items():
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
	for name,data in items.items():
		if data["typeGen"] == "aStamp":
			if item := items.get(data["stampData"][5]):
				item["uses"].append((f'[[{nameDic[name]}]]',"Lots","Stamps"))
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
		
		toDel = ["common","consumable","equip"]
		for atr, val in data.items():
			if val in [0,'0']:
				toDel.append(atr)
		for dele in toDel:
			if dele in data.keys():
				del data[dele]
				
	#Remove unused arrays
	for name,data in items.items():	
		if not data["detdrops"]:
			del data["detdrops"]
		if not data["sources"]:
			del data["sources"]
		if not data["uses"]:
			del data["uses"]

def configureDetailedRecipe(items,citem):
	#puts sub recipes into recipes recursively.
	if citem["detrecipe"] == []:
		for req,no in citem["recipeData"]["recipe"]:
			if item := items.get(req):
				if "recipeData" in item.keys():
					if item["detrecipe"] == []:
						configureDetailedRecipe(items,item)
					citem["detrecipe"].append([0] + [req, no])
					citem["detrecipe"] += [[x[0] + 1, x[1], str(int(x[2])*int(no))] for x in item["detrecipe"]]
				else:
					citem["detrecipe"].append([0] + [req,no])

def getDetailedTotals(item):
	i = 0
	counter = 0
	totals = {}
	detrecipe = item["detrecipe"]
	currentDepth = -1
	def addToTotals(item,number):
		totals[item] = totals.get(item,0) + int(number)
	while counter != 4:
		if i == len(detrecipe):
			addToTotals(detrecipe[i-1][1],detrecipe[i-1][2])
			break
		if currentDepth < detrecipe[i][0]:#If we see an item with a higher depth that means there is a sub recipe
			currentDepth = detrecipe[i][0]#we set this to our current depth untill we find the smallest subrecipe
		elif currentDepth == detrecipe[i][0]:#This means we are in the subrecipe
			addToTotals(detrecipe[i-1][1],detrecipe[i-1][2])#We add it, since this is our subrecipe
		else:#If we reach the end of the sub recipe
			addToTotals(detrecipe[i-1][1],detrecipe[i-1][2])
			currentDepth = -1
			counter += 1
		i += 1
	item["detRecipeTotals"] = [(n, v) for n, v in totals.items()]

def deleteFiller(items):
	toDelete = ["EXP","Blank","LockedInvSpace","COIN"]
	for name,data in items.items():
		if data["displayName"] in ['Filler','FILLER','Blank']:
			toDelete.append(name)
	for name in toDelete:
		del items[name]

def droptableToEnem(enemies,droptables):
	dtToEnem = {}
	def addElement(key,element):
		if key in dtToEnem.keys():
			dtToEnem[key].append(element)
		else:
			dtToEnem[key] = [element]
	for name,enem in enemies.items():
		if drops := enem.get("Drops"):
			for drop in drops:
				if drop[0][:9] == "DropTable":
					addElement(drop[0],[f'[[{enem["Name"]}]]'] + drop[1:3])
	for name, droptable in droptables.items():
		for drop in droptable:
			if drop[0][:5] == "Super":
				if dt := dtToEnem.get(name):
					for d in dt:
						addElement(drop[0],[d[0],float(d[1])*float(drop[1]),float(d[2])*float(drop[2])])
	return dtToEnem

def getSmithingRecipe(recipes, name, qty):
	tab = int(name[-1]) -1
	index = int(qty)
	for name,item in recipes[tab].items():
		if int(item["no"]) == index:
			return name

def main():
	#Get all the information saved from jsons
	items = openJSON("Items")
	deleteFiller(items)
	global nameDic 
	nameDic = {name:item["displayName"] for name,item in items.items()}
	cardData = openJSON("CardData")
	fishingTK = openJSON("FishingTK")
	enemies = openJSON("Enemies")
	droptables = openJSON("Droptables")
	dtToEnemies = droptableToEnem(enemies,droptables)
	npcs = openJSON("Npcs")
	recipes = openJSON("Recipes")
	postOffices = openJSON("PostOffice")
	shopData = openJSON("ShopData")
	cauldrons = openJSON("Cauldrens")
	processing = openCSV("Production")
	statueData = openCSV("StatueData")
	taskUnlocks = openJSON("TaskUnlocks")
	#This loop is for specific types of the items
	allItemsStart(items)
	#Adding in the fishing toolkit data
	for typ,datas in fishingTK.items():
		for i,data in enumerate(datas):
			if item := items.get(f"{typ}{i}"):
				item["Fishing"] = data
	#Adding in production data
	for name,time,lvl,exp in processing:
		if item := items.get(name): 
			item['sources'].append('[[Smithing#Production items|Anvil Production]]')
			item['prodInfo'] = {
				"time":time,
				"lvlReq":lvl,
				"expPerItem":exp,
			}
	#Adding in shop data and the source
	for vendor,data in shopData.items():
		for ite in data:
			if item :=items.get(ite["item"]):
				item["sources"].append(f'[[Vendors#{vendor}|{vendor} Vendor]]') 
				item["shopData"] = {
					"vendor": vendor,
					"quantity":ite['quantity'],
					"no":ite['no']
				}
	#Adding in the mob drops as sources for all items
	for name,enemy in enemies.items():
		if drops := enemy.get("Drops"):
			for drop in drops:
				if item := items.get(drop[0]):
					enemName = ''
					if name[0:5] == "Chest":
						enemName = f"Colosseum#{enemy['Name']}|{enemy['Name']}"
					elif False:
						pass
					else:
						enemName = enemy['Name']

					item["sources"].append(f"[[{enemName}]]")
					item["detdrops"].append((f"[[{enemName}]]",drop[1],drop[2]))
	#Adding in the sources from post office shipping rewards and uses from shipping
	for name,po in postOffices.items():
		for req in po["Orders"].keys():
			if item := items.get(req):
				item["uses"].append((f'[[Post Office#{name}|{name}]]',"Lots",'Post Office'))
		for rew in po["Rewards"].keys():
			if item := items.get(rew):
				item["sources"].append(f'[[Post Office#{name}|{name}]]')
	#Adding in all recipes data to the items and adding in uses.
	for tab in recipes:
		for name,recipe in tab.items():
			if item := items.get(name):	
				item["recipeData"] = recipe
				item["detrecipe"] = []
			for sub in recipe["recipe"]:
				if subItem := items.get(sub[0]):
					subItem["uses"].append((f'[[{nameDic[name]}]]',sub[1],"Crafting"))
	#Configure the detailed recipe
	for tab in recipes:
		for name,recipe in tab.items():
			if item := items.get(name):
				configureDetailedRecipe(items,item)
				getDetailedTotals(item)
	#Adding in uses and sources from npcs and quests
	for npc,qdata in npcs.items():
		for dline in qdata:
			#Add in the requirements to the uses of the itmes
			if dline["Type"] == "ItemsAndSpaceRequired":
				requirements = zip(dline['ItemTypeReq'],dline['ItemNumReq'])
				for req,num in requirements:
					if item := items.get(req):
						item["uses"].append((f'[[{npc}#{dline["Name"]}|{dline["Name"]}]]',num,"Quests"))
						if item['typeGen'] == 'dQuest':
							item['questAss'] = f'[[{npc}#{dline["Name"]}|{dline["Name"]}]]'
			#Add in sources for rewards and smithing recipe.
			if dline["Type"] not in  ["None","SpaceRequired","LevelReq"]:
				rewards = dline['Rewards']
				for i in range(len(rewards)):#TalentBook
					if rewards[i][:-1] == "SmithingRecipes":
						if item := items.get(getSmithingRecipe(recipes, rewards[i], rewards[i+1])):
							item["recipeData"]["recipeFrom"] = npc
					elif item := items.get(rewards[i]):
						item["sources"].append(f'[[{npc}#{dline["Name"]}|{dline["Name"]}]]')
	#Add in the cauldrens to used in
	for cname, bubbles in cauldrons.items():
		if name == "Liquid Shop":
			break
		for bname,bubble in bubbles.items():
			for req,n in bubble["requirements"]:
				if item := items.get(req):
					item["uses"].append((f'[[{cname}#{bname}|{bname}]]',"Lots","Alchemy"))
	#add in card data
	for section, cards in cardData.items():
		for name,card in cards.items():
			itemName ="Cards" + card[0]
			if item := items.get(itemName):
				item["cardData"] = [section] + card[1:]
				if desc := item.get("description"):
					if subItem := items.get(desc[0]):
						item["displayName"] = subItem["displayName"] + "_Card"
						subItem['hascard'] = True
				elif enem := enemies.get(name):
					item["displayName"] = enem["Name"] + "_Card"
					enem['hascard'] = True
	#Add in statue data
	for n, data in enumerate(statueData):
		itemN = f"EquipmentStatues{n+1}" 
		if item := items.get(itemN):
			item["statueData"] = data
	#add in subtables sources
	for name, drops in droptables.items():
		for drop in drops:
			if item := items.get(drop[0]):
				item["sources"].append(f"[[{name}]]")
				if detdrops := dtToEnemies.get(name):
					for detdrop in detdrops:
						item['detdrops'].append([
							detdrop[0],
							np.format_float_positional(float(drop[1])*float(detdrop[1]), trim='-'),
							str(float(drop[2])*float(detdrop[2]))
							])
	#Renames the internal to external name
	for tab in recipes:
		for name,recipe in tab.items():
			if item := items.get(name):	
				recipe["recipe"] = [[nameDic[x],y] for x,y in recipe["recipe"]]
				item["recipeData"] = recipe
				item["detrecipe"] = [[x,nameDic[y],z] for x,y,z in item["detrecipe"]]
				item["detRecipeTotals"] = [[nameDic[y],z] for y,z in item["detRecipeTotals"]]
	#Adding in recipe source from the task unlocks
	for taskUnlock in taskUnlocks:
		for ite in taskUnlock:
			if item := items.get(ite):
				if ite == "PremiumGem": continue
				item["recipeData"]["recipeFrom"] = "[[Tasks/Unlocks|Tasks]]"
	allItemsEnd(items)
	writeJSON("Items",items)


if __name__ == '__main__':
	main()
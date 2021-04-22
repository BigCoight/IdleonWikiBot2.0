import json 
import numpy as np
from libs.funcLib import fix
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

def getSmithingRecipe(recipes, name, qty):
	tab = int(name[-1]) -1
	index = int(qty)
	for name,item in recipes[tab].items():
		if int(item["no"]) == index:
			return name

def getTalentName(talentName, qty):
	no = int(qty[0])
	index = int(qty[1:no+1])
	return talentName[index]

def main():
	enemies = openJSON("Enemies")
	recipes = openJSON("Recipes")
	talentNames = openCSV("TalentNames")
	for name,enemy in enemies.items():
		#update drops esp recipe drops and talent books
		if drops := enemy.get("Drops"):
			newDrops = []
			for drop in drops:
				if drop[0][:-1] == "SmithingRecipes":
					dname = getSmithingRecipe(recipes,drop[0],drop[2]) + ";Recipe"
					newDrops.append([dname, drop[1],'1',drop[3]])
				elif drop[0][:-1] == "TalentBook":
					dname = getTalentName(talentNames,drop[2]) + ";Talent_Book"
					newDrops.append([dname, drop[1],'1',drop[3]])
				else:
					newDrops.append(drop)
			enemies[name]["Drops"] = newDrops
		if mType := enemy.get("Type"):
			print(mType)
			enemy["Type"] = mType.split('.')[1]
	writeJSON("Enemies",enemies)

if __name__ == "__main__":
	main()
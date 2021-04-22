import pywikibot
import json

with open(fr'./output/modified/json/Items.json' ,mode='r') as jsonFile:
		items = json.load(jsonFile)
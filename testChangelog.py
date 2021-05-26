import deepdiff
import extractInfo
import json


def openJSON(fn):
    with open(fr'./output/modified/json/{fn}.json', mode='r') as jsonFile:
        return json.load(jsonFile)


extractInfo.main(r'./input/codefile/idleon114b.txt')

itemsOld = openJSON("Items")
print("______________--------------___________________")
extractInfo.main(r'./input/codefile/idleon113.txt')

itemsNew = openJSON("Items")

print(itemsOld - itemsNew)

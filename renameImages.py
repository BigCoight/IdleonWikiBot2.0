from libs.funcLib import fix, repU
import shutil
import os
import json
from types import ClassMethodDescriptorType


def safe_copy(file_path, out_dir, dst=None):
    """Safely copy a file to the specified directory. If a file with the same name already 
    exists, the copied file name is altered to preserve both.

    :param str file_path: Path to the file to copy.
    :param str out_dir: Directory to copy the file into.
    :param str dst: New name for the copied file. If None, use the name of the original
        file.
    """
    name = dst or os.path.basename(file_path)
    if not os.path.exists(os.path.join(out_dir, name)):
        shutil.copy(file_path, os.path.join(out_dir, name))


def openJSON(fn):
    with open(fr"./output/modified/json/{fn}.json", mode="r") as jsonFile:
        return json.load(jsonFile)


def openCSV(fn):
    res = []
    with open(fr"./output/base/csv/{fn}.csv", mode="r") as csvFile:
        lines = csvFile.readlines()
        single = len(lines[0].split(";")) == 1
        if single:
            for line in lines:
                res.append(fix(line))
        else:
            for line in lines:
                res.append(fix(line).split(";"))
    return res


def main():
    items = openJSON("Items")
    for name, item in items.items():
        dispName = item["displayName"].replace(" ", "_")
        try:
            safe_copy(fr"./input/images/{name}.png", r"./output/renamedImages/items/", fr"{dispName}.png")
        except Exception:
            print(f"{dispName} does not exist!")

    talentNames = openCSV("TalentNames")
    formattedTalentNames = [repU(x) for x in talentNames]
    for n, talentName in enumerate(formattedTalentNames):
        try:
            safe_copy(fr"./input/images/UISkillIcon{n}.png", r"./output/renamedImages/skills/", fr"{talentName}.png")
        except Exception:
            print(f"UISkillIcon{n} does not exist!")


if __name__ == "__main__":
    main()

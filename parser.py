#%%
import re


def remove_type_conv(file):
    pattern = r"(?<!\w)\(null == (\w+)\s*\?\s*0[\w\s\d:\?'\"=.\(\),&|]+?\1\)\)\)"
    pattern2 = r"null == (\w+)\s*\?\s*0[\w\s\d:\?'\"=.\(\),&|]+?\1\)\)"
    pattern3 = r"null == (\w+)\s*\|\|\s*\([\w\s\d:\?\"'=.\(\),&|]+\1\)\)\)"
    parsenum = "\nfunction parseNum(num) {\n  let cast = function (a, b) {\n    if (null == a || a instanceof b) return a;\n    throw new Error('Cannot cast ' + String(a) + ' to ' + String(b));\n  }\n  return null == num ? 0\n    : 'number' == typeof num ? cast(num, Number)\n      : 'number' == typeof num && (num | 0) === num ? cast(num, {}) :\n        'boolean' == typeof num ? cast(num, Boolean) ? 1 : 0\n          : 'string' == typeof num ? parseFloat(num) : parseFloat(f.string(num))\n}"
    conv = re.compile(pattern)
    conv2 = re.compile(pattern2)
    conv3 = re.compile(pattern3)
    nfile, n = conv.subn(r"parseNum(\1)", file)
    nfile, n2 = conv2.subn(r"parseNum(\1)", nfile)
    nfile, n3 = conv3.subn(r"parseNum(\1)", nfile)
    nfile = nfile + parsenum
    return nfile, n + n2 + n3


#%%

ver = "122c"  # CHANGE THIS TO THE NAME OF THE INPUT FILE
print(f"Reading {ver}")
with open(rf"./input/codefile/idleon{ver}.txt", "r") as f:
    file = f.read()

nfile, n = remove_type_conv(file)
print(f"Removed {n} type checks")
with open(fr"./input/codefile/idleon{ver}_parsed.txt", "w") as f:
    f.write(nfile)


# %%

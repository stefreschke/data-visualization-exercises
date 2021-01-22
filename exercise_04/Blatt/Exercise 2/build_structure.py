import os
import json

result_structure = {
    "name": "source_repo",
    "children": []
}

def calculateLinesOfCode(dirEntry):
    linesOfCode = 0
    with open(dirEntry.path) as codefile:
        for line in codefile:
            line = line.strip() # removing blanks
            if len(line) > 0: # if line is not empty
                linesOfCode += 1
            # excluding comments would be possible, but very complex -> what if a string contains // or /*
    return linesOfCode

def traverse(path, structure):
    for entry in os.scandir(path):
        new_structure = {}
        new_structure["name"] = entry.name
        if entry.is_dir():
            new_structure["children"] = []
            traverse(entry.path, new_structure)
            if (len(new_structure["children"])):
                structure["children"].append(new_structure)
        else:
            if entry.name.endswith(".cpp") or entry.name.endswith(".h"):
                new_structure["value"] = calculateLinesOfCode(entry)
                structure["children"].append(new_structure)
            else:
                continue

traverse("source_repo", result_structure)

with open('data_structure.json', 'w') as outfile:
    json.dump(result_structure, outfile)

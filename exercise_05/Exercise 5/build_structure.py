import os
import json
import subprocess

edges = []
nodes = {}

def calculateLinesOfCode(dirEntry):
    linesOfCode = 0
    with open(dirEntry.path) as codefile:
        for line in codefile:
            line = line.strip() # removing blanks
            if len(line) > 0: # if line is not empty
                linesOfCode += 1
            # excluding comments would be possible, but very complex -> what if a string contains // or /*
    return linesOfCode

def traverse(path, counter):
    self_count = counter
    append_edges = []
    for entry in os.scandir(path):
        if entry.is_dir():
            new_counter, sub_edges = traverse(entry.path, counter + 1)
            if (len(sub_edges) > 0):
                nodes[counter + 1] = {'name': entry.name, 'is_leave': False, 'path': entry.path}
                append_edges.append([self_count, counter + 1])
                counter = new_counter
                append_edges.extend(sub_edges)

        else:
            if entry.name.endswith(".cpp") or entry.name.endswith(".h") or entry.name.endswith(".py"):
                nodes[counter + 1] = {'name': entry.name, 'is_leave': True, 'path': entry.path}
                append_edges.append([self_count, counter +1])
                counter += 1
                calculateLinesOfCode(entry)
            else:
                continue
    return counter, append_edges

print("Attenzione: Computing (several minutes) may take a while. Please be patient.")
# Add source node
nodes[0] = {'name': "source_repo", 'is_leave': False, 'path': "source_repo"}
# Traverse dir
ret_counter, ret_edges = traverse("source_repo", 0)

# Get number of commits
run = os.popen('cd source_repo; git log --name-only --pretty=format: | sort | uniq -c')
commit_count = run.read()
commit_counts_by_path = {}
for i, line in enumerate(commit_count.split("\n")):
    splitted = line.strip().split(" ")
    if len(splitted) != 2:
        continue
    commit_counts_by_path["source_repo/" + splitted[1]] = splitted[0]

commits_per_file = []
for key in nodes:
    node = nodes[key]
    if node['is_leave']:
        if node['path'] in commit_counts_by_path:
            commits_per_file.append(int(commit_counts_by_path[node['path']]))
        else:
            commits_per_file.append(0)

# Get number of authors per file
authors_per_file = []
for key in nodes:
    node = nodes[key]
    if node['is_leave']:
        run = os.popen("cd source_repo; git blame -p " + node['path'][12:] + " | grep -e '^author ' | sort | uniq | wc -l")
        authors_per_file.append(int(run.read().split("\n")[0]))

# Get labels
labels = []
for key in nodes:
    labels.append(nodes[key]['name'])


print("Here are the results:")

print("Tree structure")
print(ret_edges)

print("Labels")
print(labels)

print("Commits per file")
print(commits_per_file)

print("Authors per file")
print(authors_per_file)

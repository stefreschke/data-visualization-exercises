import os
import json
import subprocess
import git
import numpy as np

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
                nodes[counter + 1] = {'name': entry.name, 'is_leave': False, 'path': entry.path, 'loc': 0}
                append_edges.append([self_count, counter + 1])
                counter = new_counter
                append_edges.extend(sub_edges)

        else:
            if entry.name.endswith(".cpp") or entry.name.endswith(".h") or entry.name.endswith(".py"):
                nodes[counter + 1] = {'name': entry.name, 'is_leave': True, 'path': entry.path, 'loc': calculateLinesOfCode(entry)}
                append_edges.append([self_count, counter +1])
                counter += 1
            else:
                continue
    return counter, append_edges

print("Attenzione: Computing may take a while (several minutes). Please be patient.")
# Add source node
nodes[0] = {'name': "source_repo", 'is_leave': False, 'path': "source_repo", 'loc': 0}
# Traverse dir
ret_counter, ret_edges = traverse("source_repo", 0)
g = git.Git("source_repo")

# Get number of commits
log = g.log("--name-only", "--pretty=format:").split("\n")
(files, counts) = np.unique(log, return_counts=True)
commit_counts_by_path = {}
for line, count in zip(files, counts):
    commit_counts_by_path["source_repo/" + line] = count

commits_per_file = []
for key in sorted(nodes):
    node = nodes[key]
    if node['is_leave']:
        if node['path'] in commit_counts_by_path:
            commits_per_file.append(int(commit_counts_by_path[node['path']]))
        else:
            commits_per_file.append(0)
    else:
        commits_per_file.append(0)

# Get number of authors per file
authors_per_file = []
for key in sorted(nodes):
    node = nodes[key]
    if node['is_leave']:
        blame = g.blame("-p", node['path'][12:]).split("\n")
        authors = [ author for author in blame if author.startswith("author ")]
        num_authors = len(np.unique(authors))
        authors_per_file.append(num_authors)
    else:
        authors_per_file.append(0)

# Get labels and lines of code
labels = []
loc = []
for key in sorted(nodes):
    labels.append(nodes[key]['name'])
    loc.append(nodes[key]['loc'])




print("Here are the results:")

print("Tree structure")
print(ret_edges)

print("Labels")
print(labels)

print("Lines of code")
print(loc)

print("Commits per file")
print(commits_per_file)

print("Authors per file")
print(authors_per_file)

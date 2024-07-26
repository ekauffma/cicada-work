import os
import json

datasets = ["Muon0", "JetMET0", "Tau"]
directories = ["/hdfs/store/user/ekauffma/Muon0/", "/hdfs/store/user/ekauffma/JetMET0", "/hdfs/store/user/ekauffma/Tau"]

def list_root_files(directory):
    root_files = []
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.root'):
                full_path = os.path.join(dirpath, filename)
                root_files.append(full_path)
    return root_files

filePaths = {}
for i in range(len(datasets)):
    filePaths[datasets[i]] = root_files = list_root_files(directories[i])

with open("filePaths.json", "w") as outfile:
    json.dump(filePaths, outfile)

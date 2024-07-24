import os
import json

datasets = ["Muon0"]
directories = ["/hdfs/store/user/ekauffma/Muon0/CICADA_Muon0_Run2024F_v1_a_20240723/"]

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

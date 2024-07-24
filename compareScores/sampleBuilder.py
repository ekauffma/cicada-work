import sys
import os
import json

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from sample import sample

f = open("filePaths.json")
filePaths = json.load(f)

treeNames_unpacked = [
    'l1EventTree/L1EventTree',
    'l1CaloSummaryTree/L1CaloSummaryTree',
]

treeNames_emulated = [
    'l1EventTree/L1EventTree',
    'l1CaloSummaryEmuTree/L1CaloSummaryTree'
]

samples_unpacked = dict(
    [
        (
            sampleName,
            sample(listOfFiles = filePaths[sampleName], treeNames = treeNames_unpacked)
        )
        for sampleName in filePaths
    ]
)

samples_emulated = dict(
    [
        (
            sampleName,
            sample(listOfFiles = filePaths[sampleName], treeNames = treeNames_emulated)
        )
        for sampleName in filePaths
    ]
)

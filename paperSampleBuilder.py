########################################################################
## paperSampleBuilder.py                                              ##
## Author: Andrew Loeliger, modified by Elliott Kauffman              ##
## A generic template for samples for the paper                       ##
########################################################################
from sample import sample
import os
import json

# load json file
f = open("filePaths.json")
filePaths = json.load(f)

# the ROOT trees we care about
treeNames = [
    'l1EventTree/L1EventTree',
    'l1CaloTowerEmuTree/L1CaloTowerTree',
    'l1UpgradeTree/L1UpgradeTree',
    'L1TTriggerBitsNtuplizer/L1TTriggerBits',
    #'CICADA_v1p2p0_Ntuplizer/CICADA_v1p2p0',
    #'CICADA_v2p2p0_Ntuplizer/CICADA_v2p2p0',
    #'CICADA_v1p2p0N_Ntuplizer/CICADA_v1p2p0N',
    #'CICADA_v2p2p0N_Ntuplizer/CICADA_v2p2p0N',
    #'CICADA_v1p2p1_Ntuplizer/CICADA_v1p2p1',
    #'CICADA_v2p2p1_Ntuplizer/CICADA_v2p2p1',
    #'CICADA_v1p2p1N_Ntuplizer/CICADA_v1p2p1N',
    #'CICADA_v2p2p1N_Ntuplizer/CICADA_v2p2p1N',
    'CICADA_v1p2p2_Ntuplizer/CICADA_v1p2p2',
    'CICADA_v2p2p2_Ntuplizer/CICADA_v2p2p2',
    'CICADA_v1p2p2N_Ntuplizer/CICADA_v1p2p2N',
    'CICADA_v2p2p2N_Ntuplizer/CICADA_v2p2p2N'
    #'CICADA_vXp2p0_Teacher_Ntuplizer/CICADA_vXp2p0_teacher',
    #'CICADA_vXp2p0N_Teacher_Ntuplizer/CICADA_vXp2p0N_teacher',
    #'CICADA_vXp2p1_Teacher_Ntuplizer/CICADA_vXp2p1_teacher',
    #'CICADA_vXp2p1N_Teacher_Ntuplizer/CICADA_vXp2p1N_teacher'
]

# function for building sample object from files
def buildSample(paths, treeNames):
    theSample = sample(
        listOfFiles = paths,
        treeNames = treeNames,
    )
    return theSample

# create dictionary of samples with keys corresponding to sample name
samples = dict(
    [
        (
            sampleName,
            buildSample(filePaths[sampleName], treeNames)
        )
        for sampleName in filePaths
    ]
)

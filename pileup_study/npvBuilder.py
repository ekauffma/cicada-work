########################################################################
########################################################################
from sample import sample
import os

filePath = "ZeroBias_NPV.root"

filePaths = {
    "ZeroBias": [filePath]
}

# the ROOT trees we care about
treeNames = [
    'PUVertexNtuplizer/PUVertexNtuple',
    'CICADA_v1p2p2_Ntuplizer/CICADA_v1p2p2',
    'CICADA_v2p2p2_Ntuplizer/CICADA_v2p2p2',
    'CICADA_v1p2p2N_Ntuplizer/CICADA_v1p2p2N',
    'CICADA_v2p2p2N_Ntuplizer/CICADA_v2p2p2N'
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
            "ZeroBias",
            buildSample(filePaths[sampleName], treeNames)
        )
        for sampleName in filePaths
    ]
)

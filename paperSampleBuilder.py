# A generic template for samples for the paper
from sample import sample
import os

basePath = '/hdfs/store/user/aloelige/'

# sampleDates = {
#         "22Jan2024": [
#             "WToTauTo3Mu_TuneCP5_13p6TeV_pythia8",
#             "HTo2LongLivedTo4b_MH-350_MFF-80_CTau-1000mm_TuneCP5_13p6TeV-pythia8",
#             "GluGlutoHHto4B_kl-1p00_kt-1p00_c2-3p00_TuneCP5_13p6TeV_powheg-pythia8",
#             "ggXToYYTo2mu2e_m14_pseudoscalar_TuneCP5_13p6TeV_jhugen-pythia8",
#             "HTo2LongLivedTo4b_MH-125_MFF-50_CTau-3000mm_TuneCP5_13p6TeV-pythia8",
#             "HTo2LongLivedTo4b_MH-250_MFF-120_CTau-1000mm_TuneCP5_13p6TeV-pythia8",
#             "GluGlutoHHto4B_kl-0p00_kt-1p00_c2-0p00_TuneCP5_13p6TeV_powheg-pythia8",
#             "HTo2LongLivedTo4b_MH-250_MFF-120_CTau-10000mm_TuneCP5_13p6TeV-pythia8",
#             "HHHto4B2Tau_c3-0_d4-0_TuneCP5_13p6TeV_amcatnlo-pythia8",
#             "SUSYGluGluToBBHToBB_NarrowWidth_M-1200_TuneCP5_13p6TeV-pythia8",
#             "HTo2LongLivedTo4b_MH-350_MFF-80_CTau-10000mm_TuneCP5_13p6TeV-pythia8",
#             "HTo2LongLivedTo4b_MH-350_MFF-160_CTau-500mm_TuneCP5_13p6TeV-pythia8",
#             "ttHto2B_M-125_TuneCP5_13p6TeV_powheg-pythia8",
#             "HTo2LongLivedTo4b_MH-125_MFF-12_CTau-9000mm_TuneCP5_13p6TeV-pythia8",
#             "HTo2LongLivedTo4b_MH-250_MFF-60_CTau-10000mm_TuneCP5_13p6TeV-pythia8",
#             "GluGlutoHHto4B_kl-1p00_kt-1p00_c2-0p10_TuneCP5_13p6TeV_powheg-pythia8",
#             "HTo2LongLivedTo4mu_MH-125_MFF-25_CTau-1500mm_TuneCP5_13p6TeV-pythia8",
#             "HTo2LongLivedTo4b_MH-1000_MFF-450_CTau-10000mm_TuneCP5_13p6TeV-pythia8",
#             "GluGluHToGG_M-90_TuneCP5_13p6TeV_powheg-pythia8",
#             "GluGlutoHHto4B_kl-1p00_kt-1p00_c2-m2p00_TuneCP5_13p6TeV_powheg-pythia8",
#             "HTo2LongLivedTo4mu_MH-125_MFF-50_CTau-3000mm_TuneCP5_13p6TeV-pythia8",
#             "HTo2LongLivedTo4b_MH-125_MFF-50_CTau-30000mm_TuneCP5_13p6TeV-pythia8",
#             "GluGlutoHHto4B_kl-1p00_kt-1p00_c2-0p00_TuneCP5_13p6TeV_powheg-pythia8",
#             "HTo2LongLivedTo4b_MH-250_MFF-60_CTau-500mm_TuneCP5_13p6TeV-pythia8",
#             "SingleNeutrino_E-10-gun",
#             "SMS-Higgsino_mN2-170_mC1-160_mN1-150_HT-60_TuneCP5_13p6TeV_pythia8",
#             "GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8",
#             "SUSYGluGluToBBHToBB_NarrowWidth_M-350_TuneCP5_13p6TeV-pythia8",
#             "WToTauToMuMuMu_TuneCP5_13p6TeV-pythia8",
#             "HTo2LongLivedTo4b_MH-350_MFF-160_CTau-10000mm_TuneCP5_13p6TeV-pythia8",
#             "ggXToJpsiJpsiTo2mu2e_m7_pseudoscalar_TuneCP5_13p6TeV_jhugen-pythia8",
#             "HTo2LongLivedTo4b_MH-125_MFF-25_CTau-15000mm_TuneCP5_13p6TeV-pythia8",
#             "HHHTo6B_c3_0_d4_0_TuneCP5_13p6TeV_amcatnlo-pythia8",
#             "GluGlutoHHto4B_kl-5p00_kt-1p00_c2-0p00_TuneCP5_13p6TeV_powheg-pythia8",
#             "ttHto2C_M-125_TuneCP5_13p6TeV_powheg-pythia8",
#             "VBFHToInvisible_M-125_TuneCP5_13p6TeV_powheg-pythia8",
#             "TT_TuneCP5_13p6TeV_powheg-pythia8",
#             "GluGluHToTauTau_M-125_TuneCP5_13p6TeV_powheg-pythia8",
#             "HTo2LongLivedTo4b_MH-250_MFF-60_CTau-1000mm_TuneCP5_13p6TeV-pythia8",
#             "GluGluXToYYTo2Mu2E_M18_pseudoscalar_TuneCP5_13p6TeV_jhugen-pythia8",
#             "HTo2LongLivedTo4b_MH-250_MFF-120_CTau-500mm_TuneCP5_13p6TeV-pythia8",
#             "HTo2LongLivedTo4b_MH-125_MFF-25_CTau-1500mm_TuneCP5_13p6TeV-pythia8",
#             "HTo2LongLivedTo4mu_MH-125_MFF-12_CTau-900mm_TuneCP5_13p6TeV_pythia8",
#             "SUSYGluGluToBBHToBB_NarrowWidth_M-600_TuneCP5_13p6TeV-pythia8",
#             "GluGluHToGG_M-125_TuneCP5_13p6TeV_powheg-pythia8",
#             "VBFHto2B_M-125_TuneCP5_13p6TeV_powheg-pythia8",
#             "HTo2LongLivedTo4b_MH-350_MFF-160_CTau-1000mm_TuneCP5_13p6TeV-pythia8",
#             "GluGlutoHHto4B_kl-0p00_kt-1p00_c2-1p00_TuneCP5_13p6TeV_powheg-pythia8",
#             "VBFHToTauTau_M125_TuneCP5_13p6TeV_powheg-pythia8",
#             "HTo2LongLivedTo4b_MH-125_MFF-12_CTau-900mm_TuneCP5_13p6TeV-pythia8",
#             "GluGlutoHHto4B_kl-1p00_kt-1p00_c2-0p35_TuneCP5_13p6TeV_powheg-pythia8",
#             "HTo2LongLivedTo4b_MH-350_MFF-80_CTau-500mm_TuneCP5_13p6TeV-pythia8",
#             "GluGlutoHHto4B_kl-2p45_kt-1p00_c2-0p00_TuneCP5_13p6TeV_powheg-pythia8",
#             "SUSYGluGluToBBHToBB_NarrowWidth_M-120_TuneCP5_13p6TeV-pythia8",
#         ],
#         "29Jan2024": [
#             "GluGluHToGG_M-90_TuneCP5_13p6TeV_powheg-pythia8",
#             "GluGluHToGG_M-125_TuneCP5_13p6TeV_powheg-pythia8",
#             "VBFHToInvisible_M-125_TuneCP5_13p6TeV_powheg-pythia8",
#             "VBFHToCC_M-125_TuneCP5_13p6TeV_powheg-pythia8",
#             "ZToMuMu_M-120To200_TuneCP5_13p6TeV_powheg-pythia8",
#             "ZToMuMu_M-200To400_TuneCP5_13p6TeV_powheg-pythia8",
#         ]
# }

sampleDates = {
    "05Feb2024": [
        "GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8",
        "GluGluHToGG_M-125_TuneCP5_13p6TeV_powheg-pythia8",
        "GluGluHToTauTau_M-125_TuneCP5_13p6TeV_powheg-pythia8",
        "GluGluXToYYTo2Mu2E_M18_pseudoscalar_TuneCP5_13p6TeV_jhugen-pythia8",
        "HHHTo6B_c3_0_d4_0_TuneCP5_13p6TeV_amcatnlo-pythia8",
        "HHHto4B2Tau_c3-0_d4-0_TuneCP5_13p6TeV_amcatnlo-pythia8",
        "VBFHToTauTau_M125_TuneCP5_13p6TeV_powheg-pythia8",
        "VBFHto2B_M-125_TuneCP5_13p6TeV_powheg-pythia8",
        "WToTauTo3Mu_TuneCP5_13p6TeV_pythia8",
        "WToTauToMuMuMu_TuneCP5_13p6TeV-pythia8",
        "ggXToYYTo2mu2e_m14_pseudoscalar_TuneCP5_13p6TeV_jhugen-pythia8",
        "ggXToJpsiJpsiTo2mu2e_m7_pseudoscalar_TuneCP5_13p6TeV_jhugen-pythia8",
        "ttHto2B_M-125_TuneCP5_13p6TeV_powheg-pythia8",
        "ttHto2C_M-125_TuneCP5_13p6TeV_powheg-pythia8",
        "SMS-Higgsino_mN2-170_mC1-160_mN1-150_HT-60_TuneCP5_13p6TeV_pythia8",
        "TT_TuneCP5_13p6TeV_powheg-pythia8",
        "HTo2LongLivedTo4b_MH-1000_MFF-450_CTau-100000mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4b_MH-1000_MFF-450_CTau-10000mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4b_MH-125_MFF-12_CTau-9000mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4b_MH-125_MFF-12_CTau-900mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4b_MH-125_MFF-25_CTau-15000mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4b_MH-125_MFF-25_CTau-1500mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4b_MH-125_MFF-50_CTau-30000mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4b_MH-125_MFF-50_CTau-3000mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4b_MH-250_MFF-120_CTau-10000mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4b_MH-250_MFF-120_CTau-1000mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4b_MH-250_MFF-120_CTau-500mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4b_MH-250_MFF-60_CTau-10000mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4b_MH-250_MFF-60_CTau-1000mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4b_MH-250_MFF-60_CTau-500mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4b_MH-350_MFF-160_CTau-10000mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4b_MH-350_MFF-160_CTau-1000mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4b_MH-350_MFF-160_CTau-500mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4b_MH-350_MFF-80_CTau-10000mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4b_MH-350_MFF-80_CTau-1000mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4b_MH-350_MFF-80_CTau-500mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4mu_MH-1000_MFF-450_CTau-10000mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4mu_MH-125_MFF-12_CTau-900mm_TuneCP5_13p6TeV_pythia8",
        "HTo2LongLivedTo4mu_MH-125_MFF-25_CTau-1500mm_TuneCP5_13p6TeV-pythia8",
        "HTo2LongLivedTo4mu_MH-125_MFF-50_CTau-3000mm_TuneCP5_13p6TeV-pythia8",
        "SUSYGluGluToBBHToBB_NarrowWidth_M-1200_TuneCP5_13p6TeV-pythia8",
        "SUSYGluGluToBBHToBB_NarrowWidth_M-120_TuneCP5_13p6TeV-pythia8",
        "SUSYGluGluToBBHToBB_NarrowWidth_M-350_TuneCP5_13p6TeV-pythia8",
        "SUSYGluGluToBBHToBB_NarrowWidth_M-600_TuneCP5_13p6TeV-pythia8",
        "SingleNeutrino_E-10-gun",
        "GluGluHToGG_M-90_TuneCP5_13p6TeV_powheg-pythia8",
        "GluGluHToGG_M-125_TuneCP5_13p6TeV_powheg-pythia8",
        "VBFHToInvisible_M-125_TuneCP5_13p6TeV_powheg-pythia8",
        "VBFHToCC_M-125_TuneCP5_13p6TeV_powheg-pythia8",
        "ZToMuMu_M-120To200_TuneCP5_13p6TeV_powheg-pythia8",
        "ZToMuMu_M-200To400_TuneCP5_13p6TeV_powheg-pythia8",
        "ZeroBias",
    ]
}

samplePaths = {}
for date in sampleDates:
    for sampleName in sampleDates[date]:
        samplePaths[sampleName] = os.path.join(
            basePath,
            f'{sampleName}/Paper_Ntuples_{date}/'
        )

# Add the SUEPS by hand
# samplePaths["SUEP"] = "/hdfs/store/user/aloeliger/SUEP_Paper_Analysis/08Jan2024/"
samplePaths["SUEP"] = "/hdfs/store/user/aloeliger/SUEP_Paper_Analysis/05Feb2024/"

treeNames = [
    'l1EventTree/L1EventTree',
    #'l1CaloTowerEmuTree/L1CaloTowerTree',
    'l1UpgradeTree/L1UpgradeTree',
    'CICADA_v1p2p0_Ntuplizer/CICADA_v1p2p0',
    'CICADA_v2p2p0_Ntuplizer/CICADA_v2p2p0',
    'CICADA_v1p2p0N_Ntuplizer/CICADA_v1p2p0N',
    'CICADA_v2p2p0N_Ntuplizer/CICADA_v2p2p0N',
]

def buildSample(path, treeNames):
    theFiles = []
    for root, dirs, files in os.walk(path, topdown=True):
        for fileName in files:
            theFiles.append(os.path.join(root, fileName))
    theSample = sample(
        listOfFiles = theFiles,
        treeNames = treeNames,
    )
    return theSample

samples = dict(
    [
        (
            sampleName,
            buildSample(samplePaths[sampleName], treeNames)
        )
        for sampleName in samplePaths
    ]
)

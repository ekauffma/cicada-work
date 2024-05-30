########################################################################
## calculateUnprescaledTriggerEfficiency.py                           ##
## Author: Elliott Kauffman                                           ##
## calculate the unprescaled trigger efficiencies for ROC plots       ##
########################################################################

import ROOT
import argparse
import numpy as np
from triggers import triggers
import awkward as ak
import uproot
import os

basePath = '/hdfs/store/user/aloelige/'

sampleDates = {
    "27Mar2024": [
        "GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8",
        "GluGluHToGG_M-125_TuneCP5_13p6TeV_powheg-pythia8",
        "GluGluHToTauTau_M-125_TuneCP5_13p6TeV_powheg-pythia8",
        "GluGluXToYYTo2Mu2E_M18_pseudoscalar_TuneCP5_13p6TeV_jhugen-pythia8",
        "HHHTo6B_c3_0_d4_0_TuneCP5_13p6TeV_amcatnlo-pythia8",
        #"HHHto4B2Tau_c3-0_d4-0_TuneCP5_13p6TeV_amcatnlo-pythia8", #failed
        "VBFHToTauTau_M125_TuneCP5_13p6TeV_powheg-pythia8",
        "VBFHto2B_M-125_TuneCP5_13p6TeV_powheg-pythia8",
        "WToTauTo3Mu_TuneCP5_13p6TeV_pythia8",
        "WToTauToMuMuMu_TuneCP5_13p6TeV-pythia8",
        "ggXToYYTo2mu2e_m14_pseudoscalar_TuneCP5_13p6TeV_jhugen-pythia8",
        #"ggXToJpsiJpsiTo2mu2e_m7_pseudoscalar_TuneCP5_13p6TeV_jhugen-pythia8", #failed
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
        #"HTo2LongLivedTo4b_MH-350_MFF-160_CTau-500mm_TuneCP5_13p6TeV-pythia8", #failed
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
        #"GluGluHToGG_M-90_TuneCP5_13p6TeV_powheg-pythia8", #failed
        "GluGluHToGG_M-125_TuneCP5_13p6TeV_powheg-pythia8",
        #"VBFHToInvisible_M-125_TuneCP5_13p6TeV_powheg-pythia8", #failed
        "VBFHToCC_M-125_TuneCP5_13p6TeV_powheg-pythia8",
        #"ZToMuMu_M-120To200_TuneCP5_13p6TeV_powheg-pythia8", #failed
        #"ZToMuMu_M-200To400_TuneCP5_13p6TeV_powheg-pythia8", #failed
        "ZeroBias",
    ],
    '28Mar2024': [
        "HHHto4B2Tau_c3-0_d4-0_TuneCP5_13p6TeV_amcatnlo-pythia8",
        "ggXToJpsiJpsiTo2mu2e_m7_pseudoscalar_TuneCP5_13p6TeV_jhugen-pythia8",
        "HTo2LongLivedTo4b_MH-350_MFF-160_CTau-500mm_TuneCP5_13p6TeV-pythia8",
        "GluGluHToGG_M-90_TuneCP5_13p6TeV_powheg-pythia8",
        "VBFHToInvisible_M-125_TuneCP5_13p6TeV_powheg-pythia8",
        "ZToMuMu_M-120To200_TuneCP5_13p6TeV_powheg-pythia8",
        "ZToMuMu_M-200To400_TuneCP5_13p6TeV_powheg-pythia8",
    ]
}

treeName = "L1TTriggerBitsNtuplizer/L1TTriggerBits"

def main(nBins):

    print("Starting...")

    samplePaths = {}
    for date in sampleDates:
        for sampleName in sampleDates[date]:
            samplePaths[sampleName] = os.path.join(
                basePath,
                f'{sampleName}/Paper_Ntuples_{date}/'
            )
    samplePaths["SUEP"] = "/hdfs/store/user/aloeliger/SUEP_Paper_Analysis/25Apr2024/"

    print("Got samplePaths")

    # get list of sample names
    sample_names = list(samplePaths.keys())

    j = 0
    for root, dirs, files in os.walk(samplePaths["ZeroBias"], topdown=True):
        print("root = ", root)
        for fileName in files:

            print(fileName)
            f = uproot.open(os.path.join(root, fileName))
            tree = f[treeName]
            to_remove = []

            for i in range(len(triggers)):
                try:
                    prescales = tree[f"{triggers[i]}_prescale"].array()
                except Exception:
                    print("Trigger not found: ", triggers[i])
                if len(prescales)==0: continue
                if (sum(prescales)/len(prescales)!=1):
                    to_remove.append(triggers[i])
                    #print("Removing ", triggers[i])

            for i in range(len(to_remove)):
                triggers.remove(to_remove[i])

            f.close()

            j+=1
            if j>30: break

    for i in range(len(sample_names)):

        if sample_names[i] in sampleDates['27Mar2024']: continue

        print(sample_names[i], end=" ")
        total_events = 0
        pass_events = 0

        for root, dirs, files in os.walk(samplePaths[sample_names[i]], topdown=True):
            for fileName in files:
                f = uproot.open(os.path.join(root, fileName))
                tree = f[treeName]
                try:
                    trig_arr = np.zeros((len(triggers), len(tree[triggers[-1]].array())))
                except Exception:
                    print("bad file")
                    continue
                for j in range(len(triggers)):
                    try:
                        trig_arr[j,:] = tree[triggers[j]].array()
                    except Exception:
                        print("Could not access trigger", triggers[j])
                trig_results = ak.any(trig_arr, axis=0)
                total_events += len(trig_results)
                pass_events += sum(trig_results)

        print(pass_events/total_events)


if __name__ == "__main__":

	parser = argparse.ArgumentParser(
        description="This program creates CICADA score and HT histograms"
    )
	parser.add_argument(
        "-n",
        "--n_bins",
        default=100,
        help="number of bins")

	args = parser.parse_args()

	main( args.n_bins)

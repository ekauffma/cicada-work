########################################################################
## createHistsForROC.py                                               ##
## Author: Elliott Kauffman                                           ##
## make score and rate histograms for CICADA                          ##
########################################################################

import ROOT
import argparse
import numpy as np
from paperSampleBuilder import samples
from triggers import triggers as trig_list
import json
import uproot
import awkward as ak


# names of CICADA models
cicada_names = ["CICADA_v1p2p2",
                "CICADA_v2p2p2",
                "CICADA_v1p2p2N",
                "CICADA_v2p2p2N"]

# minimum and maximum scores for histogram
min_score_cicada = 0.0
max_score_cicada = 1024.0
n_bins_cicada = 400
min_score_ht = 0.0
max_score_ht = 2000.0
n_bins_ht = 300
min_score_trig = -0.5
max_score_trig = 1.5
n_bins_trig = 2
min_score_pt = 0.0
max_score_pt = 1000.0
n_bins_pt = 300


# Create a C++ lambda function for OR operation as a string
or_operation_cpp = """
int OROperation(const ROOT::VecOps::RVec<int>& cols) {
    for (auto col : cols) {
        if (col!=0) return 1;
    }
    return 0;
}
"""

def getUnprescaledTriggers(triggerlist):

    with open("filePaths.json") as f:
        f = open("filePaths.json")
        filePaths = json.load(f)["ZeroBias"]

    j = 0
    for filePath in filePaths:
        f = uproot.open(filePath)
        tree = f["L1TTriggerBitsNtuplizer/L1TTriggerBits"]
        to_remove = []

        for i in range(len(triggerlist)):

            try:
                prescales = tree[f"{triggerlist[i]}_prescale"].array()
            except Exception:
                print("Trigger not found: ", triggerlist[i])
                continue
            if len(prescales)==0: continue
            if (sum(prescales)/len(prescales)!=1):
                to_remove.append(triggerlist[i])

        for i in range(len(to_remove)):
            triggerlist.remove(to_remove[i])

        j+=1
        if j > 30: break

    with open("unprescaledTriggers.json", "w") as final:
        json.dump(triggerlist, final)


    return triggerlist



def main(out_prefix):
    # get unprescaled triggers (filter out prescaled triggers from list)
    with open("unprescaledTriggerTables.json", "r") as f:
        triggers = json.load(f)["unprescaledTriggers"]

    # Create a C++ function dynamically for the OR operation
    cpp_code = """
    #include <ROOT/RVec.hxx>
    using namespace ROOT::VecOps;

    int OROperation(const RVec<int>& cols) {
        for (auto col : cols) {
            if (col != 0) return 1;
        }
        return 0;
    }
    """

    # compile cpp code
    ROOT.gInterpreter.Declare(cpp_code)

    columns_str = ", ".join(triggers)
    function_call = f"OROperation({{{columns_str}}})"

    # get list of sample names and remove ZeroBias
    sample_names = list(samples.keys())
    if 'ZeroBias' in sample_names:
        sample_names.remove('ZeroBias')

    # get zerobias and filter out training events
    zero_bias = samples['ZeroBias'].getNewDataframe()

    # create column for HT
    zero_bias = zero_bias.Define("sum_mask", "(sumBx==0) && (sumType==1)")
    zero_bias = zero_bias.Define("HT", "sumEt[sum_mask]")

    # create column for whether events pass any unprescaled triggers
    zero_bias = zero_bias.Define("L1UnprescaledOR", function_call)

    zero_bias = zero_bias.Define("leadJetEt", """
    auto leadingJetEt = [](const ROOT::RVec<float>& jetEt) {
        return jetEt.size() > 0 ? jetEt[0] : -1.0f;
    };
    return leadingJetEt(jetEt);
""", ["L1Upgrade/jetEt"])

    # separate out test and train data
    zero_bias_test = zero_bias.Filter('lumi % 2 == 1')
    zero_bias_train = zero_bias.Filter('lumi % 2 == 0')

    #array = ak.from_rdataframe(zero_bias_test, columns=("L1UnprescaledOR",))
    #print(array)
    l1unprescaledor = zero_bias_test.AsNumpy(columns=["L1UnprescaledOR"])
    print("ZB Efficiency = ", sum(l1unprescaledor["L1UnprescaledOR"])/len(l1unprescaledor["L1UnprescaledOR"]))



    # create file for zerobias hists
    print("Sample: ZeroBias")
    output_file = ROOT.TFile(f"{out_prefix}_ZeroBias.root", "RECREATE")

    # create and fill CICADA score histograms for zerobias
    for i in range(len(cicada_names)):
        print("    CICADA VERSION: ", cicada_names[i])

        histModel = ROOT.RDF.TH3DModel(
            f"anomalyScore_ZeroBias_test_{cicada_names[i]}",
            f"anomalyScore_ZeroBias_test_{cicada_names[i]}",
            n_bins_cicada,
            min_score_cicada,
            max_score_cicada,
            n_bins_ht,
            min_score_ht,
            max_score_ht,
            n_bins_trig,
            min_score_trig,
            max_score_trig,
        )

        hist = zero_bias_test.Histo3D(
            histModel,
            f"{cicada_names[i]}_score",
            "HT",
            "L1UnprescaledOR"
        )
        print("        Bin Content Example 1 = ", hist.GetBinContent(10, 2, 2))
        print("        Bin Content Example 2 = ", hist.GetBinContent(5, 1, 1))
        hist.Write()


        histModel = ROOT.RDF.TH3DModel(
            f"anomalyScore_ZeroBias_train_{cicada_names[i]}",
            f"anomalyScore_ZeroBias_train_{cicada_names[i]}",
            n_bins_cicada,
            min_score_cicada,
            max_score_cicada,
            n_bins_ht,
            min_score_ht,
            max_score_ht,
            n_bins_trig,
            min_score_trig,
            max_score_trig
        )

        hist = zero_bias_train.Histo3D(
            histModel,
            f"{cicada_names[i]}_score",
            "HT",
            "L1UnprescaledOR"
        )
        hist.Write()

        histModel = ROOT.RDF.TH1DModel(
            f"jetEt_ZeroBias_test_{cicada_names[i]}",
            f"jetEt_ZeroBias_test_{cicada_names[i]}",
            n_bins_pt,
            min_score_pt,
            max_score_pt
        )

        hist = zero_bias_test.Filter("leadJetEt >= 0").Histo1D(histModel, "leadJetEt")
        hist.Write()

        histModel = ROOT.RDF.TH1DModel(
            f"jetEt_ZeroBias_train_{cicada_names[i]}",
            f"jetEt_ZeroBias_train_{cicada_names[i]}",
            n_bins_pt,
            min_score_pt,
            max_score_pt
        )

        hist = zero_bias_train.Filter("leadJetEt >= 0").Histo1D(histModel, "leadJetEt")
        hist.Write()

    output_file.Write()
    output_file.Close()


    # create and write hists for each sample
    for k in range(len(sample_names)):
        print(f"Sample: {sample_names[k]}")
        output_file = ROOT.TFile(f"{out_prefix}_{sample_names[k]}.root", "RECREATE")

        rdf = samples[sample_names[k]].getNewDataframe()
        rdf = rdf.Define("sum_mask", "(sumBx==0) && (sumType==1)")
        rdf = rdf.Define("HT", "sumEt[sum_mask]")

        rdf = rdf.Define("L1UnprescaledOR", function_call)

        rdf = rdf.Define("leadJetEt", """
    auto leadingJetEt = [](const ROOT::RVec<float>& jetEt) {
        return jetEt.size() > 0 ? jetEt[0] : -1.0f;
    };
    return leadingJetEt(jetEt);
""", ["L1Upgrade/jetEt"])

        l1unprescaledor = rdf.AsNumpy(columns=["L1UnprescaledOR"])
        print("    Sig Efficiency = ", sum(l1unprescaledor["L1UnprescaledOR"])/len(l1unprescaledor["L1UnprescaledOR"]))

        # create and fill CICADA score histograms
        for i in range(len(cicada_names)):
            print("    CICADA VERSION: ", cicada_names[i])

            histModel = ROOT.RDF.TH3DModel(
                f"anomalyScore_{sample_names[k]}_{cicada_names[i]}",
                f"anomalyScore_{sample_names[k]}_{cicada_names[i]}",
                n_bins_cicada,
                min_score_cicada,
                max_score_cicada,
                n_bins_ht,
                min_score_ht,
                max_score_ht,
                n_bins_trig,
                min_score_trig,
                max_score_trig
            )

            hist = rdf.Histo3D(
                histModel,
                f"{cicada_names[i]}_score",
                "HT",
                "L1UnprescaledOR"
            )
            print("        Bin Content Example 1 = ", hist.GetBinContent(10, 2, 2))
            print("        Bin Content Example 2 = ", hist.GetBinContent(5, 1, 1))
            hist.Write()

            histModel = ROOT.RDF.TH1DModel(
                f"jetEt_{sample_names[k]}_{cicada_names[i]}",
                f"jetEt_{sample_names[k]}_{cicada_names[i]}",
                n_bins_pt,
                min_score_pt,
                max_score_pt
            )

            hist = rdf.Filter("leadJetEt >= 0").Histo1D(histModel, "leadJetEt")
            hist.Write()

        output_file.Write()
        output_file.Close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="This program creates 3d histograms with CICADA score, HT, and L1 Unprescaled OR"
    )
    parser.add_argument("-o", "--out_prefix", default = "ROChist", help="output file name/path prefix")
    args = parser.parse_args()

    main(args.out_prefix)

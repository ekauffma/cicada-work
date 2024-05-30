########################################################################
## createHistsForROC.py                                               ##
## Author: Elliott Kauffman                                           ##
## make score and rate histograms for CICADA                          ##
########################################################################

import ROOT
import argparse
import numpy as np
from paperSampleBuilder import samples

def main():

    # get list of sample names and remove ZeroBias
    sample_names = list(samples.keys())
    if 'ZeroBias' in sample_names:
        sample_names.remove('ZeroBias')

    # get zerobias and filter out training events
    zero_bias = samples['ZeroBias'].getNewDataframe()
    zero_bias_test = zero_bias.Filter('lumi % 2 == 1')
    zero_bias_test = zero_bias_test.Define("sum_mask", "(sumBx==0) && (sumType==1)")
    zero_bias_test = zero_bias_test.Define("HT", "sumEt[sum_mask]")
    zero_bias_train = zero_bias.Filter('lumi % 2 == 0')
    zero_bias_train = zero_bias_train.Define("sum_mask", "(sumBx==0) && (sumType==1)")
    zero_bias_train = zero_bias_train.Define("HT", "sumEt[sum_mask]")

    # names of CICADA models
    cicada_names = ["CICADA_v1p2p2"]
                    #"CICADA_v2p2p2",
                    #"CICADA_v1p2p2N",
                    #"CICADA_v2p2p2N"]

    # minimum and maximum scores for histogram
    min_score_cicada = 0.0
    max_score_cicada = 1024.0
    n_bins_cicada = 200
    min_score_ht = 0.0
    max_score_ht = 2000.0
    n_bins_ht = 100


    # create file for zerobias hists
    print("Sample: ZeroBias")
    output_file = ROOT.TFile("hists_240530_ZeroBias.root", "RECREATE")

    # create and fill CICADA score histograms for zerobias
    for i in range(len(cicada_names)):
        print("    CICADA VERSION: ", cicada_names[i])

        histModel = ROOT.RDF.TH2DModel(
            f"anomalyScore_ZeroBias_test_{cicada_names[i]}",
            f"anomalyScore_ZeroBias_test_{cicada_names[i]}",
            n_bins_cicada,
            min_score_cicada,
            max_score_cicada,
            n_bins_ht,
            min_score_ht,
            max_score_ht
        )

        hist = zero_bias_test.Histo2D(histModel, f"{cicada_names[i]}_score", "HT")
        print("        Bin Content Example 1 = ", hist.GetBinContent(10, 2))
        print("        Bin Content Example 2 = ", hist.GetBinContent(5, 1))
        hist.Write()


        histModel = ROOT.RDF.TH2DModel(
            f"anomalyScore_ZeroBias_train_{cicada_names[i]}",
            f"anomalyScore_ZeroBias_train_{cicada_names[i]}",
            n_bins_cicada,
            min_score_cicada,
            max_score_cicada,
            n_bins_ht,
            min_score_ht,
            max_score_ht
        )

        hist = zero_bias_train.Histo2D(histModel, f"{cicada_names[i]}_score", "HT")
        hist.Write()

    output_file.Write()
    output_file.Close()


    # create and write hists for each sample
    for k in range(len(sample_names)):
        print(f"Sample: {sample_names[k]}")
        output_file = ROOT.TFile(f"hists_240530_{sample_names[k]}.root", "RECREATE")

        rdf = samples[sample_names[k]].getNewDataframe()
        rdf = rdf.Define("sum_mask", "(sumBx==0) && (sumType==1)")
        rdf = rdf.Define("HT", "sumEt[sum_mask]")

        # create and fill CICADA score histograms
        for i in range(len(cicada_names)):
            print("    CICADA VERSION: ", cicada_names[i])

            histModel = ROOT.RDF.TH2DModel(
                f"anomalyScore_{sample_names[k]}_{cicada_names[i]}",
                f"anomalyScore_{sample_names[k]}_{cicada_names[i]}",
                n_bins_cicada,
                min_score_cicada,
                max_score_cicada,
                n_bins_ht,
                min_score_ht,
                max_score_ht
            )

            hist = rdf.Histo2D(histModel, f"{cicada_names[i]}_score", "HT")
            print("        Bin Content Example 1 = ", hist.GetBinContent(10, 2))
            print("        Bin Content Example 2 = ", hist.GetBinContent(5, 1))
            hist.Write()

        output_file.Write()
        output_file.Close()


if __name__ == "__main__":

	main()

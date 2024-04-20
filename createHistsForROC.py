########################################################################
## createHistsForROC.py                                               ##
## Author: Elliott Kauffman                                           ##
## make score and rate histograms for CICADA                          ##
########################################################################

import ROOT
import argparse
import numpy as np
from paperSampleBuilder import samples

def main(nBins):

    # get list of sample names and remove ZeroBias
	sample_names = list(samples.keys())
	if 'ZeroBias' in sample_names:
		sample_names.remove('ZeroBias')

    # get zerobias and filter out training events
	zero_bias = samples['ZeroBias'].getNewDataframe()
	zero_bias_test = zero_bias.Filter('lumi % 2 == 1')
    zero_bias_train = zero_bias.Filter('lumi % 2 == 0')

    # names of CICADA models
	cicada_names = ["CICADA_v1p2p2",
                    "CICADA_v2p2p2",
                    "CICADA_v1p2p2N",
                    "CICADA_v2p2p2N"]

    # minimum and maximum scores for histogram
	min_score_cicada = 0.0
	max_score_cicada = 256.0
    min_score_ht = 0.0
    max_score_ht = 1500.0


    # create file for zerobias hists
    print("Sample: ZeroBias")
    output_file = ROOT.TFile("hists_240420_ZeroBias.root", "RECREATE")

    # create and fill CICADA score histograms for zerobias
    for i in range(len(cicada_names)):
        print("    CICADA VERSION: ", cicada_names[i])

        histModel = ROOT.RDF.TH1DModel(
            f"anomalyScore_ZeroBias_test_{cicada_names[i]}",
            f"anomalyScore_ZeroBias_test_{cicada_names[i]}",
            nBins,
            min_score_cicada,
            max_score_cicada
        )
        hist = zero_bias_test.Histo1D(histModel, f"{cicada_names[i]}_score")
        hist.Write()

        histModel = ROOT.RDF.TH1DModel(
            f"anomalyScore_ZeroBias_train_{cicada_names[i]}",
            f"anomalyScore_ZeroBias_train_{cicada_names[i]}",
            nBins,
            min_score_cicada,
            max_score_cicada
        )
        hist = zero_bias_train.Histo1D(histModel, f"{cicada_names[i]}_score")
        hist.Write()

    # create and fill HT histograms for zerobias
    print("    HT")
    zero_bias_test = zero_bias_test.Define("sum_mask", "(sumBx==0) && (sumType==1)")
    zero_bias_test = zero_bias_test.Define("HT", "sumEt[sum_mask]")
    zero_bias_train = zero_bias_train.Define("sum_mask", "(sumBx==0) && (sumType==1)")
    zero_bias_train = zero_bias_train.Define("HT", "sumEt[sum_mask]")

    histModel = ROOT.RDF.TH1DModel(
        f"HT_ZeroBias_test_{cicada_names[i]}",
        f"HT_ZeroBias_test_{cicada_names[i]}",
        nBins,
        min_score_ht,
        max_score_ht
    )
    hist = zero_bias_test.Histo1D(histModel, "HT")
    hist.Write()

    histModel = ROOT.RDF.TH1DModel(
        f"HT_ZeroBias_train_{cicada_names[i]}",
        f"HT_ZeroBias_train_{cicada_names[i]}",
        nBins,
        min_score_ht,
        max_score_ht
    )
    hist = zero_bias_train.Histo1D(histModel, "HT")
    hist.Write()

    output_file.Write()
    output_file.Close()


    # create and write hists for each sample
    for k in range(len(sample_names)):
        print(f"Sample: {sample_names[k]}")
        output_file = ROOT.TFile(f"hists_240420_{sample_names[k]}.root". "RECREATE")






if __name__ == "__main__":

	parser = argparse.ArgumentParser(
        description="This program creates CICADA score plots"
    )
	parser.add_argument(
        "-n",
        "--n_bins",
        default=100,
        help="number of bins")

	args = parser.parse_args()

	main( args.n_bins)

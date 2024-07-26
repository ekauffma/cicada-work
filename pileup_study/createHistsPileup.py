########################################################################
## createHistsPileup.py                                               ##
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
    zero_bias = zero_bias.Filter('lumi % 2 == 1')

    # names of CICADA models
    cicada_names = ["CICADA_v1p2p2",
                    "CICADA_v2p2p2",
                    "CICADA_v1p2p2N",
                    "CICADA_v2p2p2N"]

    # minimum and maximum scores for histogram
    min_score_cicada = 0.0
    max_score_cicada = 1024.0
    min_score_ht = 0.0
    max_score_ht = 1500.0

    # create file for zerobias hists
    output_file = ROOT.TFile("hists_pileup_240626.root", "RECREATE")

    # create and fill CICADA score histograms for zerobias
    for i in range(len(cicada_names)):
        print("CICADA VERSION: ", cicada_names[i])

        histModel = ROOT.RDF.TH1DModel(
            f"anomalyScore_ZeroBias_{cicada_names[i]}",
            f"anomalyScore_ZeroBias_{cicada_names[i]}",
            nBins,
            min_score_cicada,
            max_score_cicada
        )
        hist = zero_bias.Histo1D(histModel, f"{cicada_names[i]}_score")
        hist.Write()

    output_file.Write()
    output_file.Close()

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

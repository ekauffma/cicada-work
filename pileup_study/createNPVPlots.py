########################################################################
## createScorePlots.py                                                ##
## Author: Elliott Kauffman                                           ##
## make score and rate histograms for CICADA                          ##
########################################################################

import ROOT
import argparse
import numpy as np
from npvBuilder import samples

def main(nBins):


    # get zerobias and filter out training events
    zero_bias = samples['ZeroBias'].getNewDataframe()

    # names of CICADA models
	cicada_names = ["CICADA_v1p2p2",
                    "CICADA_v2p2p2",
                    "CICADA_v1p2p2N",
                    "CICADA_v2p2p2N"]

    # minimum and maximum scores for histogram
    min_score = 0.0
    max_score = 1024.0
    min_npv = 0.0
    max_npv = 5.0

    # create one output file per CICADA model/version
    for i in range(len(cicada_names)):
        print("CICADA VERSION: ", cicada_names[i])

        # create ROOT output file
		output_file = ROOT.TFile(f'hists_npv_240626_{cicada_names[i]}.root',
                                 'RECREATE')

		# make histModel for zerobias
		histModel = ROOT.RDF.TH2DModel(
            f"h_{cicada_names[i]}",
            f"h_{cicada_names[i]}",
            nBins,
            min_score,
            max_score,
            int(max_npv - min_npv),
            min_npv,
            max_npv
        )

        # get and write score hist
        hist = zero_bias.Histo2D(histModel, f"{cicada_names[i]}_score", "npv")
		hist.Write()

		output_file.Write()
		output_file.Close()

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

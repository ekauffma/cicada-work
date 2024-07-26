########################################################################
## createScorePlots_compare.py                                        ##
## Author: Elliott Kauffman                                           ##
## Creates histograms of the CICADA scores for student and teacher    ##
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

    # filter training events out of ZeroBias
    zero_bias = samples['ZeroBias'].getNewDataframe()
    zero_bias = zero_bias.Filter('lumi % 2 == 1')

    # names of cicada versions
    cicada_names = [
        #"CICADA_v1p2p0",
        #"CICADA_v2p2p0",
        #"CICADA_v1p2p0N",
        #"CICADA_v2p2p0N",
        #"CICADA_vXp2p0_teacher",
        "CICADA_vXp2p0N_teacher"
    ]

    # min and max scores for histograms
    min_score = 0.0
    max_score = 1024.0

    # create one output file for each cicada version
    for i in range(len(cicada_names)):

        print("CICADA VERSION: ", cicada_names[i])

        # create output ROOT file
        output_file = ROOT.TFile(
            f'hists_compare_240312_{cicada_names[i]}.root',
            'RECREATE'
        )

        # make hists for zerobias
        histModel = ROOT.RDF.TH1DModel(
            f"anomalyScore_ZeroBias_{cicada_names[i]}",
            f"anomalyScore_ZeroBias_{cicada_names[i]}",
             nBins,
            min_score,
            max_score
        )
        if "teacher" in cicada_names[i]:
            zero_bias = zero_bias.Redefine(f"{cicada_names[i]}_score", f"32*log({cicada_names[i]}_score)")
        hist = zero_bias.Histo1D(histModel, f"{cicada_names[i]}_score")
        hist.Write()

        # iterate through each sample
        for k in range(len(sample_names)):
            print("    Current Sample: ", sample_names[k])

            # make score plot
            histModel = ROOT.RDF.TH1DModel(
                f"anomalyScore_{sample_names[k]}_{cicada_names[i]}",
                f"anomalyScore_{sample_names[k]}_{cicada_names[i]}",
                nBins,
                min_score,
                max_score)
            rdf = samples[sample_names[k]].getNewDataframe()

            if "teacher" in cicada_names[i]:
                print("    Calculating teacher score")
                rdf = rdf.Redefine(f"{cicada_names[i]}_score", f"32*log({cicada_names[i]}_score)")

            hist = rdf.Histo1D(histModel, f"{cicada_names[i]}_score")
            hist.Write()


        # write and close file
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
        help="number of bins"
    )

	args = parser.parse_args()

	main( args.n_bins)

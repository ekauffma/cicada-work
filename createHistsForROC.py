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

    # create one output file per CICADA model/version
	for i in range(len(cicada_names)):
        print("CICADA VERSION: ", cicada_names[i])

        # create ROOT output file
		output_file = ROOT.TFile(f'hists_240420_{cicada_names[i]}.root',
                                 'RECREATE')

		# make histModel for zerobias
		histModel = ROOT.RDF.TH1DModel(
            f"anomalyScore_ZeroBias_{cicada_names[i]}",
            f"anomalyScore_ZeroBias_{cicada_names[i]}",
            nBins,
            min_score_cicada,
            max_score_cicada)

        # get and write score hist
        zero_bias_test = zero_bias_test.Define("sum_mask", "(sumBx==0) && (sumType==1)")
        zero_bias_test = zero_bias_test.Define("HT", "sumEt[sum_mask]")
        zero_bias_train = zero_bias_train.Define("sum_mask", "(sumBx==0) && (sumType==1)")
        zero_bias_train = zero_bias_train.Define("HT", "sumEt[sum_mask]")

        hist = zero_bias_test.Histo1D(histModel, f"{cicada_names[i]}_score")
		hist.Write()
        hist = zero_bias_train.Histo1D(histModel, f"{cicada_names[i]}_score")
        hist.Write()

        # make histModel for zerobias HT
        histModel = ROOT.RDF.TH1DModel(
            f"HT_ZeroBias_{cicada_names[i]}",
            f"HT_ZeroBias_{cicada_names[i]}",
            nBins,
            min_score_ht,
            max_score_ht
        )

        # get and write ht hist
        hist = zero_bias_test.Histo1D(histModel, "HT")
        hist.Write()
        hist = zero_bias_train.Histo1D(histModel, "HT")
        hist.Write()

        # create and write hists for each sample
		for k in range(len(sample_names)):
            print("    Current Sample: ", sample_names[k])

            rdf = samples[sample_names[k]].getNewDataframe()
            rdf = rdf.Define("sum_mask", "(sumBx==0) && (sumType==1)")
            rdf = rdf.Define("HT", "sumEt[sum_mask]")

			# make score hist
			histModel = ROOT.RDF.TH1DModel(
                f"anomalyScore_{sample_names[k]}_{cicada_names[i]}",
                f"anomalyScore_{sample_names[k]}_{cicada_names[i]}",
				nBins,
                min_score_cicada,
                max_score_cicada
            )
            hist = rdf.Histo1D(histModel, f"cicada_names[i]_score")
			hist.Write()

            # make ht hist
            histModel = ROOT.RDF.TH1DModel(
                f"HT_{sample_names[k]}_{cicada_names[i]}",
                f"HT_{sample_names[k]}_{cicada_names[i]}",
                nBins,
                min_score_ht,
                max_score_ht
            )
            hist = rdf.Histo1D(histModel, "HT")
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

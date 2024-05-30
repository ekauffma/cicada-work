########################################################################
## createHTHistograms.py                                              ##
## Author: Elliott Kauffman                                           ##
## Creates histograms of the HT and recomputed HT                     ##
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

    # min and max scores for histograms
    min_score = 0.0
    max_score = 3000.0


    # create output ROOT file
    output_file = ROOT.TFile(
        f'hists_HT_240402.root',
        'RECREATE'
    )

    # make hists for zerobias
    histModel = ROOT.RDF.TH1DModel(
        "HT_ZeroBias",
        "HT_ZeroBias",
        nBins,
        min_score,
        max_score
    )
    zero_bias = zero_bias.Define("jet_mask", "(jetEt > 30) && (jetEta < 2.4) && (jetEta > -2.4) && (jetBx == 0)")
    zero_bias = zero_bias.Define("HT", "double ht = 0.0; for (auto&& x : jetEt[jet_mask]) ht += x; return ht;")
    hist = zero_bias.Histo1D(histModel, "HT")
    hist.Write()

    histModel = ROOT.RDF.TH1DModel(
        "HT_rec_ZeroBias",
        "HT_rec_ZeroBias",
        nBins,
        min_score,
        max_score
    )
    zero_bias = zero_bias.Define("sum_mask", "(sumBx==0) && (sumType==1)")
    zero_bias = zero_bias.Define("HT_rec", "sumEt[sum_mask]")
    hist = zero_bias.Histo1D(histModel, "HT_rec")
    hist.Write()

    # iterate through each sample
    for k in range(len(sample_names)):
        print("    Current Sample: ", sample_names[k])

        # make score plot
        histModel = ROOT.RDF.TH1DModel(
            f"HT_{sample_names[k]}",
            f"HT_{sample_names[k]}",
            nBins,
            min_score,
            max_score)
        rdf = samples[sample_names[k]].getNewDataframe()

        rdf = rdf.Define("jet_mask", "(jetEt > 30) && (jetEta < 2.4) && (jetEta > -2.4) && (jetBx == 0)")
        rdf = rdf.Define("HT", "double ht = 0.0; for (auto&& x : jetEt[jet_mask]) ht += x; return ht;")

        hist = rdf.Histo1D(histModel, f"HT")
        hist.Write()

        histModel = ROOT.RDF.TH1DModel(
            f"HT_rec_{sample_names[k]}",
            f"HT_rec_{sample_names[k]}",
            nBins,
            min_score,
            max_score
        )
        rdf = rdf.Define("sum_mask", "(sumBx==0) && (sumType==1)")
        rdf = rdf.Define("HT_rec", "sumEt[sum_mask]")
        hist = rdf.Histo1D(histModel, "HT_rec")
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
        default=200,
        help="number of bins"
    )

	args = parser.parse_args()

	main( args.n_bins)

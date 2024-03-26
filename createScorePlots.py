########################################################################
## createScorePlots.py                                                ##
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
	cicada_names = ["CICADA_v1p2p0",
                    "CICADA_v2p2p0",
                    "CICADA_v1p2p0N",
                    "CICADA_v2p2p0N"]

    # minimum and maximum scores for histogram
	min_score = 0.0
	max_score = 1024.0

    # create one output file per CICADA model/version
	for i in range(len(cicada_names)):
        print("CICADA VERSION: ", cicada_names[i])

        # create ROOT output file
		output_file = ROOT.TFile(f'hists_240220_{cicada_names[i]}.root',
                                 'RECREATE')

		# make histModel for zerobias
		histModel = ROOT.RDF.TH1DModel(
            f"anomalyScore_ZeroBias_{cicada_names[i]}",
            f"anomalyScore_ZeroBias_{cicada_names[i]}",
            nBins,
            min_score,
            max_score)

        # get and write score hist
        hist = zero_bias.Histo1D(histModel, f"{cicada_names[i]}_score")
		hist.Write()

        # create efficiency hist
		eff = ROOT.TH1D(
            f"efficiency_ZeroBias_{cicada_names[i]}",
            f"efficiency_ZeroBias_{cicada_names[i]}",
            hist.GetNbinsX(),
            hist.GetXaxis().GetXmin(),
            hist.GetXaxis().GetXmax()
        )

        # get total number of events in score plot
		scoreplot_int = float(hist.Integral())

        # iterate through bins and compute partial sum of events
		for j in range(1, hist.GetNbinsX()+1):

            # calculate partial sum
			scoreplot_int_current = float(hist.Integral(j, hist.GetNbinsX()))
			# calculate uncertainty as sqrt(N)
            uncertainty = np.sqrt(scoreplot_int_current)
            # scale sum and uncertainty by total integral
			scoreplot_int_current = scoreplot_int_current/scoreplot_int
			uncertainty = uncertainty/scoreplot_int

            # set bin content and error of histogram
			eff.SetBinContent(j,scoreplot_int_current)
			eff.SetBinError(j, uncertainty)

        # clone efficiency hist to create rate hist
		rate = eff.Clone(f"rate_ZeroBias_{cicada_names[i]}")
		rate.Scale(2544.0 * 11245e-3) # convert efficiency to rate
		rate.Write()

        # create and write hists for each sample
		for k in range(len(sample_names)):
            print("    Current Sample: ", sample_names[k])

			# make score plot
			histModel = ROOT.RDF.TH1DModel(f"anomalyScore_{sample_names[k]}_{cicada_names[i]}", f"anomalyScore_{sample_names[k]}_{cicada_names[i]}",
							nBins, min_score, max_score)
			rdf = samples[sample_names[k]].getNewDataframe()
			hist = rdf.Histo1D(histModel, f"{cicada_names[i]}_score")
			hist.Write()

			# make efficiency plot
			eff = ROOT.TH1D(
                f"efficiency_{sample_names[k]}_{cicada_names[i]}",
				f"efficiency_{sample_names[k]}_{cicada_names[i]}",
				hist.GetNbinsX(),
				hist.GetXaxis().GetXmin(),
				hist.GetXaxis().GetXmax()
            )

			# total integral
			scoreplot_int = float(hist.Integral())

			# compute value for each threshold
			for j in range(1, hist.GetNbinsX()+1):
				scoreplot_int_current = float(hist.Integral(j, hist.GetNbinsX()))
				uncertainty = np.sqrt(scoreplot_int_current)
				scoreplot_int_current = scoreplot_int_current/scoreplot_int
				uncertainty = uncertainty/scoreplot_int

				eff.SetBinContent(j,scoreplot_int_current)
				eff.SetBinError(j, uncertainty)

			eff.Write()

			# make rate plot
			rate = eff.Clone(f"rate_{sample_names[k]}_{cicada_names[i]}")
			rate.Scale(2544.0 * 11245e-3) # convert efficiency to rate
			rate.Write()

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

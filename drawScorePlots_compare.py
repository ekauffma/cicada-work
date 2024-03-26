/*--------------------------------------------------------------------*/
/* drawScorePlots_compare.py                                          */
/* Author: Elliott Kauffman                                           */
/* Takes output histograms from createScorePlots_compare.py and makes */
/* plots comparing the score distribution for CICADA versions pre and */
/* post-noise suppression                                             */
/*--------------------------------------------------------------------*/


import ROOT
import argparse
import numpy as np
from array import array
from paperSampleBuilder import samples
from sampleNames import sample_name_dict

# function for drawing the CMS label on the plot
def createCMSLabel():
	cmsLatex = ROOT.TLatex()
	cmsLatex.SetTextSize(0.04)
	cmsLatex.SetNDC(True)
	cmsLatex.SetTextAlign(11)

	return cmsLatex


def main(input_file1, input_file2, N,  output_dir, cicada_name):

    # N determines whether the CICADA version is CICADA_v*p*p* or
    # CICADA_v*p*p*N
	N_str = ""
	if N: N_str = "N"

    # list containing input files
	f = [ROOT.TFile(input_file1), ROOT.TFile(input_file2)]

    # grab the sample names and remove ZeroBias and SingleNeutrino
	sample_names = list(samples.keys())
	if 'ZeroBias' in sample_names:
		sample_names.remove('ZeroBias')
	if 'SingleNeutrino_E-10-gun' in sample_names:
		sample_names.remove('SingleNeutrino_E-10-gun')

    # labels for the y axes of the plots
	ylabels = ["Frequency (Standard)",
               "Frequency (Noise-Suppressed)"]
    sample_color = [6,9] # colors for the sample plots
	sample_style = [22,26] # marker style for the sample plots
	legends = [] # empty list to hold legends for each plot
	legend_tops = [0.9,1.0] # placement of the top of the legend

    # iterate through all samples
	for i in range(len(sample_names)):

        # ROOT canvas for CICADA score
		c1 = ROOT.TCanvas("c1", "Anomaly Score", 1000, 1000)

        # define ROOT pads (necessary for having multiple plots
        # on same canvas)
		pads = [ROOT.TPad("pad1", "pad1", 0.0, 0.6, 1.0, 1.0),
                ROOT.TPad("pad2", "pad2", 0, 0.2, 1.0, 0.6)]
		pads[0].SetBottomMargin(0)
		pads[1].SetBottomMargin(0)
		pads[1].SetTopMargin(0)
		for pad in pads:
			pad.Draw()

        # set up bottom pad for ratio plot
		pad_ratio = ROOT.TPad("pad_ratio", "pad_ratio", 0, 0, 1.0, 0.2)
		pad_ratio.SetBottomMargin(0.2)
		pad_ratio.SetTopMargin(0)
		pad_ratio.Draw()

        # create the top two plots
		for j in [0,1]:

            # change directory into current pad
			pads[j].cd()

			# get histograms
			hist_zb = f[j].Get(
                f"anomalyScore_ZeroBias_{cicada_name}p{j}{N_str}"
            )
			hist_sng = f[j].Get(
                f"anomalyScore_SingleNeutrino_E-10-gun_{cicada_name}p{j}{N_str}"
            )
			hist_sample = f[j].Get(
                f"anomalyScore_{sample_names[i]}_{cicada_name}p{j}{N_str}"
            )

			# styling
			hist_zb.SetMarkerColor(1)
			hist_zb.SetLineColor(1)
			hist_zb.SetMarkerStyle(20)

			hist_sng.SetMarkerColor(8)
			hist_sng.SetLineColor(8)
			hist_sng.SetMarkerStyle(21)

			hist_sample.SetMarkerColor(sample_color[j])
			hist_sample.SetLineColor(sample_color[j])
			hist_sample.SetMarkerStyle(sample_style[j])

			# ZERO BIAS HISTOGRAM
			hist_zb.Scale(1/hist_zb.Integral())  # normalize
			hist_zb.GetYaxis().SetRangeUser(1e-7,1e1)  # set y axis range
			hist_zb.GetXaxis().SetRangeUser(0,256)  # set x axis range
			hist_zb.SetStats(0)  # remove statistics box from plot
			hist_zb.SetTitle("")  # remove title from plot
			hist_zb.GetYaxis().SetTitle(ylabels[j])  # set y axis label
			hist_zb.Draw("e")  # draw histogram

			hist_sng.Scale(1/hist_sng.Integral())  # normalize
			hist_sng.SetStats(0)  # remove statistics box from plot
			hist_sng.SetTitle("")  # remove title from plot )
			hist_sng.Draw("e same")  # draw histogram

			hist_sample.Scale(1/hist_sample.Integral())
			hist_sample.SetStats(0)  # remove statistics box from plot )
			hist_sample.SetTitle("")  # remove title from plot
			hist_sample.Draw("e same")  # draw histogram

			# create CMS label (only on top pad)
			if j==0:
				cmsLatex = createCMSLabel()
				cmsLatex.DrawLatex(0.1,
                                   0.92,
                                   "#font[61]{CMS} #font[52]{Preliminary}")

			# create and draw legend
			legends.append(
                ROOT.TLegend(0.4,
                            legend_tops[j]-0.2,
                             1.0,
                             legend_tops[j])
            )
			legends[-1].AddEntry(hist_zb,
                                 "Zero Bias",
                                 "PE")
			legends[-1].AddEntry(hist_sng,
                                 "Single Neutrino Gun",
                                 "PE")
			legends[-1].AddEntry(hist_sample,
                                 sample_name_dict[sample_names[i]],
                                 "PE")
			legends[-1].SetTextSize(0.04)
			legends[-1].SetBorderSize(0)
			legends[-1].SetFillStyle(0)
			legends[-1].Draw()

			pads[j].SetLogy() # make y axis of pad log-scale
			c1.cd() # change directory back to canvas

		# need separate loop for ratio plots
        # change directory into ratio plot pad
		pad_ratio.cd()
		pad_ratio.SetLogy()  # set log scale for ratio

        # create ratio plot
		legend_ratio = ROOT.TLegend(0.15,0.75,0.4,0.95)
		legend_ratio.SetTextSize(0.07)
		legend_ratio.SetBorderSize(0)
		legend_ratio.SetFillStyle(0)

        # create stack to add histograms to
		hs = ROOT.THStack("hs","hs")
		for j in [0,1]:
			hist_zb = f[j].Get(
                f"anomalyScore_ZeroBias_{cicada_name}p{j}{N_str}"
            )
			hist_sample = f[j].Get(
                f"anomalyScore_{sample_names[i]}_{cicada_name}p{j}{N_str}"
            )

			# calculate ratio hist and add to stack
			ratio_hist = hist_sample.Clone("ratio_hist")
			ratio_hist.Sumw2()  # handle error bars properly
			ratio_hist.Divide(hist_zb)  # divide by zero bias
			ratio_hist.SetMarkerColor(sample_color[j])
			ratio_hist.SetLineColor(sample_color[j])
			ratio_hist.SetMarkerStyle(sample_style[j])
			hs.Add(ratio_hist)
			legend_ratio.AddEntry(ratio_hist, f"{cicada_name}p{j}{N_str}")


		# create horizontal line at 1
		xvals = array('d')
		yvals = array('d')
		n = 300
		for j in range(n):
			xvals.append(j)
			yvals.append(1)
		g = ROOT.TGraph(n, xvals, yvals)
		g.SetLineColor(1)  # make line black
		g.GetXaxis().SetRangeUser(0,256)  # set x axis range of plot
		g.GetYaxis().SetRangeUser(1e-3,1e5)  # set y axis range (log scale)
		g.SetTitle("")  # make title invisible
		g.GetXaxis().SetTitle("CICADA Score")  # set x axis title
		g.GetYaxis().SetTitle("Ratio to Zero Bias")  # set y axis title
        # spacing and text size options
		g.GetXaxis().SetLabelSize(0.07)
		g.GetYaxis().SetLabelSize(0.07)
		g.GetXaxis().SetTitleSize(0.07)
		g.GetYaxis().SetTitleSize(0.07)
		g.GetYaxis().SetTitleOffset(0.6)
		g.Draw("AC")

		# draw ratios
		hs.Draw("e nostack same")
		legend_ratio.Draw()
		c1.cd()

        # draw canvas and save png
		c1.Draw()
		c1.SaveAs(
            f"{output_dir}/scorehist_{sample_names[i]}_{cicada_name}.png"
        )
		c1.Close()


if __name__ == "__main__":

	parser = argparse.ArgumentParser(
        description="This program creates CICADA score plots"
    )
	parser.add_argument(
        "-i1",
        "--input_file1",
        help="path to input ROOT file containing hists (standard)"
    )
	parser.add_argument(
        "-i2",
        "--input_file2",
        help="path to input ROOT file containing hists (noise-suppressed)"
    )
	parser.add_argument(
        "-n",
        "--n",
        default=False,
        help="whether cicada name has N at the end"
    )
	parser.add_argument(
        "-o",
        "--output_dir",
        default='./',
        help="directory to save output plots"
    )
	parser.add_argument(
        "-c",
        "--cicada_name",
        help="name of CICADA model, omitting p0(1)(N)"
    )

	args = parser.parse_args()

	main(args.input_file1,
         args.input_file2,
         args.n,
         args.output_dir,
         args.cicada_name)

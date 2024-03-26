########################################################################
## drawScorePlots_shortlist.py                                        ##
## Author: Elliott Kauffman                                           ##
## takes output histograms from createScorePlots.py and creates score ##
## and rate plots for the shortlist of samples for the paper          ##
########################################################################

import ROOT
import argparse
import numpy as np
from array import array
from sampleNames import sample_name_dict

# list of samples for the shortlist
sample_list = [
    "GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8",
    "GluGluHToGG_M-125_TuneCP5_13p6TeV_powheg-pythia8",
    "HHHTo6B_c3_0_d4_0_TuneCP5_13p6TeV_amcatnlo-pythia8",
    "HTo2LongLivedTo4b_MH-350_MFF-80_CTau-1000mm_TuneCP5_13p6TeV-pythia8",
    "SUEP",
    "SUSYGluGluToBBHToBB_NarrowWidth_M-350_TuneCP5_13p6TeV-pythia8",
    "ttHto2C_M-125_TuneCP5_13p6TeV_powheg-pythia8",
    "VBFHToInvisible_M-125_TuneCP5_13p6TeV_powheg-pythia8",
    "TT_TuneCP5_13p6TeV_powheg-pythia8"
]

# plot colors (for each sample)
sample_colors = [2, 95, 105, 3, 209, 4, 65, 51, 6]

# function for drawing the CMS label on the plots
def createCMSLabel():
	cmsLatex = ROOT.TLatex()
	cmsLatex.SetTextSize(0.04)
	cmsLatex.SetNDC(True)
	cmsLatex.SetTextAlign(11)

	return cmsLatex


def main(input_file, output_dir, cicada_name):

	f = ROOT.TFile(input_file)

    # create ROOT canvas
	c1 = ROOT.TCanvas("c1", "Anomaly Score", 1000,800)

    # create main pad for score histogram
	pad1 = ROOT.TPad("pad1", "pad1", 0, 0.4, 0.75, 1.0)
	pad1.SetBottomMargin(0)
	pad1.Draw()

    # create pad for ratio plot (directly under main plot)
	pad3 = ROOT.TPad("pad3", "pad3", 0, 0.05, 0.75, 0.4)
	pad3.SetTopMargin(0)
	pad3.SetBottomMargin(0.2)
	pad3.Draw()

    # change directory into main pad
	pad1.cd()

    # get zerobias histogram
	hist_zerobias = f.Get(f"anomalyScore_ZeroBias_{cicada_name}")

    # change histogram style options and draw
	hist_zerobias.GetYaxis().SetRangeUser(5e-1,1e7)
	hist_zerobias.GetXaxis().SetRangeUser(0,256)
	hist_zerobias.SetMarkerColor(1)
	hist_zerobias.SetMarkerStyle(20)
	hist_zerobias.SetStats(0)
	hist_zerobias.SetTitle("")
	hist_zerobias.GetYaxis().SetTitle("Counts")
	hist_zerobias.Draw("e")

    # create legend object and add ZeroBias
	legend = ROOT.TLegend(-0.08,0.2,1.0,0.95)
	legend.AddEntry(hist_zerobias, "ZeroBias", "PE")

    # iterate through samples in shortlist
	for i in range(len(sample_names)):

        # get sample histogram
		hist_sample = f.Get(
            f"anomalyScore_{sample_list[i]}_{cicada_name}"
        )

        # change histogram style options and draw on same canvas
		hist_sample.SetMarkerColor(sample_colors[i])
		hist_sample.SetMarkerStyle(20)
		hist_sample.SetLineColor(sample_colors[i])
		hist_sample.SetStats(0)
		hist_sample.SetTitle("")
		hist_sample.Draw("e same")

        # add legend entry for current sample
		legend.AddEntry(hist_sample, f"{sample_names[i]}", "PE")

    # draw cms label
	cmsLatex = createCMSLabel()
	cmsLatex.DrawLatex(0.1,
                       0.92,
                       "#font[61]{CMS} #font[52]{Preliminary}")

    # set log scale on the same axis
	pad1.SetLogy()

    # change to ratio pad
	c1.cd()
	pad3.cd()

    # draw horizontal line at 1 on ratio plot
	xvals = array('d')
	yvals = array('d')
	n = 300
	for i in range(n):
		xvals.append(i)
		yvals.append(1)
	g = ROOT.TGraph(n, xvals, yvals)
	g.SetLineColor(1)

    # set axis and title options for ratio plot
	g.GetXaxis().SetRangeUser(0,256)
	g.GetXaxis().SetLabelSize(0.06)
	g.GetYaxis().SetRangeUser(1e-4,5e6)
	g.GetYaxis().SetLabelSize(0.06)
	g.SetTitle("")
	g.GetXaxis().SetTitle("CICADA Score Threshold")
	g.GetYaxis().SetTitle("Ratio to Zero Bias")
	g.GetXaxis().SetTitleSize(0.06)
	g.GetYaxis().SetTitleSize(0.06)
	g.GetYaxis().SetTitleOffset(0.7)
	g.Draw("AC")

    # create stack to store histograms for each sample
	hs = ROOT.THStack("hs","hs")

    # iterate again through samples in shortlist
	for i in range(len(sample_names)):

		# get sample score hist
        hist_sample = f.Get(
            f"anomalyScore_{sample_list[i]}_{cicada_name}"
        )
		ratio_hist = hist_sample.Clone("ratio_hist")
		ratio_hist.Sumw2() # needed to calculate error bars
		hist_zerobias.Sumw2()
        ratio_hist.Divide(hist_zerobias) # divide by zero bias
		ratio_hist.SetMarkerStyle(20)
		ratio_hist.SetMarkerColor(sample_colors[i])
		ratio_hist.SetLineColor(sample_colors[i])

        # add to stack
		hs.Add(ratio_hist)

    # draw all histograms in the stack
	hs.Draw("e nostack same")
	pad3.SetLogy()

    # change directory to legend pad
	c1.cd()
	pad2 = ROOT.TPad("pad2", "pad2", 0.68, 0, 1.0, 1.0)
	pad2.Draw()
	pad2.cd()

    # set legend styling and draw
	legend.SetTextSize(0.04)
	legend.SetBorderSize(0)
	legend.SetFillStyle(0)
	legend.Draw()

    # draw, save, and close canvas
	c1.Draw()
	c1.SaveAs(
        f"{output_dir}/scorehist_{sample_list[i]}_{cicada_name}.png"
    )
	c1.Close()

    # TODO: scale sample rate plots and add to this one
    # create canvas for rate plot
	c2 = ROOT.TCanvas("c2","Rate",1000,800)

    # get zerobias rate hist
	hist_zerobias = f.Get(f"rate_ZeroBias_{cicada_name}")

	hist_zerobias.GetYaxis().SetRangeUser(5e-3,1e5)
	hist_zerobias.GetXaxis().SetRangeUser(0,256)
	hist_zerobias.SetMarkerColor(1)
	hist_zerobias.SetMarkerStyle(20)
	hist_zerobias.SetStats(0)
	hist_zerobias.SetTitle("")
	hist_zerobias.GetYaxis().SetTitle("Overall Rate [kHz]")
	hist_zerobias.Draw("e")

    # draw cms label
	cmsLatex = createCMSLabel()
	cmsLatex.DrawLatex(0.1,0.92, "#font[61]{CMS} #font[52]{Preliminary}")

    # set log scale for this canvas
	c2.SetLogy()

    # draw, save, and close
	c2.Draw()
	c2.SaveAs(
        f"{output_dir}/rate_{sample_name_dict[sample_list[i]]}_{cicada_name}.png"
    )
	c2.Close()

if __name__ == "__main__":

	parser = argparse.ArgumentParser(
        description="This program creates CICADA score plots"
    )
	parser.add_argument(
        "-i",
        "--input_file",
        help="path to input ROOT file containing hists"
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
        help="name of CICADA model"
    )

	args = parser.parse_args()

	main(args.input_file, args.output_dir, args.cicada_name)

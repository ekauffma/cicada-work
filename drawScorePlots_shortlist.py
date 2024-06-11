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
import json
from plottingUtils import convertCICADANametoPrint, createLabel

with open('plottingOptions.json') as f:
    options = json.load(f)
    
def drawScorePlot(hist_bkg, sample_shortlist, cicada_name, file_prefix):

    print("Creating shortlist score plot for ", cicada_name)

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
    
    # change histogram style options and draw
    hist_bkg.GetYaxis().SetRangeUser(5e-1,1e7)
    hist_bkg.GetXaxis().SetRangeUser(0,256)
    hist_bkg.SetMarkerColor(1)
    hist_bkg.SetMarkerStyle(20)
    hist_bkg.SetStats(0)
    hist_bkg.SetTitle("")
    hist_bkg.GetYaxis().SetTitle("Frequency")
    hist_bkg.Draw("e")

    # create legend object and add ZeroBias
    legend = ROOT.TLegend(-0.08,0.2,1.0,0.95)
    legend.AddEntry(hist_bkg, "Zero Bias", "PE")
    
    # iterate through samples in shortlist
    for i in range(len(sample_shortlist)):

        f = ROOT.TFile(f"{file_prefix}_{sample_shortlist[i]}.root")

        # get sample histogram
        hist_sample = f.Get(
            f"anomalyScore_{sample_shortlist[i]}_{cicada_name}"
        )
        
        hist_sig = hist_sample.ProjectionX()

        # change histogram style options and draw on same canvas
        hist_sig.SetMarkerColor(options["shortlist_colors"][i])
        hist_sig.SetMarkerStyle(options["shortlist_markers"][i])
        hist_sig.SetLineColor(options["shortlist_colors"][i])
        hist_sig.SetStats(0)
        hist_sig.SetTitle("")
        hist_sig.Draw("e same")

        # add legend entry for current sample
        legend.AddEntry(hist_sig,
                        f"{sample_name_dict[sample_shortlist[i]]}",
                        "PE")

        f.Close()
        
    # draw cms label
    cmsLatex = createLabel()
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
    g.GetYaxis().SetRangeUser(1e-6,5e6)
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
    for i in range(len(sample_list)):

        # get sample score hist
        hist_sample = f.Get(
            f"anomalyScore_{sample_shortlist[i]}_{cicada_name}"
        )
        ratio_hist = hist_sample.Clone("ratio_hist")
        ratio_hist.Sumw2() # needed to calculate error bars
        hist_zerobias.Sumw2()
        ratio_hist.Divide(hist_zerobias) # divide by zero bias
        ratio_hist.SetMarkerStyle(marker_styles[i])
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
    legend.SetTextSize(0.035)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.Draw()

    # draw, save, and close canvas
    c1.Draw()
    c1.SaveAs(
        f"{output_dir}/scorehist_{sample_shortlist[i]}_{cicada_name}.png"
    )
    c1.Close()
    
    return


def main(file_prefix, output_dir):

    f_zb = ROOT.TFile(f"{file_prefix}_ZeroBias.root")
    
    for i in range(len(options["cicada_names"])):
    
        c_name = options["cicada_names"][i]

        # get zerobias histogram
        hist_zerobias = f_zb.Get(f"anomalyScore_ZeroBias_test_{c_name}")
        
        drawScorePlot(hist_zerobias, options["sample_shortlist"], c_name, file_prefix)

    


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

	args = parser.parse_args()

	main(args.input_file, args.output_dir)

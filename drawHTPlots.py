########################################################################
## drawHTPlots.py                                                     ##
## Author: Elliott Kauffman                                           ##
## Takes output histograms from createHTHistograms.py and makes plots ##
########################################################################


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


def main(input_file, output_dir):

    # input files
    f = ROOT.TFile(input_file)

    # grab the sample names
    sample_names = list(samples.keys())

     # iterate through all samples
    for i in range(len(sample_names)):


        if sample_names[i]!="ZeroBias":
            continue
        else: print(sample_names[i])

         # ROOT canvas for CICADA score
        c1 = ROOT.TCanvas("c1", "HT", 1000, 700)

        # define ROOT pads (necessary for having multiple plots
        # on same canvas)
        pad_main = ROOT.TPad("pad_main", "pad_main", 0.0, 0.3, 1.0, 1.0)
        pad_main.SetBottomMargin(0)
        pad_main.Draw()

        # set up bottom pad for residual plot
        pad_ratio = ROOT.TPad("pad_ratio", "pad_ratio", 0, 0, 1.0, 0.3)
        pad_ratio.SetBottomMargin(0.2)
        pad_ratio.SetTopMargin(0)
        pad_ratio.Draw()

        # change directory into main pad
        pad_main.cd()

        # get histograms from ROOT files
        hist_ht = f.Get(
            f"HT_{sample_names[i]}"
        )
        hist_ht_rec = f.Get(
            f"HT_rec_{sample_names[i]}"
        )

		# styling
        hist_ht.SetMarkerColor(6)
        hist_ht.SetLineColor(6)
        hist_ht.SetMarkerStyle(20)

        hist_ht_rec.SetMarkerColor(9)
        hist_ht_rec.SetLineColor(9)
        hist_ht_rec.SetMarkerStyle(21)


		# histogram 1
        #hist_ht.Scale(1/hist_ht.Integral())  # normalize
        hist_ht.GetYaxis().SetRangeUser(5e-1,1e7)  # set y axis range
        hist_ht.GetXaxis().SetRangeUser(0,500)  # set x axis range
        hist_ht.SetStats(0)  # remove statistics box from plot
        hist_ht.SetTitle("")  # remove title from plot
        hist_ht.GetYaxis().SetTitle("Events")  # set y axis label
        hist_ht.Draw("e")  # draw histogram

        # histogram 2
        #hist_ht_rec.Scale(1/hist_ht_rec.Integral())  # normalize
        hist_ht_rec.SetStats(0)  # remove statistics box from plot
        hist_ht_rec.SetTitle("")  # remove title from plot )
        hist_ht_rec.Draw("e same")  # draw histogram

		# create CMS label
        cmsLatex = createCMSLabel()
        cmsLatex.DrawLatex(0.1,
                           0.92,
                           "#font[61]{CMS} #font[52]{Preliminary}")

		# create and draw legend
        legend = ROOT.TLegend(0.6, 0.7, 1.0, 0.9)
        legend.AddEntry(hist_ht, "HT ", "PE")
        legend.AddEntry(hist_ht_rec, "Reconstructed HT", "PE")
        legend.SetTextSize(0.04)
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.Draw()

        pad_main.SetLogy() # make y axis of pad log-scale
        c1.cd() # change directory back to canvas

        # change directory into ratio plot pad
        pad_ratio.cd()
        pad_ratio.SetLogy()

        # create stack to add histograms to
        hs = ROOT.THStack("hs","hs")

		# calculate ratio hists and add to stack
        ratio_hist = hist_ht.Clone("ratio")
        ratio_hist.Sumw2()  # handle error bars properly
        ratio_hist.Divide(hist_ht_rec)  # subtract teacher score
        ratio_hist.SetMarkerColor(2)
        ratio_hist.SetLineColor(2)
        ratio_hist.SetMarkerStyle(22)
        hs.Add(ratio_hist)


		# create horizontal line at 0
        xvals = array('d')
        yvals = array('d')
        n = 300
        for j in range(n):
            xvals.append(j)
            yvals.append(1)
        g = ROOT.TGraph(n, xvals, yvals)
        g.SetLineColor(1)  # make line black
        g.GetXaxis().SetRangeUser(0,500)  # set x axis range of plot
        g.GetYaxis().SetRangeUser(5e-1,5e1)  # set y axis range
        g.SetTitle("")  # make title invisible
        g.GetXaxis().SetTitle("HT (jetEt>30, |jetEta|<2.4)")  # set x axis title
        g.GetYaxis().SetTitle("HT / Reconstructed HT")  # set y axis title
        # spacing and text size options
        g.GetXaxis().SetLabelSize(0.07)
        g.GetYaxis().SetLabelSize(0.07)
        g.GetXaxis().SetTitleSize(0.07)
        g.GetYaxis().SetTitleSize(0.07)
        g.GetYaxis().SetTitleOffset(0.6)
        g.Draw("AC")

		# draw ratios
        hs.Draw("e nostack same")
        c1.cd()

        # draw canvas and save png
        c1.Draw()
        c1.SaveAs(
            f"{output_dir}/HThist_{sample_names[i]}.png"
        )
        c1.Close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This program draws HT histograms")
    parser.add_argument("-f", "--input_file", help="path to input ROOT file containing hists")
    parser.add_argument( "-o", "--output_dir", default='./', help="directory to save output plots")

    args = parser.parse_args()

    main(args.input_file,
         args.output_dir)

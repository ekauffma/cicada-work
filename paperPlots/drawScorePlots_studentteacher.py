########################################################################
## drawScorePlots_studentteacher.py                                   ##
## Author: Elliott Kauffman                                           ##
## Takes output histograms from createScorePlots_studentteacher.py    ##
## and makes plots comparing the student output to the teacher output ##
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


def main(input_v1, input_v2, input_teacher, N,  output_dir):

    # N determines whether the CICADA version is CICADA_v*p*p* or
    # CICADA_v*p*p*N
    N_str = ""
    if N: N_str = "N"

    # input files
    f_v1 = ROOT.TFile(input_v1)
    f_v2 = ROOT.TFile(input_v2)
    f_teacher = ROOT.TFile(input_teacher)

    # grab the sample names
    sample_names = list(samples.keys())

     # iterate through all samples
    for i in range(len(sample_names)):

         # ROOT canvas for CICADA score
        c1 = ROOT.TCanvas("c1", "Anomaly Score", 1000, 700)

        # define ROOT pads (necessary for having multiple plots
        # on same canvas)
        pad_main = ROOT.TPad("pad_main", "pad_main", 0.0, 0.3, 1.0, 1.0)
        pad_main.SetBottomMargin(0)
        pad_main.Draw()

        # set up bottom pad for residual plot
        pad_res = ROOT.TPad("pad_res", "pad_res", 0, 0, 1.0, 0.3)
        pad_res.SetBottomMargin(0.2)
        pad_res.SetTopMargin(0)
        pad_res.Draw()

        # change directory into main pad
        pad_main.cd()

        # get histograms from ROOT files
        hist_v1 = f_v1.Get(
            f"anomalyScore_{sample_names[i]}_CICADA_v1p2p0{N_str}"
        )
        hist_v2 = f_v2.Get(
            f"anomalyScore_{sample_names[i]}_CICADA_v2p2p0{N_str}"
        )
        hist_teacher = f_teacher.Get(
            f"anomalyScore_{sample_names[i]}_CICADA_vXp2p0{N_str}_teacher"
        )

		# styling
        hist_v1.SetMarkerColor(6)
        hist_v1.SetLineColor(6)
        hist_v1.SetMarkerStyle(20)

        hist_v2.SetMarkerColor(9)
        hist_v2.SetLineColor(9)
        hist_v2.SetMarkerStyle(21)

        hist_teacher.SetMarkerColor(1)
        hist_teacher.SetLineColor(1)
        hist_teacher.SetMarkerStyle(22)

		# TEACHER HISTOGRAM
        hist_teacher.Scale(1/hist_teacher.Integral())  # normalize
        hist_teacher.GetYaxis().SetRangeUser(1e-7,1e4)  # set y axis range
        hist_teacher.GetXaxis().SetRangeUser(0,256)  # set x axis range
        hist_teacher.SetStats(0)  # remove statistics box from plot
        hist_teacher.SetTitle("")  # remove title from plot
        hist_teacher.GetYaxis().SetTitle("Frequency")  # set y axis label
        hist_teacher.Draw("e")  # draw histogram

        # STUDENT HISTOGRAMS
        hist_v1.Scale(1/hist_v1.Integral())  # normalize
        hist_v1.SetStats(0)  # remove statistics box from plot
        hist_v1.SetTitle("")  # remove title from plot )
        hist_v1.Draw("e same")  # draw histogram

        hist_v2.Scale(1/hist_v2.Integral())
        hist_v2.SetStats(0)  # remove statistics box from plot )
        hist_v2.SetTitle("")  # remove title from plot
        hist_v2.Draw("e same")  # draw histogram

		# create CMS label
        cmsLatex = createCMSLabel()
        cmsLatex.DrawLatex(0.1,
                           0.92,
                           "#font[61]{CMS} #font[52]{Preliminary}")

		# create and draw legend
        legend = ROOT.TLegend(0.6, 0.7, 1.0, 0.9)
        legend.AddEntry(hist_teacher, "Teacher", "PE")
        legend.AddEntry(hist_v1, "Student v1", "PE")
        legend.AddEntry(hist_v2, "Student v2", "PE")
        legend.SetTextSize(0.04)
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.Draw()

        pad_main.SetLogy() # make y axis of pad log-scale
        c1.cd() # change directory back to canvas

		# need separate loop for residual plots
        # change directory into res plot pad
        pad_res.cd()

        # create legend for ratio plot
        legend_res = ROOT.TLegend(0.6,0.75,1.0,0.95)
        legend_res.SetTextSize(0.07)
        legend_res.SetBorderSize(0)
        legend_res.SetFillStyle(0)

        # create stack to add histograms to
        hs = ROOT.THStack("hs","hs")

		# calculate ratio hists and add to stack
        res_hist_v1 = hist_v1.Clone("res_hist_v1")
        res_hist_v1.Sumw2()  # handle error bars properly
        res_hist_v1.Add(hist_teacher, -1)  # subtract teacher score
        res_hist_v1.SetMarkerColor(6)
        res_hist_v1.SetLineColor(6)
        res_hist_v1.SetMarkerStyle(20)
        hs.Add(res_hist_v1)
        legend_res.AddEntry(res_hist_v1, "(Student v1) - (Teacher)")

        res_hist_v2 = hist_v2.Clone("res_hist_v2")
        res_hist_v2.Sumw2()
        res_hist_v2.Add(hist_teacher, -1)
        res_hist_v2.SetMarkerColor(9)
        res_hist_v2.SetLineColor(9)
        res_hist_v2.SetMarkerStyle(21)
        hs.Add(res_hist_v2)
        legend_res.AddEntry(res_hist_v2, "(Student v2) - (Teacher)")


		# create horizontal line at 0
        xvals = array('d')
        yvals = array('d')
        n = 300
        for j in range(n):
            xvals.append(j)
            yvals.append(0)
        g = ROOT.TGraph(n, xvals, yvals)
        g.SetLineColor(1)  # make line black
        g.GetXaxis().SetRangeUser(0,256)  # set x axis range of plot
        g.GetYaxis().SetRangeUser(-1,1)  # set y axis range
        g.SetTitle("")  # make title invisible
        g.GetXaxis().SetTitle("CICADA Score")  # set x axis title
        g.GetYaxis().SetTitle("Residual")  # set y axis title
        # spacing and text size options
        g.GetXaxis().SetLabelSize(0.07)
        g.GetYaxis().SetLabelSize(0.07)
        g.GetXaxis().SetTitleSize(0.07)
        g.GetYaxis().SetTitleSize(0.07)
        g.GetYaxis().SetTitleOffset(0.6)
        g.Draw("AC")

		# draw ratios
        hs.Draw("e nostack same")
        legend_res.Draw()
        c1.cd()

        # draw canvas and save png
        c1.Draw()
        c1.SaveAs(
            f"{output_dir}/scorehist_{sample_names[i]}_CICADA_vXp2p0{N_str}.png"
        )
        c1.Close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This program creates CICADA score plots")
    parser.add_argument("-v1", "--input_v1", help="path to input ROOT file containing hists student v1")
    parser.add_argument("-v2", "--input_v2", help="path to input ROOT file containing hists student v2")
    parser.add_argument("-t", "--input_teacher", help="path to input ROOT file containing hists teacher")
    parser.add_argument("-n", "--n", default=False, help="whether cicada name has N at the end")
    parser.add_argument( "-o", "--output_dir", default='./', help="directory to save output plots")

    args = parser.parse_args()

    main(args.input_v1,
         args.input_v2,
         args.input_teacher,
         args.n,
         args.output_dir)

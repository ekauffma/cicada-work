import ROOT
import argparse
import numpy as np
from array import array
import json

with open('plottingOptions.json') as f:
    options = json.load(f)

# converts cicada_name to plot print format (e.g. CICADA_v1p2p2 -> CICADA 1.2.2)
def convertCICADANametoPrint(cicada_name):
    cicada_name = cicada_name.replace("_", " ")
    cicada_name = cicada_name.replace("v", "")
    cicada_name = cicada_name.replace("p", ".")
    return cicada_name

# function for drawing labels on the plots
def createLabel():
    latex = ROOT.TLatex()
    latex.SetTextSize(0.03)
    latex.SetNDC(True)
    latex.SetTextAlign(11)

    return latex

########################################################################
# Uses two 3d histograms (bkg_hist for background, sig_hist for signal)
# to compute the ROC along axis (which can be 0 for CICADA score or 1
# for HT). Returns TPR and FPR as arrays
def calculateROC(bkg_hist, sig_hist, axis):

    if axis not in [0,1]:
        raise ValueError("axis must be 0 or 1")

    # get total integral of background histogram
    integral_bkg = float(
        bkg_hist.Integral(0, bkg_hist.GetNbinsX()+1,
                          0, bkg_hist.GetNbinsY()+1,
                          0, bkg_hist.GetNbinsZ()+1)
    )

    # get total integral of signal histogram
    integral_sig = float(
        sig_hist.Integral(0, sig_hist.GetNbinsX()+1,
                          0, sig_hist.GetNbinsY()+1,
                          0, sig_hist.GetNbinsZ()+1)
    )


    # get list of thresholds
    if axis==0:
        edges = [sig_hist.GetXaxis().GetBinLowEdge(i) for i in range(1, sig_hist.GetNbinsX() + 2)]
    else:
        edges = [sig_hist.GetYaxis().GetBinLowEdge(i) for i in range(1, sig_hist.GetNbinsY() + 2)]

    tpr = []
    fpr = []
    # compute FPR and TPR for each threshold value
    for threshold in edges:

        if axis==0:
            # find bin that corresponds to current threshold
            threshold_bin = sig_hist.GetXaxis().FindBin(threshold)

            # compute partial integrals for accepted events
            integral_sig_partial = sig_hist.Integral(
                threshold_bin, sig_hist.GetNbinsX() + 1,
                0, sig_hist.GetNbinsY()+1,
                0, sig_hist.GetNbinsZ()+1
            )
            integral_bkg_partial = bkg_hist.Integral(
                threshold_bin, bkg_hist.GetNbinsX() + 1,
                0, bkg_hist.GetNbinsY()+1,
                0, bkg_hist.GetNbinsZ()+1
            )
        else:
            threshold_bin = sig_hist.GetYaxis().FindBin(threshold)

            integral_sig_partial = sig_hist.Integral(
                0, sig_hist.GetNbinsX() + 1,
                threshold_bin, sig_hist.GetNbinsY()+1,
                0, sig_hist.GetNbinsZ()+1
            )
            integral_bkg_partial = bkg_hist.Integral(
                0, bkg_hist.GetNbinsX() + 1,
                threshold_bin, bkg_hist.GetNbinsY()+1,
                0, bkg_hist.GetNbinsZ()+1
            )

        # divide accepted events by total events
        tpr_current = integral_sig_partial / integral_sig
        fpr_current = integral_bkg_partial / integral_bkg

        tpr.append(tpr_current)
        fpr.append(fpr_current)

        if (tpr_current==0) and (fpr_current==0):
            break

    # convert to array
    tpr = array('d', tpr)
    fpr = array('d', fpr)

    return tpr, fpr

########################################################################
# Uses two 3d histograms (bkg_hist for background, sig_hist for signal)
# to compute the CICADA (or other variable associated with or_axis >
# or_threshold) ROC. Returns TPR and FPR as arrays
def calculateROCOR(bkg_hist, sig_hist, or_threshold, or_axis):

    # get total integral of background histogram
    integral_bkg = float(
        bkg_hist.Integral(
            0, bkg_hist.GetNbinsX()+1,
            0, bkg_hist.GetNbinsY()+1,
            0, bkg_hist.GetNbinsZ()+1
        )
    )

    # get total integral of signal histogram
    integral_sig = float(
        sig_hist.Integral(
            0, sig_hist.GetNbinsX()+1,
            0, sig_hist.GetNbinsY()+1,
            0, sig_hist.GetNbinsZ()+1
        )
    )

    if or_axis not in [1,2]:
        raise ValueError("or_axis must be 1 or 2")

    # compute bin associated with or_threshold
    if or_axis == 1:
        or_threshold_bin = sig_hist.GetYaxis().FindBin(or_threshold)
    else:
        or_threshold_bin = sig_hist.GetZaxis().FindBin(or_threshold)

    # get list of thresholds
    edges = [sig_hist.GetXaxis().GetBinLowEdge(i) for i in range(1, sig_hist.GetNbinsX() + 2)]

    tpr = []
    fpr = []
    for threshold in edges:
        threshold_bin = sig_hist.GetXaxis().FindBin(threshold)

        # Integrate over bins where x > threshold, including
        # overflow bins
        integral_sig_partial_x = sig_hist.Integral(
            threshold_bin, sig_hist.GetNbinsX() + 1,
            0, sig_hist.GetNbinsY() + 1,
            0, sig_hist.GetNbinsZ() + 1
        )
        integral_bkg_partial_x = bkg_hist.Integral(
            threshold_bin, bkg_hist.GetNbinsX() + 1,
            0, bkg_hist.GetNbinsY() + 1,
            0, bkg_hist.GetNbinsZ() + 1
        )

        if or_axis == 1:
            # Integrate over bins where y or z > or_threshold,
            # including overflow bins
            integral_sig_partial_yz = sig_hist.Integral(
                0, sig_hist.GetNbinsX() + 1,
                or_threshold_bin, sig_hist.GetNbinsY() + 1,
                0, sig_hist.GetNbinsZ() + 1
            )
            integral_bkg_partial_yz = bkg_hist.Integral(
                0, bkg_hist.GetNbinsX() + 1,
                or_threshold_bin, bkg_hist.GetNbinsY() + 1,
                0, bkg_hist.GetNbinsZ() + 1
            )

            # Compute the double-counted accepted events,
            # including overlap and overflow bins
            overlap_sig = sig_hist.Integral(
                threshold_bin, sig_hist.GetNbinsX() + 1,
                or_threshold_bin, sig_hist.GetNbinsY() + 1,
                0, sig_hist.GetNbinsZ() + 1
            )
            overlap_bkg = bkg_hist.Integral(
                threshold_bin, bkg_hist.GetNbinsX() + 1,
                or_threshold_bin, bkg_hist.GetNbinsY() + 1,
                0, bkg_hist.GetNbinsZ() + 1
            )

        else:
            # Integrate over bins where y or z > or_threshold,
            # including overflow bins
            integral_sig_partial_yz = sig_hist.Integral(
                0, sig_hist.GetNbinsX() + 1,
                0, sig_hist.GetNbinsY() + 1,
                or_threshold_bin, sig_hist.GetNbinsZ() + 1
            )
            integral_bkg_partial_yz = bkg_hist.Integral(
                0, bkg_hist.GetNbinsX() + 1,
                0, bkg_hist.GetNbinsY() + 1,
                or_threshold_bin, bkg_hist.GetNbinsZ() + 1
            )

            # Compute the double-counted accepted events,
            # including overlap and overflow bins
            overlap_sig = sig_hist.Integral(
                threshold_bin, sig_hist.GetNbinsX() + 1,
                0, sig_hist.GetNbinsY() + 1,
                or_threshold_bin, sig_hist.GetNbinsZ() + 1
            )
            overlap_bkg = bkg_hist.Integral(
                threshold_bin, bkg_hist.GetNbinsX() + 1,
                0, bkg_hist.GetNbinsY() + 1,
                or_threshold_bin, bkg_hist.GetNbinsZ() + 1
            )


        # compute total number of accepted events and subtract
        # out overlap
        accepted_sig = (integral_sig_partial_x + integral_sig_partial_yz
                        - overlap_sig)
        accepted_bkg = (integral_bkg_partial_x + integral_bkg_partial_yz
                        - overlap_bkg)

        # divide by total number of events to get rates
        tpr_current = accepted_sig / integral_sig
        fpr_current = accepted_bkg / integral_bkg

        tpr.append(tpr_current)
        fpr.append(fpr_current)

        if (tpr_current==0) and (fpr_current==0):
            break

    # convert to arrays
    tpr = array('d', tpr)
    fpr = array('d', fpr)

    return tpr, fpr

########################################################################
# Uses tpr and fpr arrays to create a ROOT TGraph, plotting fpr on the
# x-axis and tpr along the y-axis. color refers to the marker and line
# color of the graph, markerstyle refers to the ROOT marker style, first
# indicates whether the TGraph will be the first graph on its respective
# canvas, and bkg_name is either "Zero Bias" or "Single Neutrino Gun".
# Returns the TGraph object
def createROCTGraph(tpr, fpr, color = 1, markerstyle = 20, first = True,
                    bkg_name = "Zero Bias",
                    rate=True, logx = False, logy = False):

    # determine minimum axis limits based on whether axis is log scale
    if logx: min_x = options["ROC_x_min_log"]
    else: min_x = 0
    if logy: min_y = options["ROC_y_min_log"]
    else: min_y = 0

    # scale by rate factor if desired
    if rate:
        fpr = array('d', [n * options["rate_scale_factor"] for n in fpr])

    # create TGraph
    g = ROOT.TGraph(len(tpr), fpr, tpr)

    # plotting options for graph
    g.SetTitle("")
    g.SetLineWidth(4)
    g.SetLineColor(color)
    g.SetMarkerColor(color)
    g.SetMarkerSize(1)
    g.SetMarkerStyle(markerstyle)
    if first:
        if rate:
            g.GetXaxis().SetTitle(f"{bkg_name} Rate [kHz]")
            g.GetYaxis().SetTitle("Signal Efficiency")
        else:
            g.GetXaxis().SetTitle(f"{bkg_name} FPR (Number Accepted)/(Total)")
            g.GetYaxis().SetTitle("Signal TPR (Number Accepted)/(Total)")

    if rate:
        g.GetXaxis().SetRangeUser(min_x * options["rate_scale_factor"], options["ROC_x_max"] * options["rate_scale_factor"])
        g.GetXaxis().SetLimits(min_x * options["rate_scale_factor"], options["ROC_x_max"] * options["rate_scale_factor"])
    else:
        g.GetXaxis().SetRangeUser(min_x, options["ROC_x_max"])
        g.GetXaxis().SetLimits(min_x, options["ROC_x_max"])
    g.GetYaxis().SetRangeUser(min_y, options["ROC_y_max"])

    return g

########################################################################
# Calculates and returns the rate of events in hist which pass at least
# one unprescaled L1 Trigger bit.
def getL1UnprescaledEfficiency(hist):

    n_fail = hist.Integral(0, hist.GetNbinsX()+1, 0, hist.GetNbinsY()+1, 1, 1)
    n_pass = hist.Integral(0, hist.GetNbinsX()+1, 0, hist.GetNbinsY()+1, 2, 2)

    return n_pass / (n_fail + n_pass)

########################################################################
# Calculates and returns the rate of events in hist which pass
# HT > 200
def getHTEfficiency(hist):
    ht_threshold_bin = hist.GetYaxis().FindBin(options["ht_threshold"])
    n_denominator = hist.Integral(0, hist.GetNbinsX()+1, 0, hist.GetNbinsY()+1, 0, hist.GetNbinsZ()+1)
    n_numerator = hist.Integral(0, hist.GetNbinsX()+1, ht_threshold_bin, hist.GetNbinsY()+1, 0, hist.GetNbinsZ()+1)

    return n_numerator / n_denominator

########################################################################
# Uses the 3d input histogram hist (zero bias) to calculate the ratio of
# accepted events to total events for each threshold. This is done for
# the specified axis "axis" which is 0 for CICADA score and 1 for HT.
# Returns a TH1D histogram of ratios of accepted events
def getAcceptRatioHist(hist, axis, hist_name = "ratio_accepted"):

    if axis not in [0,1]:
        raise ValueError("axis must be 0 or 1")

    # get total integral of histogram
    integral = float(
        hist.Integral(
            0, hist.GetNbinsX()+1,
            0, hist.GetNbinsY()+1,
            0, hist.GetNbinsZ()+1
        )
    )

    # get list of thresholds
    if axis==0:
        thresholds = [hist.GetXaxis().GetBinLowEdge(i) for i in range(1, hist.GetNbinsX() + 2)]

        # create efficiency hist
        hist_out = ROOT.TH1D(
            hist_name,
            "(Number Accepted) / (Total Number)",
            hist.GetNbinsX(),
            hist.GetXaxis().GetXmin(),
            hist.GetXaxis().GetXmax()
        )

    else:
        thresholds = [hist.GetYaxis().GetBinLowEdge(i) for i in range(1, hist.GetNbinsY() + 2)]

        # create efficiency hist
        hist_out = ROOT.TH1D(
            hist_name,
            "(Number Accepted) / (Total Number)",
            hist.GetNbinsY(),
            hist.GetYaxis().GetXmin(),
            hist.GetYaxis().GetXmax()
        )

    # compute rate for each threshold value
    for j in range(len(thresholds)):

        if axis==0:
            # find bin that corresponds to current threshold
            threshold_bin = hist.GetXaxis().FindBin(thresholds[j])

            # Integrate over bins where x > threshold
            integral_partial = hist.Integral(
                threshold_bin, hist.GetNbinsX() + 1,
                0, hist.GetNbinsY() + 1,
                0, hist.GetNbinsZ() + 1
            )
        else:
            threshold_bin = hist.GetYaxis().FindBin(thresholds[j])

            integral_partial = hist.Integral(
                0, hist.GetNbinsX() + 1,
                threshold_bin, hist.GetNbinsY() + 1,
                0, hist.GetNbinsZ() + 1
            )

        # calculate uncertainty
        uncertainty = np.sqrt(integral_partial)/integral

        # divide partial integral by total integral to get ratio
        ratio_accepted = integral_partial/integral

        hist_out.SetBinContent(j+1, ratio_accepted * options["rate_scale_factor"])
        hist_out.SetBinError(j+1, uncertainty)


    return hist_out

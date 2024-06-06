########################################################################
## drawROC.py                                                         ##
## Author: Elliott Kauffman                                           ##
## takes output histograms from createHistsForROC.py and creates ROC  ##
## plots                                                              ##
########################################################################

import ROOT
import argparse
import numpy as np
from array import array
from sampleNames import sample_name_dict

max_eff_val_x = 0.00344054 * 2
max_eff_val_x = 0.03 # x axis range, set for debugging purposes
max_eff_val_y = 1.2 # y axis range, gives extra room for legend

# convert from efficiency to rate
rate_scale_factor = 2452.0 * 11245e-3

# threshold values for OR ROC plots
ht_threshold = 200
l1_threshold = 1

# names of CICADA models
cicada_names = ["CICADA_v1p2p2"]
                #"CICADA_v2p2p2",
                #"CICADA_v1p2p2N",
                #"CICADA_v2p2p2N"]
# names of CICADA models for printing
cicada_names_print = ["CICADA 1.2.2",
                      "CICADA 2.2.2",
                      "CICADA 1.2.2N",
                      "CICADA 2.2.2N"]

# function for drawing the label on the plots
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
    edges = [sig_hist.GetXaxis().GetBinLowEdge(i) for i in range(1, sig_hist.GetNbinsX() + 2)]

    tpr = []
    fpr = []
    # compute FPR and TPR for each threshold value
    for threshold in edges:
    
        # find bin that corresponds to current threshold
        threshold_bin = sig_hist.GetXaxis().FindBin(threshold)

        # compute partial integrals for accepted events
        if axis==0:
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
def createROCTGraph(tpr, fpr, color = 1, markerstyle = 20, first = True, bkg_name = "Zero Bias"):

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
        g.GetXaxis().SetTitle(f"{bkg_name} FPR (Number Accepted)/(Total)")
        g.GetYaxis().SetTitle("Signal TPR (Number Accepted)/(Total)")
    g.GetXaxis().SetRangeUser(0, max_eff_val_x)
    g.GetXaxis().SetLimits(0, max_eff_val_x)
    g.GetYaxis().SetRangeUser(0, max_eff_val_y)

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
    ht_threshold_bin = hist.GetYaxis().FindBin(ht_threshold)
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
    else:
        thresholds = [hist.GetYaxis().GetBinLowEdge(i) for i in range(1, hist.GetNbinsY() + 2)]
                      
    # create efficiency hist
    hist_out = ROOT.TH1D(
        hist_name,
        "(Number Accepted) / (Total Number)",
        hist.GetNbinsX(),
        hist.GetXaxis().GetXmin(),
        hist.GetXaxis().GetXmax()
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
        
        hist_out.SetBinContent(j+1, ratio_accepted)
        hist_out.SetBinError(j+1, uncertainty)
        

    return hist_out

########################################################################
def main(file_prefix, out_dir):

    # grab background files
    f_zb = ROOT.TFile(f"{file_prefix}_ZeroBias.root")
    f_sn = ROOT.TFile(f"{file_prefix}_SingleNeutrino_E-10-gun.root")
    f_bkg = [f_zb, f_sn]
    
    # names and associated print names of backgrounds
    bkg_names = ["ZeroBias", "SingleNeutrino_E-10-gun"]
    bkg_names_print = ["Zero Bias", "Single Neutrino Gun"]
    
    
    ####################################################################
    # get rate plot for HT                                             #
    ####################################################################
    
    # create ROOT canvas
    c = ROOT.TCanvas("c", "ROC", 1000, 800)
    
    # get score histogram from ZB file (cicada version doesn't matter
    # since we are integrating over that axis
    hist = f_bkg[0].Get(f"anomalyScore_ZeroBias_test_{cicada_names[0]}")
            
    # get accepted ratio histogram from above hist
    h = getAcceptRatioHist(hist, 1, hist_name = "HT")
    
    # scale by rate factor
    h.Scale(rate_scale_factor)
    
    # plotting options
    h.SetTitle("")
    h.GetXaxis().SetTitle("HT Threshold [GeV]")
    h.GetYaxis().SetTitle("Zero Bias Rate [kHz]")
    h.GetXaxis().SetRangeUser(0,300)
    h.GetYaxis().SetRangeUser(5e-3,1e5)
    h.SetStats(0)
    h.SetMarkerColor(2)
    h.SetMarkerStyle(20)
    
    # draw histogram
    h.Draw("e")
    
    # draw and save canvas
    c.SetLogy()
    c.Draw()
    c.SaveAs(f"{out_dir}/rate_ZeroBias_HT.png")
    c.Close()


    ####################################################################
    
    # get list of sample names
    sample_names = list(sample_name_dict.keys())

    # iterate through backgrounds
    for l in range(len(f_bkg)):
        # iterate through CICADA versions
        for k in range(len(cicada_names)):

            # load ZeroBias histograms
            if bkg_names[l]=="ZeroBias":
                h_zb = f_bkg[l].Get(f"anomalyScore_ZeroBias_test_{cicada_names[k]}")
            else:
                h_zb = f_bkg[l].Get(f"anomalyScore_SingleNeutrino_E-10-gun_{cicada_names[k]}")
                
                
            ############################################################
            # get rate plot for current CICADA version                 #
            ############################################################
            
            if bkg_names[l]=="ZeroBias":
                # create ROOT canvas
                c = ROOT.TCanvas("c", "ROC", 1000, 800)
                
                # get accepted ratio histogram from above hist
                h = getAcceptRatioHist(h_zb, 0, hist_name = cicada_names[k])
                
                # scale by rate factor
                h.Scale(rate_scale_factor)
                
                # plotting options
                h.SetTitle("")
                h.GetXaxis().SetTitle("CICADA score Threshold")
                h.GetYaxis().SetTitle("Zero Bias Rate [kHz]")
                h.GetXaxis().SetRangeUser(0,256)
                h.GetYaxis().SetRangeUser(5e-3,1e5)
                h.SetStats(0)
                h.SetMarkerColor(2)
                h.SetMarkerStyle(20)
                
                # draw histogram
                h.Draw("e")
                
                # draw and save canvas
                c.SetLogy()
                c.Draw()
                c.SaveAs(f"{out_dir}/rate_ZeroBias_{cicada_names[k]}.png")
                c.Close()
                

            # iterate through signal samples
            for i in range(len(sample_names)):

                # skip over the samples that are not signal
                if sample_names[i]=="ZeroBias": continue
                if sample_names[i]=="SingleNeutrino_E-10-gun": continue
                
                # for testing, only making one plot
                if sample_names[i]!="TT_TuneCP5_13p6TeV_powheg-pythia8": continue

                print(sample_names[i])

                # try to open signal file, skip signal if failed
                try:
                    f_s = ROOT.TFile(f"{file_prefix}_{sample_names[i]}.root")
                except Exception:
                    print(f"ROOT file for sample {sample_names[i]} does not exist")
                    continue

                # load histograms
                h_s = f_s.Get(f"anomalyScore_{sample_names[i]}_{cicada_names[k]}")
                ht_bin = h_s.GetYaxis().FindBin(200)

                # calculate simple ROC for CICADA score and HT
                tpr_cicada, fpr_cicada = calculateROC(h_zb, h_s, 0)
                tpr_ht, fpr_ht = calculateROC(h_zb, h_s, 1)

                # calcualte ROC for CICADA score > threshold OR HT > 200
                try:
                    tpr_or_ht, fpr_or_ht = calculateROCOR(h_zb, h_s, ht_threshold, 1)
                except ValueError as e:
                    print("Error:", e)

                # calcualte ROC for CICADA score > threshold OR L1 Unprescaled Trigger
                try:
                    tpr_or_l1, fpr_or_l1 = calculateROCOR(h_zb, h_s, l1_threshold, 2)
                except ValueError as e:
                    print("Error:", e)


                ########################################################################
                # plot for HT OR                                                       #
                ########################################################################

                # create ROOT canvas
                c = ROOT.TCanvas("c", "ROC", 1000, 800)

                # draw TGraph for HT OR CICADA score
                g_or = createROCTGraph(tpr_or_ht,
                                       fpr_or_ht,
                                       color = 6,
                                       markerstyle = 20,
                                       first = True,
                                       bkg_name = bkg_names_print[l])
                g_or.GetXaxis().SetRangeUser(0, max_eff_val_x)
                g_or.Draw("ACP")

                # draw TGraph for CICADA score
                g_cicada = createROCTGraph(tpr_cicada,
                                           fpr_cicada,
                                           color = 8,
                                           markerstyle = 21,
                                           first = False)
                g_cicada.Draw("CP same")

                # draw TGraph for HT
                g_ht = createROCTGraph(tpr_ht,
                                       fpr_ht,
                                       color = 9,
                                       markerstyle = 22,
                                       first = False)
                g_ht.Draw("CP same")

                # draw graph title
                title_template = "#splitline{{Signal = {str_sig}}}{{CICADA Version = {str_cic}}}"
                title = title_template.format(str_sig = sample_name_dict[sample_names[i]], str_cic = cicada_names_print[k])
                titleObj = createLabel()
                titleObj.DrawLatex(0.1, 0.93, title)

                # plot point for l1 unprescaled efficiency
                l1_eff_s = getL1UnprescaledEfficiency(h_s)
                l1_eff_zb = getL1UnprescaledEfficiency(h_zb)
                print("L1 Unprescaled Signal (Number Accepted)/(Total) = ", l1_eff_s)
                print("L1 Unprescaled Bkg (Number Accepted)/(Total) = ", l1_eff_zb)
                g_l1 = ROOT.TGraph(1, array('d', [l1_eff_zb]), array('d', [l1_eff_s]))
                g_l1.SetMarkerSize(1)
                g_l1.SetMarkerStyle(20)
                g_l1.GetXaxis().SetRangeUser(0, max_eff_val_x)
                g_l1.GetYaxis().SetRangeUser(0, max_eff_val_y)
                g_l1.Draw("P same")

                # plot point for HT>200
                ht_eff_s = getHTEfficiency(h_s)
                ht_eff_zb = getHTEfficiency(h_zb)
                print("HT>200 Signal (Number Accepted)/(Total) = ", ht_eff_s)
                print("HT>200 Bkg (Number Accepted)/(Total) = ", ht_eff_zb)
                g_ht_point = ROOT.TGraph(1, array('d', [ht_eff_zb]), array('d', [ht_eff_s]))
                g_ht_point.SetMarkerSize(1)
                g_ht_point.SetMarkerColor(4)
                g_ht_point.SetMarkerStyle(20)
                g_ht_point.GetXaxis().SetRangeUser(0, max_eff_val_x)
                g_ht_point.GetYaxis().SetRangeUser(0, max_eff_val_y)
                g_ht_point.Draw("P same")

                # draw legend
                legend = ROOT.TLegend(0.1,0.77,0.9, 0.9)
                legend.AddEntry(g_or, "(CICADA > Threshold) or (HT > 200) ")
                legend.AddEntry(g_cicada, "CICADA > Threshold")
                legend.AddEntry(g_ht, "HT > Threshold")
                legend.AddEntry(g_l1, "Unprescaled Trigger", "p")
                legend.AddEntry(g_ht_point, "HT > 200", "p")
                legend.SetBorderSize(0)
                legend.SetFillStyle(0)
                legend.SetTextSize(0.025)
                legend.Draw()

                # draw canvas and save plot
                c.Update()
                c.Draw()
                c.SaveAs(f"{out_dir}/ROC_HT_{bkg_names[l]}_{cicada_names[k]}_{sample_names[i]}.png")
                c.Close()

                ########################################################################
                # plot for L1 OR                                                       #
                ########################################################################

                # create ROOT canvas
                c = ROOT.TCanvas("c", "ROC", 1000, 800)

                # draw TGraph for L1 OR CICADA score
                g_or = createROCTGraph(tpr_or_l1,
                                       fpr_or_l1,
                                       color = 6,
                                       markerstyle = 20,
                                       first = True,
                                       bkg_name = bkg_names_print[l])
                g_or.GetXaxis().SetRangeUser(0, max_eff_val_x)
                g_or.Draw("ACP")

                # draw TGraph for CICADA score
                g_cicada = createROCTGraph(tpr_cicada,
                                           fpr_cicada,
                                           color = 8,
                                           markerstyle = 21,
                                           first = False)
                g_cicada.Draw("CP same")

                # draw graph title
                title_template = "#splitline{{Signal = {str_sig}}}{{CICADA Version = {str_cic}}}"
                title = title_template.format(str_sig = sample_name_dict[sample_names[i]], str_cic = cicada_names_print[k])
                titleObj = createLabel()
                titleObj.DrawLatex(0.1, 0.93, title)

                # plot point for l1 unprescaled efficiency
                l1_eff_s = getL1UnprescaledEfficiency(h_s)
                l1_eff_zb = getL1UnprescaledEfficiency(h_zb)
                print("L1 Unprescaled Signal (Number Accepted)/(Total) = ", l1_eff_s)
                print("L1 Unprescaled Bkg (Number Accepted)/(Total) = ", l1_eff_zb)
                g_l1 = ROOT.TGraph(1, array('d', [l1_eff_zb]), array('d', [l1_eff_s]))
                g_l1.SetMarkerSize(1)
                g_l1.SetMarkerStyle(20)
                g_l1.GetXaxis().SetRangeUser(0, max_eff_val_x)
                g_l1.GetYaxis().SetRangeUser(0, max_eff_val_y)
                g_l1.Draw("P same")

                # draw legend
                legend = ROOT.TLegend(0.1,0.77,0.9, 0.9)
                legend.AddEntry(g_or, "(CICADA > Threshold) or (Passed an Unprescaled L1 Trigger)")
                legend.AddEntry(g_cicada, "CICADA > Threshold")
                legend.AddEntry(g_l1, "Unprescaled Trigger", "p")
                legend.SetBorderSize(0)
                legend.SetFillStyle(0)
                legend.SetTextSize(0.025)
                legend.Draw()

                # draw canvas and save plot
                c.Update()
                c.Draw()
                c.SaveAs(f"{out_dir}/ROC_L1_{bkg_names[l]}_{cicada_names[k]}_{sample_names[i]}.png")
                c.Close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This program creates CICADA ROC plots"
    )

    parser.add_argument(
        "-p",
        "--file_prefix",
        help="prefix of files containing histograms"
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        default='./',
        help="directory to save output plots"
    )

    args = parser.parse_args()


    main(
        args.file_prefix,
        args.output_dir
    )

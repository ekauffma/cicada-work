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
from efficiencies import efficiencies
import ctypes

max_eff_val_x = 0.00344054 * 2
max_eff_val_x = 1.0
max_eff_val_y = 1.2


#rate_scale_factor = 2544.0 * 11245e-3

ht_threshold = 200
l1_threshold = 1

# names of CICADA models
cicada_names = ["CICADA_v1p2p2"]
                #"CICADA_v2p2p2",
                #"CICADA_v1p2p2N",
                #"CICADA_v2p2p2N"]
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

    edges = [sig_hist.GetXaxis().GetBinLowEdge(i) for i in range(1, sig_hist.GetNbinsX() + 2)]

    tpr = []
    fpr = []
    for threshold in edges:
        threshold_bin = sig_hist.GetXaxis().FindBin(threshold)
        
        if axis==0:
            integral_sig_partial = sig_hist.Integral(threshold_bin, sig_hist.GetNbinsX() + 1,
                                                     0, sig_hist.GetNbinsY()+1,
                                                     0, sig_hist.GetNbinsZ()+1)
            integral_bkg_partial = bkg_hist.Integral(threshold_bin, bkg_hist.GetNbinsX() + 1,
                                                     0, bkg_hist.GetNbinsY()+1,
                                                     0, bkg_hist.GetNbinsZ()+1)
        else:
            integral_sig_partial = sig_hist.Integral(0, sig_hist.GetNbinsX() + 1,
                                                     threshold_bin, sig_hist.GetNbinsY()+1,
                                                     0, sig_hist.GetNbinsZ()+1)
            integral_bkg_partial = bkg_hist.Integral(0, bkg_hist.GetNbinsX() + 1,
                                                     threshold_bin, bkg_hist.GetNbinsY()+1,
                                                     0, bkg_hist.GetNbinsZ()+1)

        tpr_current = integral_sig_partial / integral_sig
        fpr_current = integral_bkg_partial / integral_bkg

        tpr.append(tpr_current)
        fpr.append(fpr_current)

    tpr = array('d', tpr)
    fpr = array('d', fpr)

    return tpr, fpr

def calculateROCOR(bkg_hist, sig_hist, or_threshold, or_axis):

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

    if or_axis not in [1,2]:
        raise ValueError("or_axis must be 1 or 2")
    if or_axis == 1:
        or_threshold_bin = sig_hist.GetYaxis().FindBin(or_threshold)
    else:
        or_threshold_bin = sig_hist.GetZaxis().FindBin(or_threshold)

    edges = [sig_hist.GetXaxis().GetBinLowEdge(i) for i in range(1, sig_hist.GetNbinsX() + 2)]

    tpr = []
    fpr = []
    for threshold in edges:
        threshold_bin = sig_hist.GetXaxis().FindBin(threshold)

        # Integrate over bins where x > threshold, including overflow bins
        integral_sig_partial_x = sig_hist.Integral(threshold_bin, sig_hist.GetNbinsX() + 1,
                                                   0, sig_hist.GetNbinsY() + 1,
                                                   0, sig_hist.GetNbinsZ() + 1)
        integral_bkg_partial_x = bkg_hist.Integral(threshold_bin, bkg_hist.GetNbinsX() + 1,
                                                   0, bkg_hist.GetNbinsY() + 1,
                                                   0, bkg_hist.GetNbinsZ() + 1)

        if or_axis == 1:
            # Integrate over bins where y or z > or_threshold, including overflow bins
            integral_sig_partial_yz = sig_hist.Integral(0, sig_hist.GetNbinsX() + 1,
                                                        or_threshold_bin, sig_hist.GetNbinsY() + 1,
                                                        0, sig_hist.GetNbinsZ() + 1)
            integral_bkg_partial_yz = bkg_hist.Integral(0, bkg_hist.GetNbinsX() + 1,
                                                        or_threshold_bin, bkg_hist.GetNbinsY() + 1,
                                                        0, bkg_hist.GetNbinsZ() + 1)
            # Compute the double-counted accepted events, including overlap and overflow bins
            overlap_sig = sig_hist.Integral(threshold_bin, sig_hist.GetNbinsX() + 1,
                                            or_threshold_bin, sig_hist.GetNbinsY() + 1,
                                            0, sig_hist.GetNbinsZ() + 1)
            overlap_bkg = bkg_hist.Integral(threshold_bin, bkg_hist.GetNbinsX() + 1,
                                            or_threshold_bin, bkg_hist.GetNbinsY() + 1,
                                            0, bkg_hist.GetNbinsZ() + 1)

        else:
            # Integrate over bins where y or z > or_threshold, including overflow bins
            integral_sig_partial_yz = sig_hist.Integral(0, sig_hist.GetNbinsX() + 1,
                                                        0, sig_hist.GetNbinsY() + 1,
                                                        or_threshold_bin, sig_hist.GetNbinsZ() + 1)
            integral_bkg_partial_yz = bkg_hist.Integral(0, bkg_hist.GetNbinsX() + 1,
                                                        0, bkg_hist.GetNbinsY() + 1,
                                                        or_threshold_bin, bkg_hist.GetNbinsZ() + 1)
            # Compute the double-counted accepted events, including overlap and overflow bins
            overlap_sig = sig_hist.Integral(threshold_bin, sig_hist.GetNbinsX() + 1,
                                            0, sig_hist.GetNbinsY() + 1,
                                            or_threshold_bin, sig_hist.GetNbinsZ() + 1)
            overlap_bkg = bkg_hist.Integral(threshold_bin, bkg_hist.GetNbinsX() + 1,
                                            0, bkg_hist.GetNbinsY() + 1,
                                            or_threshold_bin, bkg_hist.GetNbinsZ() + 1)



        accepted_sig = integral_sig_partial_x + integral_sig_partial_yz - overlap_sig
        accepted_bkg = integral_bkg_partial_x + integral_bkg_partial_yz - overlap_bkg

        tpr_current = accepted_sig / integral_sig
        fpr_current = accepted_bkg / integral_bkg

        tpr.append(tpr_current)
        fpr.append(fpr_current)

    tpr = array('d', tpr)
    fpr = array('d', fpr)

    return tpr, fpr

def createROCTGraph(tpr, fpr, color = 1, markerstyle = 20, first = True, bkg_name = "Zero Bias"):

    # create TGraph
    g = ROOT.TGraph(len(tpr), fpr, tpr)

    # plotting options graph
    g.SetTitle("")
    g.SetLineWidth(4)
    g.SetLineColor(color)
    g.SetMarkerColor(color)
    g.SetMarkerSize(1)
    g.SetMarkerStyle(markerstyle)
    if first:
        g.GetXaxis().SetTitle(f"{bkg_name} Efficiency (FPR)")
        g.GetYaxis().SetTitle("Signal Efficiency")
    g.GetXaxis().SetRangeUser(0, max_eff_val_x)
    g.GetXaxis().SetLimits(0, max_eff_val_x)
    g.GetYaxis().SetRangeUser(0, max_eff_val_y)

    return g

def getL1UnprescaledEfficiency(hist):

    n_fail = hist.Integral(0, hist.GetNbinsX()+1, 0, hist.GetNbinsY()+1, 1, 1)
    n_pass = hist.Integral(0, hist.GetNbinsX()+1, 0, hist.GetNbinsY()+1, 2, 2)

    return n_pass / (n_fail + n_pass)

def getHTEfficiency(hist):
    ht_threshold_bin = hist.GetYaxis().FindBin(ht_threshold)
    n_denominator = hist.Integral(0, hist.GetNbinsX()+1, 0, hist.GetNbinsY()+1, 0, hist.GetNbinsZ()+1)
    n_numerator = hist.Integral(0, hist.GetNbinsX()+1, ht_threshold_bin, hist.GetNbinsY()+1, 0, hist.GetNbinsZ()+1)

    return n_numerator / n_denominator




def main(file_prefix, out_dir):

    f_zb = ROOT.TFile(f"{file_prefix}_ZeroBias.root")
    f_sn = ROOT.TFile(f"{file_prefix}_SingleNeutrino_E-10-gun.root")

    f_bkg = [f_zb, f_sn]
    bkg_names = ["ZeroBias", "SingleNeutrino_E-10-gun"]
    bkg_names_print = ["Zero Bias", "Single Neutrino Gun"]

    for l in range(len(f_bkg)):
        for k in range(len(cicada_names)):

            # load ZeroBias histograms
            if bkg_names[l]=="ZeroBias":
                h_zb = f_bkg[l].Get(f"anomalyScore_ZeroBias_test_{cicada_names[k]}")
            else:
                h_zb = f_bkg[l].Get(f"anomalyScore_SingleNeutrino_E-10-gun_{cicada_names[k]}")

            sample_names = list(sample_name_dict.keys())
            for i in range(len(sample_names)):

                if sample_names[i]=="ZeroBias": continue
                if sample_names[i]=="SingleNeutrino_E-10-gun": continue
                if sample_names[i]!="TT_TuneCP5_13p6TeV_powheg-pythia8": continue

                print()
                print(sample_names[i])

                try:
                    f_s = ROOT.TFile(f"{file_prefix}_{sample_names[i]}.root")
                except Exception:
                    print(f"ROOT file for sample {sample_names[i]} does not exist")
                    continue

                # load histograms
                h_s = f_s.Get(f"anomalyScore_{sample_names[i]}_{cicada_names[k]}")
                ht_bin = h_s.GetYaxis().FindBin(200)

                tpr_cicada, fpr_cicada = calculateROC(h_zb, h_s, 0)

                tpr_ht, fpr_ht = calculateROC(h_zb, h_s, 1)

                try:
                    tpr_or_ht, fpr_or_ht = calculateROCOR(h_zb, h_s, ht_threshold, 1)
                except ValueError as e:
                    print("Error:", e)

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
                g_or.Draw("AP")

                # draw TGraph for CICADA score
                g_cicada = createROCTGraph(tpr_cicada,
                                           fpr_cicada,
                                           color = 8,
                                           markerstyle = 21,
                                           first = False)
                g_cicada.Draw("P same")

                # draw TGraph for HT
                g_ht = createROCTGraph(tpr_ht,
                                       fpr_ht,
                                       color = 9,
                                       markerstyle = 22,
                                       first = False)
                g_ht.Draw("P same")

                # draw graph title
                title_template = "#splitline{{Signal = {str_sig}}}{{CICADA Version = {str_cic}}}"
                title = title_template.format(str_sig = sample_name_dict[sample_names[i]], str_cic = cicada_names_print[k])
                titleObj = createLabel()
                titleObj.DrawLatex(0.1, 0.93, title)

                # plot point for l1 unprescaled efficiency
                l1_eff_s = getL1UnprescaledEfficiency(h_s)
                l1_eff_zb = getL1UnprescaledEfficiency(h_zb)
                print("L1 Unprescaled Signal Efficiency = ", l1_eff_s)
                print("L1 Unprescaled Bkg Efficiency = ", l1_eff_zb)
                g_l1 = ROOT.TGraph(1, array('d', [l1_eff_zb]), array('d', [l1_eff_s]))
                g_l1.SetMarkerSize(1)
                g_l1.SetMarkerStyle(20)
                g_l1.GetXaxis().SetRangeUser(0, max_eff_val_x)
                g_l1.GetYaxis().SetRangeUser(0, max_eff_val_y)
                g_l1.Draw("P same")

                ht_eff_s = getHTEfficiency(h_s)
                ht_eff_zb = getHTEfficiency(h_zb)
                print("HT>200 Signal Efficiency = ", ht_eff_s)
                print("HT>200 Bkg Efficiency = ", ht_eff_zb)
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
                g_or.Draw("AP")

                # draw TGraph for CICADA score
                g_cicada = createROCTGraph(tpr_cicada,
                                           fpr_cicada,
                                           color = 8,
                                           markerstyle = 21,
                                           first = False)
                g_cicada.Draw("P same")

                # draw graph title
                title_template = "#splitline{{Signal = {str_sig}}}{{CICADA Version = {str_cic}}}"
                title = title_template.format(str_sig = sample_name_dict[sample_names[i]], str_cic = cicada_names_print[k])
                titleObj = createLabel()
                titleObj.DrawLatex(0.1, 0.93, title)

                # plot point for l1 unprescaled efficiency
                l1_eff_s = getL1UnprescaledEfficiency(h_s)
                l1_eff_zb = getL1UnprescaledEfficiency(h_zb)
                print("L1 Unprescaled Signal Efficiency = ", l1_eff_s)
                print("L1 Unprescaled Bkg Efficiency = ", l1_eff_zb)
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
                legend.AddEntry(g_l1, "Unprescaled Trigger Efficiency", "p")
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

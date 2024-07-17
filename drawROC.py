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
from plottingUtils import convertCICADANametoPrint, createLabel, calculateROC, calculateROCPt, calculateROCOR, createROCTGraph, getL1UnprescaledEfficiency, getHTEfficiency, getAcceptRatioHist
import json
import re

with open('plottingOptions.json') as f:
    options = json.load(f)

def findClosestY(graph, x_point):
    n_points = graph.GetN()
    x_values = np.array(graph.GetX())
    y_values = np.array(graph.GetY())

    differences = np.abs(x_values - x_point)
    closest_index = np.argmin(differences)

    return y_values[closest_index]


########################################################################
# creates a rate plot for HT from the file f_bkg which has events from
# background sample bkg_name and saves the plot to out_dir
def plotRateHT(f_bkg, out_dir, bkg_name):
    print("Making rate plot for HT")

    # create ROOT canvas
    c = ROOT.TCanvas("c", "ROC", 1000, 800)

    # get score histogram from ZB file (cicada version doesn't matter
    # since we are integrating over that axis
    c_name = options["cicada_names"][0]
    if bkg_name == "ZeroBias":
        hist = f_bkg.Get(f"anomalyScore_ZeroBias_test_{c_name}")
    else:
        hist = f_bkg.Get(f"anomalyScore_{bkg_name}_{c_name}")

    # get accepted ratio histogram from above hist
    h = getAcceptRatioHist(hist, 1, hist_name = "HT")

    # plotting options
    h.SetTitle("")
    h.GetXaxis().SetTitle("HT Threshold [GeV]")
    h.GetYaxis().SetTitle("Zero Bias Rate [kHz]")
    h.GetXaxis().SetRangeUser(0,1000)
    h.GetYaxis().SetRangeUser(1e-1,1e5)
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

    return

########################################################################
# creates a Zero Bias rate plot for CICADA from the background histogram
# hist_bkg for the CICADA version cicada_name and save the plot to
# out_dir
def plotRateCICADA(hist_bkg, out_dir, cicada_name):
    print(f"Making rate plot for {cicada_name}")

    # create ROOT canvas
    c = ROOT.TCanvas("c", "ROC", 1000, 800)

    # get accepted ratio histogram from above hist
    h = getAcceptRatioHist(hist_bkg, 0, hist_name = cicada_name)

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
    c.SaveAs(f"{out_dir}/rate_ZeroBias_{cicada_name}.png")
    c.Close()

    return

########################################################################
# creates a ROC plot for (HT>ht_threshold or CICADA score>threshold)
# for the CICADA version cicada_name for signal samples listed in
# sample_shortlist and loaded from files with prefix file_prefix and the
# background histogram hist_bkg, which has events from background sample
# bkg_name and saves the plot to out_dir
def plotROCHTShortlist(hist_bkg, out_dir, bkg_name, sample_shortlist, cicada_name, file_prefix):
    print(f"Making ROC shortlist plot for (HT>ht_threshold or CICADA score>threshold) for {cicada_name} and background {bkg_name}")

    # create ROOT canvas
    c = ROOT.TCanvas("c", "ROC", 1000,800)
    # create legend object
    legend = ROOT.TLegend(-0.08,0.2,1.0,0.95)

    graphs = []
    for i in range(len(sample_shortlist)):

        print("    Current Sample = ", sample_shortlist[i])

        try:
            f_s = ROOT.TFile(f"{file_prefix}_{sample_shortlist[i]}.root")
        except Exception:
            print(f"    ROOT file for sample {sample_shortlist[i]} does not exist")
            continue

        # load histograms
        h_s = f_s.Get(f"anomalyScore_{sample_shortlist[i]}_{cicada_name}")

        # calcualte ROC for CICADA score > threshold OR HT > ht_threshold
        try:
            tpr_or_ht, fpr_or_ht = calculateROCOR(hist_bkg, h_s, options["ht_threshold"], 1)
        except ValueError as e:
            print("    Error:", e)


        # draw TGraph for HT OR CICADA score
        if i==0: first = True
        else: first = False
        g = createROCTGraph(tpr_or_ht,
                            fpr_or_ht,
                            color = ROOT.TColor.GetColor(options["shortlist_colors"][i]),
                            markerstyle = options["shortlist_markers"][i],
                            first = first,
                            bkg_name = convertCICADANametoPrint(bkg_name))
        graphs.append(g)

        # add legend entry for current sample
        legend.AddEntry(g,
            f"{sample_name_dict[sample_shortlist[i]]}",
            "CP")

    graphs[0].GetXaxis().SetRangeUser(0, options["ROC_x_max"])
    graphs[0].Draw("ACP")
    for i in range(1, len(sample_shortlist)): graphs[i].Draw("CP same")

    # draw cms label
    cmsLatex = createLabel()
    cmsLatex.DrawLatex(0.1,
                        0.92,
                        "#font[61]{CMS} #font[52]{Preliminary}")


    # set legend styling and draw
    legend.SetTextSize(0.035)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    #legend.Draw()

    # draw, save, and close canvas
    c.Draw()
    c.SaveAs(
        f"{out_dir}/ROC_HT_shortlist_{bkg_name}_{cicada_name}.png"
    )
    c.Close()

    return

########################################################################
# creates a ROC plot for (l1 unprescaled or CICADA score>threshold)
# for the CICADA version cicada_name for signal samples listed in
# sample_shortlist and loaded from files with prefix file_prefix and the
# background histogram hist_bkg, which has events from background sample
# bkg_name and saves the plot to out_dir
def plotROCL1Shortlist(hist_bkg, out_dir, bkg_name, sample_shortlist, cicada_name, file_prefix):
    print(f"Making ROC shortlist plot for (l1 unprescaled  or CICADA score>threshold) for {cicada_name} and background {bkg_name}")

    # create ROOT canvas
    c = ROOT.TCanvas("c", "ROC", 1000,800)

    # create legend object
    legend = ROOT.TLegend(-0.08,0.2,1.0,0.95)

    graphs = []
    for i in range(len(sample_shortlist)):

        try:
            f_s = ROOT.TFile(f"{file_prefix}_{sample_shortlist[i]}.root")
        except Exception:
            print(f"ROOT file for sample {sample_shortlist[i]} does not exist")
            continue

        # load histograms
        h_s = f_s.Get(f"anomalyScore_{sample_shortlist[i]}_{cicada_name}")

        # calcualte ROC for CICADA score > threshold OR L1 Trigger
        try:
            tpr_or_l1, fpr_or_l1 = calculateROCOR(hist_bkg, h_s, options["l1_threshold"], 2)
        except ValueError as e:
            print("Error:", e)


        # draw TGraph for HT OR CICADA score
        if i==0: first = True
        else: first = False
        g = createROCTGraph(tpr_or_l1,
                            fpr_or_l1,
                            color = ROOT.TColor.GetColor(options["shortlist_colors"][i]),
                            markerstyle = options["shortlist_markers"][i],
                            first = first,
                            bkg_name = convertCICADANametoPrint(bkg_name))

        graphs.append(g)

        # add legend entry for current sample
        legend.AddEntry(g,
            f"{sample_name_dict[sample_shortlist[i]]}",
            "CP")

    graphs[0].GetXaxis().SetRangeUser(0, options["ROC_x_max"])
    graphs[0].Draw("ACP")
    for i in range(1, len(sample_shortlist)): graphs[i].Draw("CP same")

    # draw cms label
    cmsLatex = createLabel()
    cmsLatex.DrawLatex(0.1,
                        0.92,
                        "#font[61]{CMS} #font[52]{Preliminary}")


    # set legend styling and draw
    legend.SetTextSize(0.035)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    #legend.Draw()

    # draw, save, and close canvas
    c.Draw()
    c.SaveAs(
        f"{out_dir}/ROC_L1_shortlist_{bkg_name}_{cicada_name}.png"
    )
    c.Close()

    return

def plotCombinedROC(hist_bkg, signal_list, file_prefix, c_name, out_dir, suffix):

    # create ROOT canvas
    canvas = ROOT.TCanvas("c", "ROC", 1000, 800)

    # Define TPads (pad2 for legend)
    pad1 = ROOT.TPad("pad1", "Pad 1", 0.0, 0.0, 0.65, 1.0)
    pad2 = ROOT.TPad("pad2", "Pad 2", 0.6, 0.0, 1.0, 1.0)

    # Draw the TPads on the canvas
    pad1.Draw()
    pad2.Draw()

    pad1.cd()

    tgraphs = []
    sig_files = []
    max_y = 0.0
    first = True

    for i in range(len(signal_list)):

        signal_index = options["sample_shortlist"].index(signal_list[i])
        signal_color = ROOT.TColor.GetColor(options["shortlist_colors"][signal_index])

        sig_files.append(ROOT.TFile(f"{file_prefix}_{signal_list[i]}.root"))

        # load histograms
        hist_sig = sig_files[-1].Get(f"anomalyScore_{signal_list[i]}_{c_name}")

        tpr_cicada, fpr_cicada = calculateROC(hist_bkg, hist_sig, 0)
        tpr_ht, fpr_ht = calculateROC(hist_bkg, hist_sig, 1)

        # get TGraph for CICADA
        g_cicada = createROCTGraph(tpr_cicada,
                                   fpr_cicada,
                                   color = signal_color,
                                   linestyle = 1,
                                   linewidth = 2,
                                   first = first)

        if first:
            g_cicada.GetXaxis().SetRangeUser(0, options["ROC_x_max"] * options["rate_scale_factor"])
        max_cicada = findClosestY(g_cicada, options["ROC_x_max"] * options["rate_scale_factor"])
        tgraphs.append(g_cicada)

        first = False

        # get TGraph for HT
        g_ht = createROCTGraph(tpr_ht,
                               fpr_ht,
                               color = signal_color,
                               linestyle = 7,
                               linewidth = 2,
                               first = first)

        max_ht = findClosestY(g_ht, options["ROC_x_max"] * options["rate_scale_factor"])
        tgraphs.append(g_ht)

        max_y = max(max_y, max(max_cicada, max_ht))

    tgraphs[0].GetYaxis().SetRangeUser(0, 1.15*max_y)
    tgraphs[0].Draw("AC")
    for i in range(1, len(tgraphs)):
        tgraphs[i].Draw("C same")

    # draw cms label
    cmsLatex = createLabel()
    cmsLatex.DrawLatex(0.1,
                       0.92,
                       "#font[61]{CMS} #font[52]{Preliminary}")

    canvas.cd()

    # create legend
    pad2.cd()
    legend = ROOT.TLegend(0.0, 0.4, 0.9, 0.9)
    for i in range(0, int(len(tgraphs)/2)):
        name = re.sub("[\(\[].*?[\)\]]", "", sample_name_dict[signal_list[i]])
        name2 = name + " CICADA ROC"
        legend.AddEntry(tgraphs[2*i], name2, "l")
        name2 = name + " HT ROC"
        legend.AddEntry(tgraphs[2*i+1], name2, "l")

    legend.SetTextSize(0.04)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.Draw()

    canvas.SaveAs(f"{out_dir}/ROC_CICADA_HT_combined_{c_name}_{suffix}.pdf")

    for i in range(len(sig_files)):
        sig_files[i].Close()

    return

########################################################################
# creates a ROC plot for (ht>threshold or CICADA score>threshold)
# for the CICADA version cicada_name for signal sample sample_name from
# events from background bkg_name. Uses background histogram hist_bkg
# and signal histogram hist_sig. Takes in precalculated TPR and FPR
# arrays for the OR ROC (fpr_or_ht, tpr_or_ht), cicada (tpr_cicada,
# fpr_cicada), and ht (tpr_ht, fpr_ht). Saves plots to out_dir
def plotHTOR(hist_sig, hist_bkg,
             fpr_or_ht, tpr_or_ht, tpr_cicada, fpr_cicada, tpr_ht, fpr_ht, tpr_pt, fpr_pt,
             out_dir, bkg_name, cicada_name, sample_name,
             logx = False, logy = False):

    # determine axis limits based on whether axis is log scale
    if logx: min_x = options["ROC_x_min_log"]
    else: min_x = 0

    if logy: min_y = options["ROC_y_min_log"]
    else: min_y = 0

    # create ROOT canvas
    c = ROOT.TCanvas("c", "ROC", 1000, 800)

    # get TGraph for HT OR CICADA score
    g_or = createROCTGraph(tpr_or_ht,
                           fpr_or_ht,
                           color = 6,
                           markerstyle = 20,
                           first = True,
                           bkg_name = sample_name_dict[bkg_name],
                           logx = logx,
                           logy = logy)
    g_or.GetXaxis().SetRangeUser(min_x * options["rate_scale_factor"], options["ROC_x_max"] * options["rate_scale_factor"])

    # get TGraph for CICADA score
    g_cicada = createROCTGraph(tpr_cicada,
                               fpr_cicada,
                               color = 8,
                               markerstyle = 21,
                               first = False,
                               logx = logx,
                               logy = logy)

    # get TGraph for HT
    g_ht = createROCTGraph(tpr_ht,
                           fpr_ht,
                           color = 9,
                           markerstyle = 22,
                           first = False,
                           logx = logx,
                           logy = logy)

    # get TGraph for jet pT
    g_pt = createROCTGraph(tpr_pt,
                           fpr_pt,
                           color = 2,
                           markerstyle = 23,
                           first = False,
                           logx = logx,
                           logy = logy)

    # set y max and draw graphs
    max_or = findClosestY(g_or, options["ROC_x_max"] * options["rate_scale_factor"])
    max_cicada = findClosestY(g_cicada, options["ROC_x_max"] * options["rate_scale_factor"])
    max_ht = findClosestY(g_ht, options["ROC_x_max"] * options["rate_scale_factor"])
    max_pt = findClosestY(g_pt, options["ROC_x_max"] * options["rate_scale_factor"])
    max_all = max(max(max_or, max_cicada), max(max_ht, max_pt))
    g_or.GetYaxis().SetRangeUser(0, 1.5*max_all)
    g_or.Draw("AC")
    g_cicada.Draw("C same")
    g_ht.Draw("C same")
    g_pt.Draw("C same")

    # draw graph title
    title_template = "Signal = {str_sig}"
    title = title_template.format(str_sig = sample_name_dict[sample_name])#, str_cic = convertCICADANametoPrint(cicada_name))
    titleObj = createLabel()
    titleObj.DrawLatex(0.13, 0.85, title)

    # draw cms label
    cmsLatex = createLabel()
    cmsLatex.DrawLatex(0.1,
                       0.93,
                       "#font[61]{CMS} #font[52]{Preliminary}")

    # plot point for l1 unprescaled efficiency
    l1_eff_s = getL1UnprescaledEfficiency(hist_sig)
    l1_eff_zb = getL1UnprescaledEfficiency(hist_bkg)
    print("    L1 Unprescaled Signal (Number Accepted)/(Total) = ", l1_eff_s)
    print("    L1 Unprescaled Bkg (Number Accepted)/(Total) = ", l1_eff_zb)
    print("    L1 Unprescaled Bkg Rate = ", l1_eff_zb * options["rate_scale_factor"])

    g_l1 = ROOT.TGraph(1, array('d', [l1_eff_zb * options["rate_scale_factor"]]), array('d', [l1_eff_s]))
    g_l1.SetMarkerSize(1.5)
    g_l1.SetMarkerStyle(20)
    g_l1.GetXaxis().SetRangeUser(min_x * options["rate_scale_factor"], options["ROC_x_max"] * options["rate_scale_factor"])
    g_l1.GetYaxis().SetRangeUser(min_y, options["ROC_y_max"])
    g_l1.Draw("P same")

    # plot point for HT>ht_threshold
    ht_eff_s = getHTEfficiency(hist_sig)
    ht_eff_zb = getHTEfficiency(hist_bkg)
    print("    HT>threshold Signal (Number Accepted)/(Total) = ", ht_eff_s)
    print("    HT>threshold Bkg (Number Accepted)/(Total) = ", ht_eff_zb)
    print("    HT>threshold Bkg Rate = ", ht_eff_zb * options["rate_scale_factor"])
    g_ht_point = ROOT.TGraph(1, array('d', [ht_eff_zb * options["rate_scale_factor"]]), array('d', [ht_eff_s]))
    g_ht_point.SetMarkerSize(1.5)
    g_ht_point.SetMarkerColor(9)
    g_ht_point.SetMarkerStyle(20)
    g_ht_point.GetXaxis().SetRangeUser(min_x * options["rate_scale_factor"], options["ROC_x_max"] * options["rate_scale_factor"])
    g_ht_point.GetYaxis().SetRangeUser(min_y, options["ROC_y_max"])
    g_ht_point.Draw("P same")

    # draw legends
    legend = ROOT.TLegend(0.1, 0.7, 0.85, 0.85)
    legend_str = "(CICADA > Threshold) or (HT > " + str(options["ht_threshold"]) + ") "
    legend.AddEntry(g_or, legend_str, "l")
    legend.AddEntry(g_cicada, "CICADA > Threshold", "l")
    legend.AddEntry(g_ht, "HT > Threshold", "l")
    legend.AddEntry(g_pt, "Jet PT > Threshold", "l")
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetTextSize(0.022)
    legend.Draw()

    legend2 = ROOT.TLegend(0.56, 0.77, 0.85, 0.85)
    legend2.AddEntry(g_l1, "Unprescaled Trigger", "p")
    legend2_str = "HT > " + str(options["ht_threshold"])
    legend2.AddEntry(g_ht_point, legend_str, "p")
    legend2.SetBorderSize(0)
    legend2.SetFillStyle(0)
    legend2.SetTextSize(0.023)
    legend2.Draw()

    extra_name = ""
    if logx: extra_name += "_logx"
    if logy: extra_name += "_logy"

    # draw canvas and save plot
    c.Update()
    c.Draw()
    c.SaveAs(f"{out_dir}/ROC_HT{extra_name}_{bkg_name}_{cicada_name}_{sample_name}.png")
    c.Close()

    return

########################################################################
# creates a ROC plot for (l1 unprescaled or CICADA score>threshold)
# for the CICADA version cicada_name for signal sample sample_name from
# events from background bkg_name. Uses background histogram hist_bkg
# and signal histogram hist_sig. Takes in precalculated TPR and FPR
# arrays for the OR ROC (fpr_or_l1, tpr_or_l1), and cicada (tpr_cicada,
# fpr_cicada). Saves plots to out_dir
def plotL1OR(hist_sig, hist_bkg,
             fpr_or_l1, tpr_or_l1, tpr_cicada, fpr_cicada,
             out_dir, bkg_name, cicada_name, sample_name, logx=False, logy=False):

    # determine axis limits based on whether axis is log scale
    if logx: min_x = options["ROC_x_min_log"]
    else: min_x = 0

    if logy: min_y = options["ROC_y_min_log"]
    else: min_y = 0

    # create ROOT canvas
    c = ROOT.TCanvas("c", "ROC", 1000, 800)

    # draw TGraph for L1 OR CICADA score
    g_or = createROCTGraph(tpr_or_l1,
                           fpr_or_l1,
                           color = 6,
                           markerstyle = 20,
                           first = True,
                           bkg_name = convertCICADANametoPrint(bkg_name),
                           logx = logx,
                           logy = logy)
    g_or.GetXaxis().SetRangeUser(0, options["ROC_x_max"] * options["rate_scale_factor"])

    # draw TGraph for CICADA score
    g_cicada = createROCTGraph(tpr_cicada,
                               fpr_cicada,
                               color = 8,
                               markerstyle = 21,
                               first = False,
                               logx = logx,
                               logy = logy)

    max_or = findClosestY(g_or, options["ROC_x_max"] * options["rate_scale_factor"])
    max_cicada = findClosestY(g_cicada, options["ROC_x_max"] * options["rate_scale_factor"])
    max_all = max(max_or, max_cicada)
    g_or.GetYaxis().SetRangeUser(0, 1.5*max_all)
    g_or.Draw("AC")
    g_cicada.Draw("C same")

    # draw graph title
    title_template = "#splitline{{Signal = {str_sig}}}{{CICADA Version = {str_cic}}}"
    title = title_template.format(str_sig = sample_name_dict[sample_name], str_cic = convertCICADANametoPrint(cicada_name))
    titleObj = createLabel()

    # draw cms label
    cmsLatex = createLabel()
    cmsLatex.DrawLatex(0.1,
                       0.93,
                       "#font[61]{CMS} #font[52]{Preliminary}")

    # plot point for l1 unprescaled efficiency
    l1_eff_s = getL1UnprescaledEfficiency(hist_sig)
    l1_eff_zb = getL1UnprescaledEfficiency(hist_bkg)
    print("    L1 Unprescaled Signal (Number Accepted)/(Total) = ", l1_eff_s)
    print("    L1 Unprescaled Bkg (Number Accepted)/(Total) = ", l1_eff_zb)
    print("    L1 Unprescaled Bkg Rate = ", l1_eff_zb * options["rate_scale_factor"])

    g_l1 = ROOT.TGraph(1, array('d', [l1_eff_zb * options["rate_scale_factor"]]), array('d', [l1_eff_s]))
    g_l1.SetMarkerSize(1)
    g_l1.SetMarkerStyle(20)
    g_l1.GetXaxis().SetRangeUser(min_x * options["rate_scale_factor"], options["ROC_x_max"] * options["rate_scale_factor"])
    g_l1.GetYaxis().SetRangeUser(min_y, options["ROC_y_max"])
    g_l1.Draw("P same")

    # draw legend
    legend = ROOT.TLegend(0.1, 0.7, 0.85, 0.8)
    legend.AddEntry(g_or, "(CICADA > Threshold) or (Passed an Unprescaled L1 Trigger)", "p")
    legend.AddEntry(g_cicada, "CICADA > Threshold", "l")
    legend.AddEntry(g_l1, "Unprescaled Trigger", "p")
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetTextSize(0.025)
    legend.Draw()

    extra_name = ""
    if logx: extra_name += "_logx"
    if logy: extra_name += "_logy"

    # draw canvas and save plot
    c.Update()
    c.Draw()
    c.SaveAs(f"{out_dir}/ROC_L1{extra_name}_{bkg_name}_{cicada_name}_{sample_name}.png")
    c.Close()

    return

########################################################################
# creates OR ROC plots for the CICADA version cicada_name for signal
# sample sample_name from events from background bkg_name. Uses
# background histogram hist_bkg and signal histogram hist_sig. Saves
# plots to out_dir
def createIndividualROCPlots(hist_bkg, hist_sig, hist_bkg_pt, hist_sig_pt, out_dir, bkg_name, cicada_name, sample_name):

    print(f"Creating ROC plots for sample {sample_name}")

    # calculate simple ROC for CICADA score and HT
    tpr_cicada, fpr_cicada = calculateROC(hist_bkg, hist_sig, 0)
    tpr_ht, fpr_ht = calculateROC(hist_bkg, hist_sig, 1)
    tpr_pt, fpr_pt = calculateROCPt(hist_bkg_pt, hist_sig_pt)

    # calculate ROC for CICADA score > threshold OR HT > ht_threshold
    try:
        tpr_or_ht, fpr_or_ht = calculateROCOR(hist_bkg, hist_sig, options["ht_threshold"], 1)
    except ValueError as e:
        print("Error:", e)

    # calcualte ROC for CICADA score > threshold OR L1 Unprescaled Trigger
    try:
        tpr_or_l1, fpr_or_l1 = calculateROCOR(hist_bkg, hist_sig, options["l1_threshold"], 2)
    except ValueError as e:
        print("Error:", e)

    # plot ROC for CICADA score > threshold OR HT > ht_threshold
    plotHTOR(hist_sig, hist_bkg,
             fpr_or_ht, tpr_or_ht, tpr_cicada, fpr_cicada, tpr_ht, fpr_ht, tpr_pt, fpr_pt,
             out_dir, bkg_name, cicada_name, sample_name)
    #plotHTOR(hist_sig, hist_bkg,
             #fpr_or_ht, tpr_or_ht, tpr_cicada, fpr_cicada, tpr_ht, fpr_ht, tpr_pt, fpr_pt,
             #out_dir, bkg_name, cicada_name, sample_name, logx=True)
    #plotHTOR(hist_sig, hist_bkg,
             #fpr_or_ht, tpr_or_ht, tpr_cicada, fpr_cicada, tpr_ht, fpr_ht, tpr_pt, fpr_pt,
             #out_dir, bkg_name, cicada_name, sample_name, logx=True, logy=True)

    # plot ROC for CICADA score > threshold OR L1 Trigger
    plotL1OR(hist_sig, hist_bkg,
             fpr_or_l1, tpr_or_l1, tpr_cicada, fpr_cicada,
             out_dir, bkg_name, cicada_name, sample_name)
    #plotL1OR(hist_sig, hist_bkg,
             #fpr_or_l1, tpr_or_l1, tpr_cicada, fpr_cicada,
             #out_dir, bkg_name, cicada_name, sample_name, logx=True)
    #plotL1OR(hist_sig, hist_bkg,
             #fpr_or_l1, tpr_or_l1, tpr_cicada, fpr_cicada,
             #out_dir, bkg_name, cicada_name, sample_name, logx=True, logy=True)



    return



########################################################################
def main(file_prefix, out_dir):

    print("Loading bkg files ...")

    # grab background files
    f_zb = ROOT.TFile(f"{file_prefix}_ZeroBias.root")
    f_sn = ROOT.TFile(f"{file_prefix}_SingleNeutrino_E-10-gun.root")
    f_bkg = [f_zb, f_sn]

    # names and associated print names of backgrounds
    bkg_names = ["ZeroBias", "SingleNeutrino_E-10-gun"]

    # get rate plot for HT
    plotRateHT(f_bkg[0], out_dir, bkg_names[0])

    # get list of sample names
    sample_names = list(sample_name_dict.keys())

    # iterate through backgrounds
    for l in range(len(f_bkg)):
        # iterate through CICADA versions
        for k in range(len(options["cicada_names"])):

            c_name = options["cicada_names"][k]

            # load ZeroBias histograms
            if bkg_names[l]=="ZeroBias":
                h_zb = f_bkg[l].Get(f"anomalyScore_ZeroBias_test_{c_name}")
                h_zb_pt = f_bkg[l].Get(f"jetEt_ZeroBias_test_{c_name}")
            else:
                h_zb = f_bkg[l].Get(f"anomalyScore_SingleNeutrino_E-10-gun_{c_name}")
                h_zb_pt = f_bkg[l].Get(f"jetEt_SingleNeutrino_E-10-gun_{c_name}")

            # combined ROC plots
            plotCombinedROC(h_zb, options["samples_loweff"], file_prefix, c_name, out_dir, "low")
            plotCombinedROC(h_zb, options["samples_higheff"], file_prefix, c_name, out_dir, "high")

            # get rate plot for current CICADA version
            if bkg_names[l]=="ZeroBias":
                plotRateCICADA(h_zb, out_dir, c_name)

            # combined shortlist plot for HT or CICADA
            #plotROCHTShortlist(h_zb, out_dir, bkg_names[l], options["sample_shortlist"], c_name, file_prefix)
            # combined shortlist plot for L1 or CICADA
            #plotROCL1Shortlist(h_zb, out_dir, bkg_names[l], options["sample_shortlist"], c_name, file_prefix)

            # individual plots for signal samples
            for i in range(len(sample_names)):

                # skip over the samples that are not signal
                if sample_names[i]=="ZeroBias": continue
                if sample_names[i]=="SingleNeutrino_E-10-gun": continue

                print(sample_names[i])

                # try to open signal file, skip signal if failed
                try:
                    f_s = ROOT.TFile(f"{file_prefix}_{sample_names[i]}.root")
                except Exception:
                    print(f"ROOT file for sample {sample_names[i]} does not exist")
                    continue

                # load histograms
                h_s = f_s.Get(f"anomalyScore_{sample_names[i]}_{c_name}")
                h_s_pt = f_s.Get(f"jetEt_{sample_names[i]}_{c_name}")

                # plot ROCs
                createIndividualROCPlots(h_zb, h_s, h_zb_pt, h_s_pt, out_dir, bkg_names[l], c_name, sample_names[i])





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

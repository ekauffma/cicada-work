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
from plottingUtils import convertCICADANametoPrint, createLabel, calculateROC, calculateROCOR, createROCTGraph, getL1UnprescaledEfficiency, getHTEfficiency, getAcceptRatioHist
import json

with open('plottingOptions.json') as f:
    options = json.load(f)

########################################################################
def main(file_prefix, out_dir):

    print("Loading bkg files ...")

    # grab background files
    f_zb = ROOT.TFile(f"{file_prefix}_ZeroBias.root")
    f_sn = ROOT.TFile(f"{file_prefix}_SingleNeutrino_E-10-gun.root")
    f_bkg = [f_zb, f_sn]

    # names and associated print names of backgrounds
    bkg_names = ["ZeroBias", "SingleNeutrino_E-10-gun"]


    ####################################################################
    # get rate plot for HT                                             #
    ####################################################################

    print("Making rate plot for HT")

    # create ROOT canvas
    c = ROOT.TCanvas("c", "ROC", 1000, 800)

    # get score histogram from ZB file (cicada version doesn't matter
    # since we are integrating over that axis
    c_name = options["cicada_names"][0]
    hist = f_bkg[0].Get(f"anomalyScore_ZeroBias_test_{c_name}")

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


    ####################################################################

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
            else:
                h_zb = f_bkg[l].Get(f"anomalyScore_SingleNeutrino_E-10-gun_{c_name}")


            ############################################################
            # get rate plot for current CICADA version                 #
            ############################################################

            if bkg_names[l]=="ZeroBias":
                # create ROOT canvas
                c = ROOT.TCanvas("c", "ROC", 1000, 800)

                # get accepted ratio histogram from above hist
                h = getAcceptRatioHist(h_zb, 0, hist_name = c_name)

                # scale by rate factor
                #h.Scale(rate_scale_factor)

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
                c.SaveAs(f"{out_dir}/rate_ZeroBias_{c_name}.png")
                c.Close()
                
            ############################################################
            # combined shortlist plots                                 #
            ############################################################
            
            # create ROOT canvas
            c = ROOT.TCanvas("c", "ROC", 1000,800)
            # create legend object
            legend = ROOT.TLegend(-0.08,0.2,1.0,0.95)
            
            graphs = []
            
            sample_shortlist = options["sample_shortlist"]
            for i in range(len(sample_shortlist)):
            
                try:
                    f_s = ROOT.TFile(f"{file_prefix}_{sample_shortlist[i]}.root")
                except Exception:
                    print(f"ROOT file for sample {sample_shortlist[i]} does not exist")
                    continue
                    
                # load histograms
                h_s = f_s.Get(f"anomalyScore_{sample_shortlist[i]}_{c_name}")

                # calcualte ROC for CICADA score > threshold OR HT > 200
                try:
                    tpr_or_ht, fpr_or_ht = calculateROCOR(h_zb, h_s, options["ht_threshold"], 1)
                except ValueError as e:
                    print("Error:", e)
                    
                
                # draw TGraph for HT OR CICADA score
                if i==0: first = True
                else: first = False
                g = createROCTGraph(tpr_or_ht,
                                    fpr_or_ht,
                                    color = options["shortlist_colors"][i],
                                    markerstyle = options["shortlist_markers"][i],
                                    first = first,
                                    bkg_name = convertCICADANametoPrint(bkg_names[l]))
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
                f"{out_dir}/ROC_HT_shortlist_{bkg_names[l]}_{c_name}.png"
            )
            c.Close()
            
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
                h_s = f_s.Get(f"anomalyScore_{sample_shortlist[i]}_{c_name}")

                # calcualte ROC for CICADA score > threshold OR HT > 200
                try:
                    tpr_or_l1, fpr_or_l1 = calculateROCOR(h_zb, h_s, options["l1_threshold"], 2)
                except ValueError as e:
                    print("Error:", e)
                    
                
                # draw TGraph for HT OR CICADA score
                if i==0: first = True
                else: first = False
                g = createROCTGraph(tpr_or_l1,
                                    fpr_or_l1,
                                    color = options["shortlist_colors"][i],
                                    markerstyle = options["shortlist_markers"][i],
                                    first = first,
                                    bkg_name = convertCICADANametoPrint(bkg_names[l]))
                                    
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
                f"{out_dir}/ROC_L1_shortlist_{bkg_names[l]}_{c_name}.png"
            )
            c.Close()
                
                
                

            ############################################################
            # individual plots for signal samples                      #
            ############################################################
            for i in range(len(sample_names)):
            
                # skip over the samples that are not signal
                if sample_names[i]=="ZeroBias": continue
                if sample_names[i]=="SingleNeutrino_E-10-gun": continue

                # for testing, only making one plot
                #if sample_names[i]!="TT_TuneCP5_13p6TeV_powheg-pythia8": continue

                print(sample_names[i])

                # try to open signal file, skip signal if failed
                try:
                    f_s = ROOT.TFile(f"{file_prefix}_{sample_names[i]}.root")
                except Exception:
                    print(f"ROOT file for sample {sample_names[i]} does not exist")
                    continue

                # load histograms
                h_s = f_s.Get(f"anomalyScore_{sample_names[i]}_{c_name}")

                # calculate simple ROC for CICADA score and HT
                tpr_cicada, fpr_cicada = calculateROC(h_zb, h_s, 0)
                tpr_ht, fpr_ht = calculateROC(h_zb, h_s, 1)

                # calcualte ROC for CICADA score > threshold OR HT > 200
                try:
                    tpr_or_ht, fpr_or_ht = calculateROCOR(h_zb, h_s, options["ht_threshold"], 1)
                except ValueError as e:
                    print("Error:", e)

                # calcualte ROC for CICADA score > threshold OR L1 Unprescaled Trigger
                try:
                    tpr_or_l1, fpr_or_l1 = calculateROCOR(h_zb, h_s, options["l1_threshold"], 2)
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
                                       bkg_name = convertCICADANametoPrint(bkg_names[l]))
                g_or.GetXaxis().SetRangeUser(0, options["ROC_x_max"])
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
                title = title_template.format(str_sig = sample_name_dict[sample_names[i]], str_cic = convertCICADANametoPrint(c_name))
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
                g_l1.GetXaxis().SetRangeUser(0, options["ROC_x_max"])
                g_l1.GetYaxis().SetRangeUser(0, options["ROC_y_max"])
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
                g_ht_point.GetXaxis().SetRangeUser(0, options["ROC_x_max"])
                g_ht_point.GetYaxis().SetRangeUser(0, options["ROC_y_max"])
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
                c.SaveAs(f"{out_dir}/ROC_HT_{bkg_names[l]}_{c_name}_{sample_names[i]}.png")
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
                                       bkg_name = convertCICADANametoPrint(bkg_names[l]))
                g_or.GetXaxis().SetRangeUser(0, options["ROC_x_max"])
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
                title = title_template.format(str_sig = sample_name_dict[sample_names[i]], str_cic = convertCICADANametoPrint(c_name))
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
                g_l1.GetXaxis().SetRangeUser(0, options["ROC_x_max"])
                g_l1.GetYaxis().SetRangeUser(0, options["ROC_y_max"])
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
                c.SaveAs(f"{out_dir}/ROC_L1_{bkg_names[l]}_{c_name}_{sample_names[i]}.png")
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

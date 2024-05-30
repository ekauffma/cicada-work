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

max_eff_val = 0.00344054
rate_scale_factor = 2544.0 * 11245e-3

# names of CICADA models
cicada_names = ["CICADA_v1p2p2",
                "CICADA_v2p2p2",
                "CICADA_v1p2p2N",
                "CICADA_v2p2p2N"]

# function for drawing the CMS label on the plots
def createCMSLabel():
    cmsLatex = ROOT.TLatex()
    cmsLatex.SetTextSize(0.04)
    cmsLatex.SetNDC(True)
    cmsLatex.SetTextAlign(11)

    return cmsLatex

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

            # get integral of ZeroBias histograms
            integral_zb = float(h_zb.Integral(1, h_zb.GetNbinsX()+1, 1, h_zb.GetNbinsY()+1))

            sample_names = list(sample_name_dict.keys())
            for i in range(len(sample_names)):

                if sample_names[i]=="ZeroBias": continue
                if sample_names[i]=="SingleNeutrino_E-10-gun": continue
                if sample_names[i]=="HHHTo6B_c3_0_d4_0_TuneCP5_13p6TeV_amcatnlo-pythia8": continue
                if sample_names[i]=="HHHto4B2Tau_c3-0_d4-0_TuneCP5_13p6TeV_amcatnlo-pythia8": continue

                print(sample_names[i])

                try:
                    f_s = ROOT.TFile(f"{file_prefix}_{sample_names[i]}.root")
                except Exception:
                    print(f"ROOT file for sample {sample_names[i]} does not exist")
                    continue

                # load histograms
                h_s = f_s.Get(f"anomalyScore_{sample_names[i]}_{cicada_names[k]}")

                # get integral of each histogram
                integral_s = float(h_s.Integral(1, h_s.GetNbinsX()+1, 1, h_s.GetNbinsY()+1))

                # initialize lists for tpr and fpr
                tpr_or = []
                fpr_or = []
                tpr_cicada = []
                fpr_cicada = []
                tpr_ht = []
                fpr_ht = []

                # iterate through bins and compute tpr and fpr for each threshold
                for j in range(h_zb.GetNbinsX()):
                    # compute partial sums of histograms
                    partial_or_s = float(h_s.Integral(j+1, h_s.GetNbinsX()+1, 2, h_s.GetNbinsY()+1))
                    partial_or_zb = float(h_zb.Integral(j+1, h_zb.GetNbinsX()+1, 2, h_zb.GetNbinsY()+1))
                    partial_cicada_s = float(h_s.Integral(j+1, h_s.GetNbinsX()+1, 1, h_s.GetNbinsY()+1))
                    partial_cicada_zb = float(h_zb.Integral(j+1, h_zb.GetNbinsX()+1, 1, h_zb.GetNbinsY()+1))
                    partial_ht_s = float(h_s.Integral(1, h_s.GetNbinsX()+1, j+1, h_s.GetNbinsY()+1))
                    partial_ht_zb = float(h_zb.Integral(1, h_zb.GetNbinsX()+1, j+1, h_zb.GetNbinsY()+1))

                    tpr_or_current = partial_or_s/integral_s
                    fpr_or_current = partial_or_zb/integral_zb
                    tpr_cicada_current = partial_cicada_s/integral_s
                    fpr_cicada_current = partial_cicada_zb/integral_zb
                    tpr_ht_current = partial_ht_s/integral_s
                    fpr_ht_current = partial_ht_zb/integral_zb

                    tpr_or.append(tpr_or_current)
                    fpr_or.append(fpr_or_current * rate_scale_factor)
                    tpr_cicada.append(tpr_cicada_current)
                    fpr_cicada.append(fpr_cicada_current * rate_scale_factor)
                    tpr_ht.append(tpr_ht_current)
                    fpr_ht.append(fpr_ht_current * rate_scale_factor)

                print("Efficiencies = ", tpr_or)
                print("Zero Bias Rates = ", fpr_or)

                # convert to array for some reason
                tpr_or = array('d', tpr_or)
                fpr_or = array('d', fpr_or)
                tpr_cicada = array('d', tpr_cicada)
                fpr_cicada = array('d', fpr_cicada)
                tpr_ht = array('d', tpr_ht)
                fpr_ht = array('d', fpr_ht)

                # create ROOT canvas
                c = ROOT.TCanvas("c", "ROC", 1000, 800)

                # create TGraph
                g = ROOT.TGraph(len(tpr_or), fpr_or, tpr_or)

                # plotting options for cicada graph
                title_template = "#splitline{{Signal = {str_sig}}}{{CICADA Version = {str_cic}}}"
                title = title_template.format(str_sig = sample_name_dict[sample_names[i]], str_cic = cicada_names[k])
                #pavetext = ROOT.TPaveText(0.1, 0.93, 0.9, 0.98, "NDC")
                #pavetext.AddText(title)
                #pavetext.SetTextSize(0.05)
                #pavetext.SetFillColor(0)
                #pavetext.Draw()


                g.SetTitle(title)
                g.SetLineWidth(4)
                g.SetLineColor(6)
                g.GetXaxis().SetTitle(f"{bkg_names_print[l]} Rate [kHz]")
                g.GetYaxis().SetTitle("Signal Efficiency")
                g.GetXaxis().SetRangeUser(0,max_eff_val*rate_scale_factor)
                g.GetYaxis().SetRangeUser(0,1.2)

                # draw cicada TGraph
                g.Draw("AC")

                # create and draw TGraph for CICADA
                g_cicada = ROOT.TGraph(len(tpr_cicada), fpr_cicada, tpr_cicada)
                g_cicada.SetLineWidth(4)
                g_cicada.SetLineColor(8)
                g_cicada.GetXaxis().SetRangeUser(0,max_eff_val*rate_scale_factor)
                g_cicada.GetYaxis().SetRangeUser(0,1.2)
                g_cicada.Draw("C same")


                # create and draw TGraph for HT
                g_ht = ROOT.TGraph(1, fpr_ht[1:2], tpr_ht[1:2])
                #g_ht.SetLineWidth(4)
                g_ht.SetMarkerColor(9)
                g_ht.SetMarkerSize(1)
                g_ht.SetMarkerStyle(21)
                g_ht.GetXaxis().SetRangeUser(0,max_eff_val*rate_scale_factor)
                g_ht.GetYaxis().SetRangeUser(0,1.2)
                g_ht.Draw("P same")


                if sample_names[i] in efficiencies:
                    g_l1 = ROOT.TGraph(1, array('d', [rate_scale_factor * efficiencies[bkg_names[l]]]), array('d', [efficiencies[sample_names[i]]]))
                    g_l1.SetMarkerSize(1)
                    g_l1.SetMarkerStyle(20)
                    g_l1.GetXaxis().SetRangeUser(0, max_eff_val*rate_scale_factor)
                    g_l1.GetYaxis().SetRangeUser(0,1.2)
                    g_l1.Draw("P same")

                legend = ROOT.TLegend(0.1,0.77,0.9, 0.9)
                legend.AddEntry(g, "(CICADA > Threshold) or (HT > 200) ")
                legend.AddEntry(g_cicada, "CICADA > Threshold")
                legend.AddEntry(g_ht, "HT > 200")
                if sample_names[i] in efficiencies:
                    legend.AddEntry(g_l1, "Unprescaled Trigger Efficiency", "p")
                legend.SetBorderSize(0)
                legend.SetFillStyle(0)
                legend.SetTextSize(0.025)
                legend.Draw()

                # draw canvas and save plot
                c.Update()
                c.Draw()
                c.SaveAs(f"{out_dir}/ROC_allcurves_{bkg_names[l]}_{cicada_names[k]}_{sample_names[i]}.png")
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

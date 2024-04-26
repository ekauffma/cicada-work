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

    for k in range(len(cicada_names)):

        # load ZeroBias histograms
        h_cicada_zb = f_zb.Get(f"anomalyScore_ZeroBias_test_{cicada_names[k]}")
        h_ht_zb = f_zb.Get(f"HT_ZeroBias_test")

        # get integral of ZeroBias histograms
        integral_cicada_zb = float(h_cicada_zb.Integral(1, h_cicada_zb.GetNbinsX()+1))
        integral_ht_zb = float(h_ht_zb.Integral(1, h_ht_zb.GetNbinsX()+1))

        sample_names = list(sample_name_dict.keys())
        for i in range(len(sample_names)):


            f_s = ROOT.TFile(f"{file_prefix}_{sample_names[i]}.root")

            # load histograms
            h_cicada_s = f_s.Get(f"anomalyScore_{sample_names[i]}_{cicada_names[k]}")
            h_ht_s = f_s.Get(f"HT_{sample_names[i]}")

            # get integral of each histogram
            integral_cicada_s = float(h_cicada_s.Integral(1, h_cicada_s.GetNbinsX()+1))
            integral_ht_s = float(h_ht_s.Integral(1, h_ht_s.GetNbinsX()+1))

            # initialize lists for tpr and fpr
            tpr_cicada = []
            tpr_ht = []
            fpr_cicada = []
            fpr_ht = []

            # iterate through bins and compute tpr and fpr for each threshold
            for j in range(h_cicada_zb.GetNbinsX()):
                # compute partial sums of histograms
                partial_cicada_s = float(h_cicada_s.Integral(j+1, h_cicada_s.GetNbinsX()+1))
                partial_ht_s = float(h_ht_s.Integral(j+1, h_ht_s.GetNbinsX()+1))
                partial_cicada_zb = float(h_cicada_zb.Integral(j+1, h_cicada_zb.GetNbinsX()+1))
                partial_ht_zb = float(h_ht_zb.Integral(j+1, h_ht_zb.GetNbinsX()+1))

                tpr_cicada_current = partial_cicada_s/integral_cicada_s
                fpr_cicada_current = partial_cicada_zb/integral_cicada_zb
                if fpr_cicada_current <= max_eff_val:
                    tpr_cicada.append(tpr_cicada_current)
                    fpr_cicada.append(fpr_cicada_current)

                fpr_ht_current = partial_ht_zb/integral_ht_zb
                tpr_ht_current = partial_ht_s/integral_ht_s
                if fpr_ht_current <= max_eff_val:
                    tpr_ht.append(tpr_ht_current)
                    fpr_ht.append(fpr_cicada_current)


            # convert to np arrays for some reason
            tpr_cicada = np.array(tpr_cicada, dtype = np.double)
            tpr_ht = np.array(tpr_ht, dtype = np.double)

            # create ROOT canvas
            c = ROOT.TCanvas("c", "ROC", 1000, 800)


            # create TGraph for cicada
            g_cicada = ROOT.TGraph(len(tpr_cicada), fpr_cicada, tpr_cicada)

            # plotting options for cicada graph
            g_cicada.SetTitle(f"ROC: Signal = {sample_names[i]}, CICADA version = {cicada_names[k]}")
            g_cicada.SetLineWidth(4)
            g_cicada.SetLineColor(2)
            g_cicada.GetXaxis().SetTitle("Zero Bias Rate")
            g_cicada.GetYaxis().SetTitle("Signal Efficiency")
            g_cicada.GetXaxis().SetRangeUser(0,max_eff_val)
            g_cicada.GetYaxis().SetRangeUser(0,1.2)

            # draw cicada TGraph
            g_cicada.Draw("AC")

            # create TGraph for HT
            g_ht = ROOT.TGraph(len(tpr_ht), fpr_ht, tpr_ht)

            # plotting options for ht graph
            g_ht.SetLineWidth(4)
            g_ht.SetLineColor(4)
            g_ht.GetXaxis().SetRangeUser(0,max_eff_val)
            g_ht.GetYaxis().SetRangeUser(0,1.2)
            g_ht.Draw("C same")

            #g_l1 = ROOT.TGraph(1, [efficiencies["ZeroBias"]], [efficiencies[sample_names[i]]])
            if sample_names[i] in efficiencies:
                g_l1 = ROOT.TGraph(1, 0.5, [efficiencies[sample_names[i]]])
            else: g_l1 = ROOT.TGraph(1, 0.5, 0.5)
            g_l1.SetMarkerSize(5)
            g_l1.Draw("P same")

            legend = ROOT.TLegend(0.1,0.75,0.9, 0.95)
            legend.AddEntry(g_cicada, "CICADA")
            legend.AddEntry(g_ht, "HT")
            legend.AddEntry(g_l1, "Unprescaled Trigger Efficiency")
            legend.SetBorderSize(0)
            legend.SetFillStyle(0)
            legend.Draw()

            # draw canvas and save plot
            c.Draw()
            c.SaveAs(f"{out_dir}/ROC_ZeroBias_{cicada_names[k]}_{sample_names[i]}.png")
            c.Close()

            #except Exception:
                #print(f"Unable to access sample: {sample_names[i]}, CICADA version: {cicada_names[k]}")


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

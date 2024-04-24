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

max_eff_val = 0.00344054

# function for drawing the CMS label on the plots
def createCMSLabel():
    cmsLatex = ROOT.TLatex()
    cmsLatex.SetTextSize(0.04)
    cmsLatex.SetNDC(True)
    cmsLatex.SetTextAlign(11)

    return cmsLatex

def main(zb_file, signal_file, signal_name, cicada_version, out_dir):

    f_zb = ROOT.TFile(zb_file)
    f_s = ROOT.TFile(signal_file)

    # load histograms
    h_cicada_zb = f_zb.Get(f"anomalyScore_ZeroBias_test_{cicada_version}")
    h_cicada_s = f_s.Get(f"anomalyScore_{signal_name}_{cicada_version}")
    h_ht_zb = f_zb.Get(f"HT_ZeroBias_test")
    h_ht_s = f_s.Get(f"HT_{signal_name}")

    # get integral of each histogram
    integral_cicada_zb = float(h_cicada_zb.Integral(1, h_cicada_zb.GetNbinsX()+1))
    integral_cicada_s = float(h_cicada_s.Integral(1, h_cicada_s.GetNbinsX()+1))
    integral_ht_zb = float(h_ht_zb.Integral(1, h_ht_zb.GetNbinsX()+1))
    integral_ht_s = float(h_ht_s.Integral(1, h_ht_s.GetNbinsX()+1))

    # initialize lists for tpr and fpr
    tpr_cicada = []
    fpr_cicada = []
    tpr_ht = []
    fpr_ht = []

    # iterate through bins and compute tpr and fpr for each threshold
    for j in range(h_cicada_zb.GetNbinsX()):
        # compute partial sums of histograms
        partial_cicada_zb = float(h_cicada_zb.Integral(j+1, h_cicada_zb.GetNbinsX()+1))
        partial_cicada_s = float(h_cicada_s.Integral(j+1, h_cicada_s.GetNbinsX()+1))
        partial_ht_zb = float(h_ht_zb.Integral(j+1, h_ht_zb.GetNbinsX()+1))
        partial_ht_s = float(h_ht_s.Integral(j+1, h_ht_s.GetNbinsX()+1))

        fpr_cicada_current = partial_cicada_zb/integral_cicada_zb
        tpr_cicada_current = partial_cicada_s/integral_cicada_s
        if fpr_cicada_current <= max_eff_val:
            fpr_cicada.append(fpr_cicada_current)
            tpr_cicada.append(tpr_cicada_current)

        fpr_ht_current = partial_ht_zb/integral_ht_zb
        tpr_ht_current = partial_ht_s/integral_ht_s
        if fpr_ht_current <= max_eff_val:
            fpr_ht.append(fpr_ht_current)
            tpr_ht.append(tpr_ht_current)


    # convert to np arrays for some reason
    tpr_cicada = np.array(tpr_cicada)
    fpr_cicada = np.array(fpr_cicada)
    tpr_ht = np.array(tpr_ht)
    fpr_ht = np.array(fpr_ht)

    # create ROOT canvas
    c = ROOT.TCanvas("c", "ROC", 1000, 800)

    # create TGraph for cicada
    g_cicada = ROOT.TGraph(len(tpr_cicada), fpr_cicada, tpr_cicada)

    # plotting options for cicada graph
    g_cicada.SetTitle(f"ROC: Signal = {signal_name}, CICADA version = {cicada_version}")
    g_cicada.SetLineWidth(4)
    g_cicada.SetLineColor(2)
    g_cicada.GetXaxis().SetTitle("FPR")
    g_cicada.GetYaxis().SetTitle("TPR")
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

    # draw canvas and save plot
    c.Draw()
    c.SaveAs(f"{out_dir}/ROC_{cicada_version}_{signal_name}.png")
    c.Close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This program creates CICADA ROC plots"
    )

    parser.add_argument(
        "-z",
        "--zero_bias_file",
        help="path to file containing zero bias histograms"
    )
    parser.add_argument(
        "-s",
        "--signal_file",
        help="path to file containing signal histograms"
    )
    parser.add_argument(
        "-n",
        "--signal_name",
        help="name of signal sample"
    )
    parser.add_argument(
        "-c",
        "--cicada_version",
        help="CICADA version"
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        default='./',
        help="directory to save output plots"
    )

    args = parser.parse_args()


    main(
        args.zero_bias_file,
        args.signal_file,
        args.signal_name,
        args.cicada_version,
        args.output_dir
    )

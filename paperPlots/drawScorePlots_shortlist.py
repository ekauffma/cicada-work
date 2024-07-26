import ROOT
import argparse
from sampleNames import sample_name_dict
import json
import re
from plottingUtils import convertCICADANametoPrint, createLabel

with open('plottingOptions.json') as f:
    options = json.load(f)

def drawOptions_ZeroBias(h_zb):
    h_zb.GetYaxis().SetRangeUser(options["scoreHist_y_min"], options["scoreHist_y_max"])
    h_zb.GetXaxis().SetRangeUser(0, options["scoreHist_x_max"])
    h_zb.SetMarkerColor(1)
    h_zb.SetLineColor(1)
    h_zb.SetMarkerStyle(20)
    h_zb.SetStats(0)
    h_zb.SetTitle("")
    h_zb.GetYaxis().SetTitle("Density")
    h_zb.GetXaxis().SetTitle("CICADA Score")

    return h_zb

# sets ROOT draw options for signal TH1 score histogram h_s for signal sample
# in shortlist with index i and returns the modified histogram
def drawOptions_Signal(h_s, i):

    h_s.SetMarkerColor(ROOT.TColor.GetColor(options["shortlist_colors"][i]))
    h_s.SetLineColor(ROOT.TColor.GetColor(options["shortlist_colors"][i]))
    h_s.SetMarkerStyle(options["shortlist_markers"][i])
    h_s.SetStats(0)
    h_s.SetTitle("")

    return h_s

def drawScorePlot(file_prefix, out_dir, c_name):

    c_name = "CICADA_v2p2p2"

    f_zb = ROOT.TFile(f"{file_prefix}_ZeroBias.root")
    h_zb = f_zb.Get(f"anomalyScore_ZeroBias_test_{c_name}").ProjectionX()
    h_zb.Scale(1/h_zb.Integral(0,h_zb.GetNbinsX()+1))


    # Create a canvas
    canvas = ROOT.TCanvas("canvas", "Canvas with TPads", 1000, 600)

    # Define three TPads
    pad1 = ROOT.TPad("pad1", "Pad 1", 0.0, 0.0, 0.8, 1.0)
    pad2 = ROOT.TPad("pad2", "Pad 2", 0.75, 0.0, 1.0, 1.0)

    # Draw the TPads on the canvas
    pad1.Draw()
    pad2.Draw()

    pad1.cd()

    # draw zb hist
    h_zb = drawOptions_ZeroBias(h_zb)
    h_zb.Draw("e")

    histograms = []
    files = []
    for i in range(len(options["sample_shortlist"])):
        current_sample = options["sample_shortlist"][i]
        print(current_sample)

        files.append(ROOT.TFile(f"{file_prefix}_{current_sample}.root"))
        h_s = files[-1].Get(f"anomalyScore_{current_sample}_{c_name}").ProjectionX()
        h_s.Scale(1/h_s.Integral(0,h_s.GetNbinsX()+1))
        h_s = drawOptions_Signal(h_s, i)

        histograms.append(h_s)

    for i in range(len(histograms)):
        histograms[i].Draw("e same")


    # draw cms label
    cmsLatex = createLabel()
    cmsLatex.DrawLatex(0.1,
                       0.92,
                       "#font[61]{CMS} #font[52]{Preliminary}")

    pad1.SetLogy()
    canvas.cd()

    pad2.cd()
    legend = ROOT.TLegend(0, 0.4, 0.9, 0.9)
    legend.AddEntry(h_zb, "Zero Bias", "lp")
    for i in range(len(histograms)):
        name = re.sub("[\(\[].*?[\)\]]", "", sample_name_dict[options["sample_shortlist"][i]])
        legend.AddEntry(histograms[i], name, "lp")
    legend.SetTextSize(0.055)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.Draw()

    # Save the canvas to a file
    canvas.SaveAs(f"{out_dir}/scorehist_shortlist_{c_name}.pdf")

    f_zb.Close()

    for i in range(len(files)):
        files[i].Close()


def main(file_prefix, output_dir):

    for i in range(len(options["cicada_names"])):

        drawScorePlot(file_prefix, output_dir, options["cicada_names"][i])

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="This program creates CICADA score plots"
    )
    parser.add_argument(
        "-p",
        "--file_prefix",
        help="path prefix to input ROOT files containing hists"
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        default='./',
        help="directory to save output plots"
    )

    args = parser.parse_args()



    main(args.file_prefix, args.output_dir)


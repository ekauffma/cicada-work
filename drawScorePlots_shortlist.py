import ROOT
import argparse
import numpy as np

sample_names = ["GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8",
                "GluGluHToGG_M-125_TuneCP5_13p6TeV_powheg-pythia8",
                "HHHTo6B_c3_0_d4_0_TuneCP5_13p6TeV_amcatnlo-pythia8",
                "HTo2LongLivedTo4b_MH-350_MFF-80_CTau-1000mm_TuneCP5_13p6TeV-pythia8",
                "SUEP",
                "SUSYGluGluToBBHToBB_NarrowWidth_M-350_TuneCP5_13p6TeV-pythia8",
                "ttHto2C_M-125_TuneCP5_13p6TeV_powheg-pythia8",
                "VBFHToInvisible_M-125_TuneCP5_13p6TeV_powheg-pythia8",
                "TT_TuneCP5_13p6TeV_powheg-pythia8"]

sample_colors = [46, 38, 30, 28, 42, 49, 39, 32, 41]

def createCMSLabel():
	cmsLatex = ROOT.TLatex()
	cmsLatex.SetTextSize(0.04)
	cmsLatex.SetNDC(True)
	cmsLatex.SetTextAlign(11)

	return cmsLatex


def main(input_file, output_dir, cicada_name):

	f = ROOT.TFile(input_file)

	c1 = ROOT.TCanvas("c1", "Anomaly Score", 1000,600)
	hist_zerobias = f.Get(f"anomalyScore_ZeroBias_{cicada_name}")

	hist_zerobias.GetYaxis().SetRangeUser(1,1e9)
	hist_zerobias.GetXaxis().SetRangeUser(0,256)
	hist_zerobias.SetMarkerColor(1)
	hist_zerobias.SetMarkerStyle(20)
	hist_zerobias.SetStats(0)
	hist_zerobias.SetTitle("")
	hist_zerobias.Draw("e")

	legend = ROOT.TLegend(0.1,0.7,0.9,0.9)

	for i in range(len(sample_names)):
		hist_sample = f.Get(f"anomalyScore_{sample_names[i]}_{cicada_name}")

	for i in range(len(sample_names)):
		hist_sample = f.Get(f"anomalyScore_{sample_names[i]}_{cicada_name}")

		hist_sample.SetMarkerColor(sample_colors[i])
		hist_sample.SetMarkerStyle(20)
		hist_sample.SetStats(0)
		hist_sample.SetTitle("")
		hist_sample.Draw("e same")

	cmsLatex = createCMSLabel()
	cmsLatex.DrawLatex(0.1,0.92, "#font[61]{CMS} #font[52]{Preliminary}")

	legend.AddEntry(hist_sample, f"{sample_names[i]}", "PE")
	legend.AddEntry(hist_zerobias, "ZeroBias", "PE")
	legend.SetTextSize(0.025)
	legend.SetBorderSize(0)
	legend.SetFillStyle(0)
	legend.Draw()

	c1.SetLogy()
	c1.Draw()
	c1.SaveAs(f"{output_dir}/scorehist_{sample_names[i]}_{cicada_name}.png")
	c1.Close()
		
	'''	hist_sample = f.Get(f"rate_{sample_names[i]}_{cicada_name}")
		hist_zerobias = f.Get(f"rate_ZeroBias_{cicada_name}")
		
		c3= ROOT.TCanvas("c2","Rate",1000,600)
		hist_zerobias.SetStats(0)
		hist_zerobias.SetMarkerColor(2)
		hist_zerobias.SetMarkerStyle(20)
		hist_zerobias.SetTitle("")
		hist_zerobias.GetXaxis().SetTitle("CICADA Score Threshold")
		hist_zerobias.GetYaxis().SetTitle("Overall Rate [kHz]")
		hist_zerobias.GetYaxis().SetRangeUser(5e-3,1e7)
		hist_zerobias.GetXaxis().SetRangeUser(0,256)
			
		hist_sample.SetStats(0)
		hist_sample.SetTitle("")
		hist_sample.SetMarkerColor(4)
		hist_sample.SetMarkerStyle(20)
		
		hist_zerobias.Draw("e")
		hist_sample.Draw("e same")

		cmsLatex = createCMSLabel()
		cmsLatex.DrawLatex(0.1,0.92, "#font[61]{CMS} #font[52]{Preliminary}")

		legend = ROOT.TLegend(0.1,0.7,0.9,0.9)
		legend.AddEntry(hist_sample, f"{sample_names[i]}", "PE")
		legend.AddEntry(hist_zerobias, "ZeroBias", "PE")
		legend.SetTextSize(0.025)
		legend.SetBorderSize(0)
		legend.SetFillStyle(0)
		legend.Draw()

		c3.SetLogy()
		c3.Draw()
		c3.SaveAs(f"{output_dir}/rate_{sample_names[i]}_{cicada_name}.png")
		c3.Close() '''

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="This program creates CICADA score plots")
	parser.add_argument("-i", "--input_file", help="path to input ROOT file containing hists")
	parser.add_argument("-o", "--output_dir", default='./', help="directory to save output plots")
	parser.add_argument("-c", "--cicada_name", help="name of CICADA model")

	args = parser.parse_args()

	main(args.input_file, args.output_dir, args.cicada_name)

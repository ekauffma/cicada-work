import ROOT
import argparse
import numpy as np
from array import array

sample_list = ["GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8",
               "GluGluHToGG_M-125_TuneCP5_13p6TeV_powheg-pythia8",
               "HHHTo6B_c3_0_d4_0_TuneCP5_13p6TeV_amcatnlo-pythia8",
               "HTo2LongLivedTo4b_MH-350_MFF-80_CTau-1000mm_TuneCP5_13p6TeV-pythia8",
               "SUEP",
               "SUSYGluGluToBBHToBB_NarrowWidth_M-350_TuneCP5_13p6TeV-pythia8",
               "ttHto2C_M-125_TuneCP5_13p6TeV_powheg-pythia8",
               "VBFHToInvisible_M-125_TuneCP5_13p6TeV_powheg-pythia8",
               "TT_TuneCP5_13p6TeV_powheg-pythia8"]

sample_names = ["#splitline{GluGluHToBB_M-125_TuneCP5_13p6TeV_}{powheg-pythia8}",
                "#splitline{GluGluHToGG_M-125_TuneCP5_13p6TeV_}{powheg-pythia8}",
                "#splitline{HHHTo6B_c3_0_d4_0_TuneCP5_13p6TeV_}{amcatnlo-pythia8}",
                "#splitline{HTo2LongLivedTo4b_MH-350_MFF-80_CTau}{-1000mm_TuneCP5_13p6TeV-pythia8}",
                "SUEP",
                "#splitline{SUSYGluGluToBBHToBB_NarrowWidth_M-350}{_TuneCP5_13p6TeV-pythia8}",
                "#splitline{ttHto2C_M-125_TuneCP5_13p6TeV_powheg-}{pythia8}",
                "#splitline{VBFHToInvisible_M-125_TuneCP5_13p6TeV_}{powheg-pythia8}",
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

	c1 = ROOT.TCanvas("c1", "Anomaly Score", 1000,800)

	pad1 = ROOT.TPad("pad1", "pad1", 0, 0.4, 0.7, 1.0)
	pad1.SetBottomMargin(0)
	pad1.Draw()

	pad3 = ROOT.TPad("pad3", "pad3", 0, 0.05, 0.7, 0.4)
	pad3.SetTopMargin(0)
	pad3.SetBottomMargin(0.2)
	pad3.Draw()
	
	pad1.cd()

	hist_zerobias = f.Get(f"anomalyScore_ZeroBias_{cicada_name}")

	hist_zerobias.GetYaxis().SetRangeUser(1,1e7)
	hist_zerobias.GetXaxis().SetRangeUser(0,256)
	hist_zerobias.SetMarkerColor(1)
	hist_zerobias.SetMarkerStyle(20)
	hist_zerobias.SetStats(0)
	hist_zerobias.SetTitle("")
	hist_zerobias.GetYaxis().SetTitle("Counts")
	hist_zerobias.Draw("e")

	pad1.cd()

	legend = ROOT.TLegend(0.0,0.2,1.0,0.95)
	legend.AddEntry(hist_zerobias, "ZeroBias", "PE")	

	for i in range(len(sample_names)):
		hist_sample = f.Get(f"anomalyScore_{sample_list[i]}_{cicada_name}")

		hist_sample.SetMarkerColor(sample_colors[i])
		hist_sample.SetMarkerStyle(20)
		hist_sample.SetLineColor(sample_colors[i])
		hist_sample.SetStats(0)
		hist_sample.SetTitle("")
		hist_sample.Draw("e same")

		legend.AddEntry(hist_sample, f"{sample_names[i]}", "PE")

	cmsLatex = createCMSLabel()
	cmsLatex.DrawLatex(0.1,0.92, "#font[61]{CMS} #font[52]{Preliminary}")

	pad1.SetLogy()

	c1.cd()
	pad3.cd()
	xvals = array('d')
	yvals = array('d')
	n = 300
	for i in range(n):
		xvals.append(i)
		yvals.append(1)
	g = ROOT.TGraph(n, xvals, yvals)
	g.SetLineColor(1)
	g.GetXaxis().SetRangeUser(0,256)
	g.GetYaxis().SetRangeUser(1e-3,1e7)
	g.SetTitle("")
	g.GetXaxis().SetTitle("CICADA Score Threshold")
	g.GetYaxis().SetTitle("Ratio")
	g.Draw("AC")

	hs = ROOT.THStack("hs","hs")

	for i in range(len(sample_names)):
		hist_sample = f.Get(f"anomalyScore_{sample_list[i]}_{cicada_name}")
		ratio_hist = hist_sample.Clone("ratio_hist")
		ratio_hist.Sumw2()
		ratio_hist.Divide(hist_zerobias)
		ratio_hist.SetMarkerStyle(20)
		ratio_hist.SetMarkerColor(sample_colors[i])
		ratio_hist.SetLineColor(sample_colors[i])

		#ratio_hist.Draw("e same")
		hs.Add(ratio_hist)

	hs.Draw("e nostack same")
	pad3.SetLogy()

	c1.cd()
	pad2 = ROOT.TPad("pad2", "pad2", 0.65, 0, 1.0, 1.0)
	pad2.Draw()
	pad2.cd()

	legend.SetTextSize(0.035)
	legend.SetBorderSize(0)
	legend.SetFillStyle(0)
	legend.Draw()


	c1.Draw()
	c1.SaveAs(f"{output_dir}/scorehist_{sample_list[i]}_{cicada_name}.png")
	#c1.Close()
		
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

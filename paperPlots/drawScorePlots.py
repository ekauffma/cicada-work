import ROOT
import argparse
import numpy as np
from paperSampleBuilder import samples

def createCMSLabel():
	cmsLatex = ROOT.TLatex()
	cmsLatex.SetTextSize(0.04)
	cmsLatex.SetNDC(True)
	cmsLatex.SetTextAlign(11)

	return cmsLatex


def main(input_file, output_dir, cicada_name):

	f = ROOT.TFile(input_file)

	sample_names = list(samples.keys())
	if 'ZeroBias' in sample_names:
		sample_names.remove('ZeroBias')
	

	for i in range(len(sample_names)):
		hist_sample = f.Get(f"anomalyScore_{sample_names[i]}_{cicada_name}")
		hist_zerobias = f.Get(f"anomalyScore_ZeroBias_{cicada_name}")

		c1 = ROOT.TCanvas("c1", "Anomaly Score", 1000,600)
		hist_sample.SetMarkerColor(4)
		hist_sample.SetMarkerStyle(20)
		hist_zerobias.GetXaxis().SetTitle("CICADA Score Threshold");
		hist_zerobias.GetYaxis().SetTitle("Counts");
		hist_sample.SetStats(0)
		hist_sample.SetTitle("")
	
		hist_zerobias.GetYaxis().SetRangeUser(1,1e9)
		hist_zerobias.GetXaxis().SetRangeUser(0,256)	
		hist_zerobias.SetMarkerColor(2)
		hist_zerobias.SetMarkerStyle(20)
		hist_zerobias.SetStats(0)
		#hist_zerobias.Draw("b same")
		hist_zerobias.SetTitle("")
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

		c1.SetLogy()
		c1.Draw()
		c1.SaveAs(f"{output_dir}/scorehist_{sample_names[i]}_{cicada_name}.png")
		c1.Close()
		
		hist_sample = f.Get(f"rate_{sample_names[i]}_{cicada_name}")
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
		c3.Close()

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="This program creates CICADA score plots")
	parser.add_argument("-i", "--input_file", help="path to input ROOT file containing hists")
	parser.add_argument("-o", "--output_dir", default='./', help="directory to save output plots")
	parser.add_argument("-c", "--cicada_name", help="name of CICADA model")

	args = parser.parse_args()

	main(args.input_file, args.output_dir, args.cicada_name)

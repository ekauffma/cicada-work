import ROOT
import argparse
import numpy as np
from array import array
from paperSampleBuilder import samples
from sampleNames import sample_name_dict

def createCMSLabel():
	cmsLatex = ROOT.TLatex()
	cmsLatex.SetTextSize(0.04)
	cmsLatex.SetNDC(True)
	cmsLatex.SetTextAlign(11)

	return cmsLatex


def main(input_file1, input_file2, N,  output_dir, cicada_name):

	N_str = ""
	if N: N_str = "N"

	f = [ROOT.TFile(input_file1), ROOT.TFile(input_file2)]

	sample_names = list(samples.keys())
	if 'ZeroBias' in sample_names:
		sample_names.remove('ZeroBias')	
	if 'SingleNeutrino_E-10-gun' in sample_names:
		sample_names.remove('SingleNeutrino_E-10-gun')

	ylabels = ["Frequency (Standard)", "Frequency (Noise-Suppressed)"]
	sample_color = [6,9]
	sample_style = [22,26]
	legends = []
	legend_tops = [0.9,1.0]

	for i in range(len(sample_names)):

		c1 = ROOT.TCanvas("c1", "Anomaly Score", 1000, 1000)

		pads = [ROOT.TPad("pad1", "pad1", 0.0, 0.6, 1.0, 1.0), ROOT.TPad("pad2", "pad2", 0, 0.2, 1.0, 0.6)]
		pads[0].SetBottomMargin(0)
		pads[1].SetBottomMargin(0)
		pads[1].SetTopMargin(0)
		for pad in pads:
			pad.Draw()
		pad_ratio = ROOT.TPad("pad_ratio", "pad_ratio", 0, 0, 1.0, 0.2)
		pad_ratio.SetBottomMargin(0.2)
		pad_ratio.SetTopMargin(0)
		pad_ratio.Draw()

		for j in [0,1]:

			pads[j].cd()	

			# get histograms
			print(f"anomalyScore_ZeroBias_{cicada_name}p{j}{N_str}")	
			hist_zb = f[j].Get(f"anomalyScore_ZeroBias_{cicada_name}p{j}{N_str}")
			hist_sng = f[j].Get(f"anomalyScore_SingleNeutrino_E-10-gun_{cicada_name}p{j}{N_str}")
			hist_sample = f[j].Get(f"anomalyScore_{sample_names[i]}_{cicada_name}p{j}{N_str}")

			# styling
			hist_zb.SetMarkerColor(1)
			hist_zb.SetLineColor(1)
			hist_zb.SetMarkerStyle(20)

			hist_sng.SetMarkerColor(8)
			hist_sng.SetLineColor(8)
			hist_sng.SetMarkerStyle(21)

			hist_sample.SetMarkerColor(sample_color[j])
			hist_sample.SetLineColor(sample_color[j])
			hist_sample.SetMarkerStyle(sample_style[j])

			# draw histograms
			hist_zb.Scale(1/hist_zb.Integral())
			hist_zb.GetYaxis().SetRangeUser(1e-7,1e1)
			hist_zb.GetXaxis().SetRangeUser(0,256)
			hist_zb.SetStats(0)
			hist_zb.SetTitle("")
			hist_zb.GetYaxis().SetTitle(ylabels[j])
			hist_zb.Draw("e")

			hist_sng.Scale(1/hist_sng.Integral())
			hist_sng.SetStats(0)
			hist_sng.SetTitle("")
			hist_sng.Draw("e same")

			hist_sample.Scale(1/hist_sample.Integral())
			hist_sample.SetStats(0)
			hist_sample.SetTitle("")
			hist_sample.Draw("e same")
			
			# create CMS label (only on top pad)
			if j==0:
				cmsLatex = createCMSLabel()
				cmsLatex.DrawLatex(0.1,0.92, "#font[61]{CMS} #font[52]{Preliminary}")

			# create and draw legend
			legends.append(ROOT.TLegend(0.4,legend_tops[j]-0.2,1.0,legend_tops[j]))
			legends[-1].AddEntry(hist_zb, "Zero Bias", "PE")
			legends[-1].AddEntry(hist_sng, "Single Neutrino Gun", "PE")
			legends[-1].AddEntry(hist_sample, sample_name_dict[sample_names[i]], "PE")	
			legends[-1].SetTextSize(0.04)
			legends[-1].SetBorderSize(0)
			legends[-1].SetFillStyle(0)
			legends[-1].Draw()
			
			pads[j].SetLogy()
			c1.cd()
			
		# need separate loop for ratio plots
		pad_ratio.cd()
		pad_ratio.SetLogy()
		legend_ratio = ROOT.TLegend(0.15,0.75,0.4,0.95)
		legend_ratio.SetTextSize(0.07)
		legend_ratio.SetBorderSize(0)
		legend_ratio.SetFillStyle(0)
		hs = ROOT.THStack("hs","hs")
		for j in [0,1]:
			hist_zb = f[j].Get(f"anomalyScore_ZeroBias_{cicada_name}p{j}{N_str}")
			hist_sample = f[j].Get(f"anomalyScore_{sample_names[i]}_{cicada_name}p{j}{N_str}")
			
			# calculate ratio hist and add to stack
			ratio_hist = hist_sample.Clone("ratio_hist")
			ratio_hist.Sumw2()
			ratio_hist.Divide(hist_zb)
			ratio_hist.SetMarkerColor(sample_color[j])
			ratio_hist.SetLineColor(sample_color[j])
			ratio_hist.SetMarkerStyle(sample_style[j])
			hs.Add(ratio_hist)
			legend_ratio.AddEntry(ratio_hist, f"{cicada_name}p{j}{N_str}")

		
		# create horizontal line at 1
		xvals = array('d')
		yvals = array('d')
		n = 300
		for j in range(n):
			xvals.append(j)
			yvals.append(1)
		g = ROOT.TGraph(n, xvals, yvals)
		g.SetLineColor(1)
		g.GetXaxis().SetRangeUser(0,256)
		g.GetYaxis().SetRangeUser(1e-3,1e5)
		g.SetTitle("")
		g.GetXaxis().SetTitle("CICADA Score")
		g.GetYaxis().SetTitle("Ratio to Zero Bias")
		g.GetXaxis().SetLabelSize(0.07)
		g.GetYaxis().SetLabelSize(0.07)
		g.GetXaxis().SetTitleSize(0.07)
		g.GetYaxis().SetTitleSize(0.07)
		g.GetYaxis().SetTitleOffset(0.6)
		g.Draw("AC")

		# draw ratios
		hs.Draw("e nostack same")
		legend_ratio.Draw()
		c1.cd()

		c1.Draw()
		c1.SaveAs(f"{output_dir}/scorehist_{sample_names[i]}_{cicada_name}.png")
		c1.Close()
	

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="This program creates CICADA score plots")
	parser.add_argument("-i1", "--input_file1", help="path to input ROOT file containing hists (standard)")
	parser.add_argument("-i2", "--input_file2", help="path to input ROOT file containing hists (noise-suppressed)")
	parser.add_argument("-n", "--n", default=False, help="whether cicada name has N at the end")
	parser.add_argument("-o", "--output_dir", default='./', help="directory to save output plots")
	parser.add_argument("-c", "--cicada_name", help="name of CICADA model, omitting p0(1)(N)")

	args = parser.parse_args()

	main(args.input_file1, args.input_file2, args.n, args.output_dir, args.cicada_name)

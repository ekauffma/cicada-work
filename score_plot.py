import ROOT
import argparse
import numpy as np

def main(input_file, run):

	# histogram and plotting options
	nBins = 100

	f = open(input_file, "r")

	root_files = f.read().split("\n")

	tchains = [ROOT.TChain("CICADAv1ntuplizer/L1TCaloSummaryOutput"), ROOT.TChain("CICADAv2ntuplizer/L1TCaloSummaryOutput")]
	tchain_names = ["CICADAv1","CICADAv2"]


	for file_name in root_files:
		for tchain in tchains:
			try:
				tchain.Add(file_name)
			except:
				print(f"An exception occured for file {file_name}")
				continue
	print("Created TChains")
	
	for i in range(len(tchains)):
		rdf = ROOT.RDataFrame(tchains[i])
		print(f"Created RDF for {tchain_names[i]}")
		max_score = rdf.Max('anomalyScore').GetValue()
		min_score = rdf.Min('anomalyScore').GetValue()
		print(f"Max = {max_score}, Min = {min_score}")

		histModel = ROOT.RDF.TH1DModel("anomalyScore", "anomalyScore", nBins, min_score, max_score)
		hist = rdf.Histo1D(histModel, 'anomalyScore')

		# create score plot
		c1 = ROOT.TCanvas("c1", "Anomaly Score", 200, 10, 700, 500)
		hist.SetMarkerColor(4)
		hist.SetMarkerStyle(20)
		hist.GetXaxis().SetTitle("CICADA Score");
		hist.GetYaxis().SetTitle("Counts");
		hist.SetStats(0)
		hist.SetTitle("")
		hist.Draw("b")
		hist.Draw("e same")

		cmsLatex = ROOT.TLatex()
		cmsLatex.SetTextSize(0.04)
		cmsLatex.SetNDC(True)
		cmsLatex.SetTextAlign(11)
		cmsLatex.DrawLatex(0.1,0.92, "#font[61]{CMS} #font[52]{Preliminary}")

		c1.SetLogy()
		c1.Draw()
		c1.SaveAs(f"scorehist_{run}_{tchain_names[i]}.png")
		c1.Close()

		# make efficiency plot
		eff = ROOT.TH1D("anomalyScore_eff",
				"anomalyScore_eff",
				hist.GetNbinsX(), 
				hist.GetXaxis().GetXmin(),
				hist.GetXaxis().GetXmax())

		# total integral
		scoreplot_int = float(hist.Integral())

		# compute value for each threshold
		for j in range(1, hist.GetNbinsX()+1):
			scoreplot_int_current = float(hist.Integral(j, hist.GetNbinsX()))
			uncertainty = np.sqrt(scoreplot_int_current)
			scoreplot_int_current = scoreplot_int_current/scoreplot_int
			uncertainty = uncertainty/scoreplot_int

			eff.SetBinContent(j,scoreplot_int_current)
			eff.SetBinError(j, uncertainty)
		
		c2 = ROOT.TCanvas("c2", "efficiency", 200, 10, 700, 500)
		eff.SetStats(0)
		eff.SetMarkerColor(4)
		eff.SetMarkerStyle(20)
		eff.SetTitle("")
		eff.GetXaxis().SetTitle("CICADA Score Threshold")
		eff.GetYaxis().SetTitle("Efficiency")
		eff.GetXaxis().SetRangeUser(0,8)
		eff.Draw("b")
		eff.Draw("e same")
		
		cmsLatex = ROOT.TLatex()
		cmsLatex.SetTextSize(0.04)
		cmsLatex.SetNDC(True)
		cmsLatex.SetTextAlign(11)
		cmsLatex.DrawLatex(0.1,0.92, "#font[61]{CMS} #font[52]{Preliminary}")

		c2.SetLogy()
		c2.Draw()
		c2.SaveAs(f"eff_{run}_{tchain_names[i]}.png")
		c2.Close()

		# make rate plot
		c3 = ROOT.TCanvas("c3", "rate", 200, 10, 700, 500)
		eff.Scale(2544.0 * 11245e-3) # convert efficiency to rate
		eff.SetStats(0)
		eff.SetMarkerColor(4)
		eff.SetMarkerStyle(20)
		eff.SetTitle("")
		eff.GetXaxis().SetTitle("CICADA Score Threshold")
		eff.GetYaxis().SetTitle("Rate (kHz)")
		eff.GetXaxis().SetRangeUser(0,8)
		eff.Draw("b")
		eff.Draw("e same")
		c3.SetLogy()
		
		cmsLatex = ROOT.TLatex()
		cmsLatex.SetTextSize(0.04)
		cmsLatex.SetNDC(True)
		cmsLatex.SetTextAlign(11)
		cmsLatex.DrawLatex(0.1,0.92, "#font[61]{CMS} #font[52]{Preliminary}")

		c3.Draw()
		c3.SaveAs(f"rate_{run}_{tchain_names[i]}.png")
		c3.Close()	

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="This program creates CICADA score plots")
	parser.add_argument("-i", "--input_file", help="path to input text file listing paths to ROOT files")
	parser.add_argument("-n", "--run", help="run corresponding to files listed in input_file")

	args = parser.parse_args()

	main(args.input_file, args.run)

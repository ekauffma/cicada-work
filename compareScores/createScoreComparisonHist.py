import ROOT
import argparse
import awkward as ak
import json
import numpy as np
from sampleBuilder import samples_unpacked, samples_emulated

# limits for histograms
min_diff = -100
max_diff = 100
bins_diff = 400
min_run = 382725
max_run = 383467
bins_run = max_run - min_run
min_score = 0
max_score = 256
bins_score = 100

def main(dataset, out_dir):

    dict_total = {}
    dict_discrepancies = {}

    # get dataframe from samples
    print("Getting dataframes and creating aliases")
    df_unpacked = samples_unpacked[dataset].getNewDataframe()
    df_emulated = samples_emulated[dataset].getNewDataframe()
    df_unpacked = df_unpacked.Alias("CICADAScore_unpacked", "CICADAScore")
    df_emulated = df_emulated.Alias("CICADAScore_emulated", "CICADAScore")

    print("Saving as numpy arrays")
    df_unpacked_arr = df_unpacked.AsNumpy(columns=["CICADAScore_unpacked", "run"])
    df_emulated_arr = df_emulated.AsNumpy(columns=["CICADAScore_emulated"])

    combined_data = {
        "run": df_unpacked_arr["run"],
        "CICADAScore_unpacked": df_unpacked_arr["CICADAScore_unpacked"],
        "CICADAScore_emulated": df_emulated_arr["CICADAScore_emulated"],
        "score_difference": df_unpacked_arr["CICADAScore_unpacked"] - df_emulated_arr["CICADAScore_emulated"]
    }

    print("Creating combined dataframe")
    combined_df = ROOT.RDF.FromNumpy(combined_data)

    # create output ROOT file
    print("Creating output ROOT file")
    output_file = ROOT.TFile(
        f'{out_dir}/hist_comparescore_{dataset}.root',
        'RECREATE'
    )

    print("Creating and writing histogram for difference")
    histModel = ROOT.RDF.TH2DModel(
        "compareScore",
        "compareScore",
        bins_run,
        min_run,
        max_run,
        bins_diff,
        min_diff,
        max_diff,
    )
    hist = combined_df.Histo2D(
        histModel,
        "run",
        "score_difference"
    )
    hist.Write()

    print("Creating and writing histogram for unpacked score")
    histModel = ROOT.RDF.TH2DModel(
        "unpackedScore",
        "unpackedScore",
        bins_run,
        min_run,
        max_run,
        bins_score,
        min_score,
        max_score,
    )
    hist = combined_df.Histo2D(
        histModel,
        "run",
        "CICADAScore_unpacked"
    )
    hist.Write()

    print("Creating and writing histogram for emulated score")
    histModel = ROOT.RDF.TH2DModel(
        "emulatedcore",
        "emulatedScore",
        bins_run,
        min_run,
        max_run,
        bins_score,
        min_score,
        max_score,
    )
    hist = combined_df.Histo2D(
        histModel,
        "run",
        "CICADAScore_emulated"
    )
    hist.Write()

    print("Computing number of discrepancies and saving to dictionaries")
    for i in range(len(combined_data["run"])):
        if not combined_data["run"][i] in dict_total:
            dict_total[combined_data["run"][i]] = 0
            dict_discrepancies[combined_data["run"][i]] = 0

        if combined_data["score_difference"][i]==0: dict_discrepancies[combined_data["run"][i]]+=1
        dict_total[combined_data["run"][i]]+=1

    print("Dividing number of discrepancies by total number of events and saving")
    dict_ratio = {}
    for run in dict_total.keys():
        dict_ratio[int(run)] = dict_discrepancies[run]/dict_total[run]
        print("    Run = ", run, ", Fraction Not Matching = ", dict_ratio[run])

    with open(f"{out_dir}/differences_{dataset}.json", "w") as outfile:
        json.dump(dict_ratio, outfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This program creates a 2d histogram with run number and discrepancy between unpacked and emulator score"
    )
    parser.add_argument(
        "-d",
        "--dataset",
        help="which dataset to create the histogram for"
    )
    parser.add_argument(
        "-o",
        "--out_dir",
        default = ".",
        help="directory to save files to"
    )

    args = parser.parse_args()

    main(args.dataset, args.out_dir)

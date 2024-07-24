import uproot
import awkward as ak
import hist
from hist import Hist
import mplhep as hep
import argparse
import matplotlib.pyplot as plt
import json
import numpy as np
from matplotlib.ticker import MaxNLocator

def reduceHistogram(h):

    values = h.values()
    run_nums = h.axis(0).edges()
    
    values_mod = []
    run_nums_mod = []
    
    for i in range(values.shape[0]):
        if sum(values[i,:])>0:
            values_mod.append(list(values[i,:]))
            run_nums_mod.append(run_nums[i])
            
    h_mod = Hist(
        hist.axis.Regular(len(run_nums_mod), 0, len(run_nums_mod), name="run"),
        hist.axis.Regular(len(h.axis(1).edges())-1, h.axis(1).edges()[0], h.axis(1).edges()[-1], name="score"),
    )
    
    for i in range(len(values_mod)):
        for j in range(len(values_mod[i])):
            h_mod[i, j] = values_mod[i][j]
            
    print(h_mod.values())
    
    return h_mod, run_nums_mod

def main(input_file_hist, input_file_json, out_dir, dataset):

    hep.style.use("CMS")

    f = uproot.open(input_file_hist)

    # comparison plot
    h_compareScore = f["compareScore"]
    h_compareScore_mod, run_nums_mod = reduceHistogram(h_compareScore)
    fig, ax = plt.subplots()
    hep.hist2dplot(h_compareScore_mod, ax=ax)
    plt.tight_layout()
    ax.set_xlabel("Run Number")
    ax.set_ylabel("Unpacked Score - Emulated Score")
    ax.set_ylim([-25,25])
    ax.set_title(f"Dataset: {dataset}")
    ax.set_xticks(np.arange(1, len(run_nums_mod)+1))
    ax.set_xticklabels([str(int(x)) for x in run_nums_mod], rotation=45, ha='right')
    fig.subplots_adjust(bottom=0.2)
    fig.show()
    fig.savefig(f'{out_dir}/compareScore_mod_{dataset}.png')
    plt.clf()

    # unpacked score plot
    h_unpackedScore = f["unpackedScore"]
    h_unpackedScore_mod, run_nums_mod = reduceHistogram(h_unpackedScore)
    fig, ax = plt.subplots()
    hep.hist2dplot(h_unpackedScore_mod, ax=ax)
    plt.tight_layout()
    ax.set_xlabel("Run Number")
    ax.set_ylabel("Unpacked Score")
    ax.set_ylim([0 ,256])
    ax.set_title(f"Dataset: {dataset}")
    ax.set_xticks(np.arange(1, len(run_nums_mod)+1))
    ax.set_xticklabels([str(int(x)) for x in run_nums_mod], rotation=45, ha='right')
    fig.subplots_adjust(bottom=0.2)
    fig.show()
    fig.savefig(f'{out_dir}/unpackedScore_mod_{dataset}.png')
    plt.clf()

    # emulated score plot
    h_emulatedScore = f["emulatedcore"]
    h_emulatedScore_mod, run_nums_mod = reduceHistogram(h_emulatedScore)
    fig, ax = plt.subplots()
    hep.hist2dplot(h_emulatedScore_mod, ax=ax)
    plt.tight_layout()
    ax.set_xlabel("Run Number")
    ax.set_ylabel("Emulated Score")
    ax.set_ylim([0 ,256])
    ax.set_title(f"Dataset: {dataset}")
    ax.set_xticks(np.arange(1, len(run_nums_mod)+1))
    ax.set_xticklabels([str(int(x)) for x in run_nums_mod], rotation=45, ha='right')
    fig.subplots_adjust(bottom=0.2)
    fig.show()
    fig.savefig(f'{out_dir}/emulatedScore_mod_{dataset}.png')
    plt.clf()

    f.close()

    f = open(input_file_json)
    data = json.load(f)
    runs = list(data.keys())
    ratios = list(data.values())
    ratios = [x for _,x in sorted(zip(runs, ratios))]
    runs = sorted(runs)

    fig, ax = plt.subplots()
    ax.plot(runs, ratios, 'o')
    ax.set_xlabel("Run Number")
    ax.set_ylabel("Number of Discrepancies / Total")
    ax.set_title(f"Dataset: {dataset}")
    ax.set_xticks(ax.get_xticks())
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    plt.tight_layout()
    fig.savefig(f'{out_dir}/fractionDifferent_{dataset}.png')

    f.close()

if __name__ == "__main__":


    parser = argparse.ArgumentParser(description = "This program draws histograms and plots comparing emulated vs unpacked score")

    parser.add_argument("-r", "--input_file_hist", help="input file for ROOT histograms")
    parser.add_argument("-j", "--input_file_json", help="input file for json containing discrepancy ratios")
    parser.add_argument("-o", "--out_dir", help="directory in which to save plots")
    parser.add_argument("-d", "--dataset", help="which dataset")

    args = parser.parse_args()


    main(args.input_file_hist, args.input_file_json, args.out_dir, args.dataset)


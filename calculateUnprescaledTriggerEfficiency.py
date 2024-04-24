########################################################################
## calculateUnprescaledTriggerEfficiency.py                           ##
## Author: Elliott Kauffman                                           ##
## calculate the unprescaled trigger efficiencies for ROC plots        ##
########################################################################

import ROOT
import argparse
import numpy as np
from paperSampleBuilder import samples

triggers = [
    "L1_AlwaysTrue",
    "L1_BPTX_AND_Ref1_VME",
    "L1_BPTX_AND_Ref3_VME",
    "L1_BPTX_AND_Ref4_VME",
    "L1_BPTX_BeamGas_B1_VME",
    "L1_BPTX_BeamGas_B2_VME",
    "L1_BPTX_BeamGas_Ref1_VME",
    "L1_BPTX_BeamGas_Ref2_VME",
    "L1_BPTX_NotOR_VME",
    "L1_BPTX_OR_Ref3_VME",
    "L1_BPTX_OR_Ref4_VME",
    "L1_BPTX_RefAND_VME",
    "L1_BptxMinus",
    "L1_BptxOR",
    "L1_BptxPlus",
    "L1_BptxXOR",
    "L1_CDC_SingleMu_3_er1p2_TOP120_DPHI2p618_3p142",
    "L1_DoubleEG10_er1p2_dR_Max0p6",
    "L1_DoubleEG10p5_er1p2_dR_Max0p6",
    "L1_DoubleEG11_er1p2_dR_Max0p6",
    "L1_DoubleEG4_er1p2_dR_Max0p9",
    "L1_DoubleEG4p5_er1p2_dR_Max0p9",
    "L1_DoubleEG5_er1p2_dR_Max0p9",
    "L1_DoubleEG5p5_er1p2_dR_Max0p8",
    "L1_DoubleEG6_er1p2_dR_Max0p8",
    "L1_DoubleEG6p5_er1p2_dR_Max0p8",
    "L1_DoubleEG7_er1p2_dR_Max0p8",
    "L1_DoubleEG7p5_er1p2_dR_Max0p7",
    "L1_DoubleEG8_er1p2_dR_Max0p7",
    "L1_DoubleEG8er2p5_HTT260er",
    "L1_DoubleEG8er2p5_HTT280er",
    "L1_DoubleEG8er2p5_HTT300er",
    "L1_DoubleEG8er2p5_HTT320er",
    "L1_DoubleEG8er2p5_HTT340er",
    "L1_DoubleEG8p5_er1p2_dR_Max0p7",
    "L1_DoubleEG9_er1p2_dR_Max0p7",
    "L1_DoubleEG9p5_er1p2_dR_Max0p6",
    "L1_DoubleEG_15_10_er2p5",
    "L1_DoubleEG_20_10_er2p5",
    "L1_DoubleEG_22_10_er2p5",
    "L1_DoubleEG_25_12_er2p5",
    "L1_DoubleEG_25_14_er2p5",
    "L1_DoubleEG_27_14_er2p5",
    "L1_DoubleEG_LooseIso16_LooseIso12_er1p5",
    "L1_DoubleEG_LooseIso18_LooseIso12_er1p5",
    "L1_DoubleEG_LooseIso20_LooseIso12_er1p5",
    "L1_DoubleEG_LooseIso22_12_er2p5",
    "L1_DoubleEG_LooseIso22_LooseIso12_er1p5",
    "L1_DoubleEG_LooseIso25_12_er2p5",
    "L1_DoubleEG_LooseIso25_LooseIso12_er1p5",
    "L1_DoubleIsoTau26er2p1_Jet55_RmOvlp_dR0p5",
    "L1_DoubleIsoTau26er2p1_Jet70_RmOvlp_dR0p5",
    "L1_DoubleIsoTau28er2p1",
    "L1_DoubleIsoTau28er2p1_Mass_Max80",
    "L1_DoubleIsoTau28er2p1_Mass_Max90",
    "L1_DoubleIsoTau30er2p1",
    "L1_DoubleIsoTau30er2p1_Mass_Max80",
    "L1_DoubleIsoTau30er2p1_Mass_Max90",
    "L1_DoubleIsoTau32er2p1",
    "L1_DoubleIsoTau32er2p1_Mass_Max80",
    "L1_DoubleIsoTau34er2p1",
    "L1_DoubleIsoTau35er2p1",
    "L1_DoubleIsoTau36er2p1",
    "L1_DoubleJet100er2p3_dEta_Max1p6",
    "L1_DoubleJet100er2p5",
    "L1_DoubleJet112er2p3_dEta_Max1p6",
    "L1_DoubleJet120er2p5",
    "L1_DoubleJet120er2p5_Mu3_dR_Max0p8",
    "L1_DoubleJet150er2p5",
    "L1_DoubleJet16er2p5_Mu3_dR_Max0p4",
    "L1_DoubleJet30er2p5_Mass_Min225_dEta_Max1p5",
    "L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5",
    "L1_DoubleJet30er2p5_Mass_Min300_dEta_Max1p5",
    "L1_DoubleJet30er2p5_Mass_Min330_dEta_Max1p5",
    "L1_DoubleJet30er2p5_Mass_Min360_dEta_Max1p5",
    "L1_DoubleJet35_Mass_Min450_IsoTau45_RmOvlp",
    "L1_DoubleJet35_Mass_Min450_IsoTau45er2p1_RmOvlp_dR0p5",
    "L1_DoubleJet35er2p5_Mu3_dR_Max0p4",
    "L1_DoubleJet40_Mass_Min450_IsoEG10er2p1_RmOvlp_dR0p2",
    "L1_DoubleJet40_Mass_Min450_LooseIsoEG15er2p1_RmOvlp_dR0p2",
    "L1_DoubleJet40er2p5",
    "L1_DoubleJet45_Mass_Min450_IsoTau45er2p1_RmOvlp_dR0p5",
    "L1_DoubleJet45_Mass_Min450_LooseIsoEG20er2p1_RmOvlp_dR0p2",
    "L1_DoubleJet60er2p5_Mu3_dR_Max0p4",
    "L1_DoubleJet80er2p5_Mu3_dR_Max0p4",
    "L1_DoubleJet_100_30_DoubleJet30_Mass_Min620",
    "L1_DoubleJet_100_30_DoubleJet30_Mass_Min800",
    "L1_DoubleJet_110_35_DoubleJet35_Mass_Min620",
    "L1_DoubleJet_110_35_DoubleJet35_Mass_Min800",
    "L1_DoubleJet_115_40_DoubleJet40_Mass_Min620",
    "L1_DoubleJet_115_40_DoubleJet40_Mass_Min620_Jet60TT28",
    "L1_DoubleJet_120_45_DoubleJet45_Mass_Min620",
    "L1_DoubleJet_120_45_DoubleJet45_Mass_Min620_Jet60TT28",
    "L1_DoubleJet_60_30_DoubleJet30_Mass_Min500_DoubleJetCentral50",
    "L1_DoubleJet_65_30_DoubleJet30_Mass_Min400_ETMHF65",
    "L1_DoubleJet_65_35_DoubleJet35_Mass_Min500_DoubleJetCentral50",
    "L1_DoubleJet_70_35_DoubleJet35_Mass_Min400_ETMHF65",
    "L1_DoubleJet_80_30_DoubleJet30_Mass_Min500_Mu3OQ",
    "L1_DoubleJet_80_30_Mass_Min420_DoubleMu0_SQ",
    "L1_DoubleJet_80_30_Mass_Min420_IsoTau40_RmOvlp",
    "L1_DoubleJet_80_30_Mass_Min420_Mu8",
    "L1_DoubleJet_85_35_DoubleJet35_Mass_Min500_Mu3OQ",
    "L1_DoubleJet_90_30_DoubleJet30_Mass_Min620",
    "L1_DoubleJet_90_30_DoubleJet30_Mass_Min800",
    "L1_DoubleLLPJet40",
    "L1_DoubleLooseIsoEG22er2p1",
    "L1_DoubleLooseIsoEG24er2p1",
    "L1_DoubleMu0",
    "L1_DoubleMu0_Mass_Min1",
    "L1_DoubleMu0_OQ",
    "L1_DoubleMu0_SQ",
    "L1_DoubleMu0_SQ_OS",
    "L1_DoubleMu0_Upt15_Upt7",
    "L1_DoubleMu0_Upt15_Upt7_BMTF_EMTF",
    "L1_DoubleMu0_Upt5_Upt5",
    "L1_DoubleMu0_Upt5_Upt5_BMTF_EMTF",
    "L1_DoubleMu0_Upt6_IP_Min1_Upt4",
    "L1_DoubleMu0_Upt6_IP_Min1_Upt4_BMTF_EMTF",
    "L1_DoubleMu0_dR_Max1p6_Jet90er2p5_dR_Max0p8",
    "L1_DoubleMu0er1p4_OQ_OS_dEta_Max1p6",
    "L1_DoubleMu0er1p4_SQ_OS_dEta_Max1p2",
    "L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4",
    "L1_DoubleMu0er1p5_SQ",
    "L1_DoubleMu0er1p5_SQ_OS",
    "L1_DoubleMu0er1p5_SQ_OS_dEta_Max1p2",
    "L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4",
    "L1_DoubleMu0er1p5_SQ_dR_Max1p4",
    "L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p5",
    "L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p6",
    "L1_DoubleMu0er2p0_SQ_dEta_Max1p5",
    "L1_DoubleMu0er2p0_SQ_dEta_Max1p6",
    "L1_DoubleMu18er2p1_SQ",
    "L1_DoubleMu3_OS_er2p3_Mass_Max14_DoubleEG7p5_er2p1_Mass_Max20",
    "L1_DoubleMu3_SQ_ETMHF30_HTT60er",
    "L1_DoubleMu3_SQ_ETMHF30_Jet60er2p5_OR_DoubleJet40er2p5",
    "L1_DoubleMu3_SQ_ETMHF40_HTT60er",
    "L1_DoubleMu3_SQ_ETMHF40_Jet60er2p5_OR_DoubleJet40er2p5",
    "L1_DoubleMu3_SQ_ETMHF50_HTT60er",
    "L1_DoubleMu3_SQ_ETMHF50_Jet60er2p5",
    "L1_DoubleMu3_SQ_ETMHF50_Jet60er2p5_OR_DoubleJet40er2p5",
    "L1_DoubleMu3_SQ_ETMHF60_Jet60er2p5",
    "L1_DoubleMu3_SQ_HTT220er",
    "L1_DoubleMu3_SQ_HTT240er",
    "L1_DoubleMu3_SQ_HTT260er",
    "L1_DoubleMu3_dR_Max1p6_Jet90er2p5_dR_Max0p8",
    "L1_DoubleMu3er2p0_SQ_OS_dR_Max1p6",
    "L1_DoubleMu4_SQ_EG9er2p5",
    "L1_DoubleMu4_SQ_OS",
    "L1_DoubleMu4_SQ_OS_dR_Max1p2",
    "L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6",
    "L1_DoubleMu4p5_SQ_OS",
    "L1_DoubleMu4p5_SQ_OS_dR_Max1p2",
    "L1_DoubleMu4p5er2p0_SQ_OS",
    "L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18",
    "L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7",
    "L1_DoubleMu5_OS_er2p3_Mass_8to14_DoubleEG3er2p1_Mass_Max20",
    "L1_DoubleMu5_SQ_EG9er2p5",
    "L1_DoubleMu5_SQ_OS_dR_Max1p6",
    "L1_DoubleMu8_SQ",
    "L1_DoubleMu9_SQ",
    "L1_DoubleMu_12_5",
    "L1_DoubleMu_15_5_SQ",
    "L1_DoubleMu_15_7",
    "L1_DoubleMu_15_7_Mass_Min1",
    "L1_DoubleMu_15_7_SQ",
    "L1_DoubleTau70er2p1",
    "L1_ETM120",
    "L1_ETM150",
    "L1_ETMHF100",
    "L1_ETMHF100_HTT60er",
    "L1_ETMHF110",
    "L1_ETMHF110_HTT60er",
    "L1_ETMHF120",
    "L1_ETMHF120_HTT60er",
    "L1_ETMHF130",
    "L1_ETMHF130_HTT60er",
    "L1_ETMHF140",
    "L1_ETMHF150",
    "L1_ETMHF70",
    "L1_ETMHF70_HTT60er",
    "L1_ETMHF80",
    "L1_ETMHF80_HTT60er",
    "L1_ETMHF80_SingleJet55er2p5_dPhi_Min2p1",
    "L1_ETMHF80_SingleJet55er2p5_dPhi_Min2p6",
    "L1_ETMHF90",
    "L1_ETMHF90_HTT60er",
    "L1_ETMHF90_SingleJet60er2p5_dPhi_Min2p1",
    "L1_ETMHF90_SingleJet60er2p5_dPhi_Min2p6",
    "L1_ETMHF90_SingleJet80er2p5_dPhi_Min2p1",
    "L1_ETMHF90_SingleJet80er2p5_dPhi_Min2p6",
    "L1_ETT1600",
    "L1_ETT2000",
    "L1_FirstBunchAfterTrain",
    "L1_FirstBunchBeforeTrain",
    "L1_FirstBunchInTrain",
    "L1_FirstCollisionInOrbit",
    "L1_FirstCollisionInTrain",
    "L1_HCAL_LaserMon_Trig",
    "L1_HCAL_LaserMon_Veto",
    "L1_HTT120_SingleLLPJet40",
    "L1_HTT120er",
    "L1_HTT160_SingleLLPJet50",
    "L1_HTT160er",
    "L1_HTT200_SingleLLPJet60",
    "L1_HTT200er",
    "L1_HTT240_SingleLLPJet70",
    "L1_HTT255er",
    "L1_HTT280er",
    "L1_HTT280er_QuadJet_70_55_40_35_er2p5",
    "L1_HTT320er",
    "L1_HTT320er_QuadJet_70_55_40_40_er2p5",
    "L1_HTT320er_QuadJet_80_60_er2p1_45_40_er2p3",
    "L1_HTT320er_QuadJet_80_60_er2p1_50_45_er2p3",
    "L1_HTT360er",
    "L1_HTT400er",
    "L1_HTT450er",
    "L1_IsoEG32er2p5_Mt40",
    "L1_IsoTau52er2p1_QuadJet36er2p5",
    "L1_IsolatedBunch",
    "L1_LastBunchInTrain",
    "L1_LastCollisionInTrain",
    "L1_LooseIsoEG22er2p1_IsoTau26er2p1_dR_Min0p3",
    "L1_LooseIsoEG22er2p1_Tau70er2p1_dR_Min0p3",
    "L1_LooseIsoEG24er2p1_HTT100er",
    "L1_LooseIsoEG24er2p1_IsoTau27er2p1_dR_Min0p3",
    "L1_LooseIsoEG26er2p1_HTT100er",
    "L1_LooseIsoEG26er2p1_Jet34er2p5_dR_Min0p3",
    "L1_LooseIsoEG28er2p1_HTT100er",
    "L1_LooseIsoEG28er2p1_Jet34er2p5_dR_Min0p3",
    "L1_LooseIsoEG30er2p1_HTT100er",
    "L1_LooseIsoEG30er2p1_Jet34er2p5_dR_Min0p3",
    "L1_MinimumBiasHF0",
    "L1_MinimumBiasHF0_AND_BptxAND",
    "L1_Mu10er2p3_Jet32er2p3_dR_Max0p4_DoubleJet32er2p3_dEta_Max1p6",
    "L1_Mu12er2p3_Jet40er2p1_dR_Max0p4_DoubleJet40er2p1_dEta_Max1p6",
    "L1_Mu12er2p3_Jet40er2p3_dR_Max0p4_DoubleJet40er2p3_dEta_Max1p6",
    "L1_Mu18er2p1_Tau24er2p1",
    "L1_Mu18er2p1_Tau26er2p1",
    "L1_Mu18er2p1_Tau26er2p1_Jet55",
    "L1_Mu18er2p1_Tau26er2p1_Jet70",
    "L1_Mu20_EG10er2p5",
    "L1_Mu22er2p1_IsoTau28er2p1",
    "L1_Mu22er2p1_IsoTau30er2p1",
    "L1_Mu22er2p1_IsoTau32er2p1",
    "L1_Mu22er2p1_IsoTau34er2p1",
    "L1_Mu22er2p1_IsoTau36er2p1",
    "L1_Mu22er2p1_IsoTau40er2p1",
    "L1_Mu22er2p1_Tau70er2p1",
    "L1_Mu3_Jet120er2p5_dR_Max0p4",
    "L1_Mu3_Jet16er2p5_dR_Max0p4",
    "L1_Mu3_Jet30er2p5",
    "L1_Mu3_Jet60er2p5_dR_Max0p4",
    "L1_Mu3er1p5_Jet100er2p5_ETMHF30",
    "L1_Mu3er1p5_Jet100er2p5_ETMHF40",
    "L1_Mu3er1p5_Jet100er2p5_ETMHF50",
    "L1_Mu5_EG23er2p5",
    "L1_Mu5_LooseIsoEG20er2p5",
    "L1_Mu6_DoubleEG10er2p5",
    "L1_Mu6_DoubleEG12er2p5",
    "L1_Mu6_DoubleEG15er2p5",
    "L1_Mu6_DoubleEG17er2p5",
    "L1_Mu6_HTT240er",
    "L1_Mu6_HTT250er",
    "L1_Mu7_EG20er2p5",
    "L1_Mu7_EG23er2p5",
    "L1_Mu7_LooseIsoEG20er2p5",
    "L1_Mu7_LooseIsoEG23er2p5",
    "L1_NotBptxOR",
    "L1_QuadJet60er2p5",
    "L1_QuadJet_95_75_65_20_DoubleJet_75_65_er2p5_Jet20_FWD3p0",
    "L1_QuadMu0",
    "L1_QuadMu0_OQ",
    "L1_QuadMu0_SQ",
    "L1_SecondBunchInTrain",
    "L1_SecondLastBunchInTrain",
    "L1_SingleEG10er2p5",
    "L1_SingleEG15er2p5",
    "L1_SingleEG26er2p5",
    "L1_SingleEG28_FWD2p5",
    "L1_SingleEG28er1p5",
    "L1_SingleEG28er2p1",
    "L1_SingleEG28er2p5",
    "L1_SingleEG34er2p5",
    "L1_SingleEG36er2p5",
    "L1_SingleEG38er2p5",
    "L1_SingleEG40er2p5",
    "L1_SingleEG42er2p5",
    "L1_SingleEG45er2p5",
    "L1_SingleEG50",
    "L1_SingleEG60",
    "L1_SingleEG8er2p5",
    "L1_SingleIsoEG24er2p1",
    "L1_SingleIsoEG26er2p1",
    "L1_SingleIsoEG26er2p5",
    "L1_SingleIsoEG28_FWD2p5",
    "L1_SingleIsoEG28er1p5",
    "L1_SingleIsoEG28er2p1",
    "L1_SingleIsoEG28er2p5",
    "L1_SingleIsoEG30er2p1",
    "L1_SingleIsoEG30er2p5",
    "L1_SingleIsoEG32er2p1",
    "L1_SingleIsoEG32er2p5",
    "L1_SingleIsoEG34er2p5",
    "L1_SingleIsoTau32er2p1",
    "L1_SingleJet10erHE",
    "L1_SingleJet120",
    "L1_SingleJet120_FWD2p5",
    "L1_SingleJet120_FWD3p0",
    "L1_SingleJet120er2p5",
    "L1_SingleJet12erHE",
    "L1_SingleJet140er2p5",
    "L1_SingleJet140er2p5_ETMHF90",
    "L1_SingleJet160er2p5",
    "L1_SingleJet180",
    "L1_SingleJet180er2p5",
    "L1_SingleJet200",
    "L1_SingleJet20er2p5_NotBptxOR",
    "L1_SingleJet20er2p5_NotBptxOR_3BX",
    "L1_SingleJet35",
    "L1_SingleJet35_FWD2p5",
    "L1_SingleJet35_FWD3p0",
    "L1_SingleJet35er2p5",
    "L1_SingleJet43er2p5_NotBptxOR_3BX",
    "L1_SingleJet46er2p5_NotBptxOR_3BX",
    "L1_SingleJet60",
    "L1_SingleJet60_FWD2p5",
    "L1_SingleJet8erHE",
    "L1_SingleJet90",
    "L1_SingleJet90_FWD2p5",
    "L1_SingleLooseIsoEG26er1p5",
    "L1_SingleLooseIsoEG26er2p5",
    "L1_SingleLooseIsoEG28_FWD2p5",
    "L1_SingleLooseIsoEG28er1p5",
    "L1_SingleLooseIsoEG28er2p1",
    "L1_SingleLooseIsoEG28er2p5",
    "L1_SingleLooseIsoEG30er1p5",
    "L1_SingleLooseIsoEG30er2p5",
    "L1_SingleMu0_BMTF",
    "L1_SingleMu0_DQ",
    "L1_SingleMu0_EMTF",
    "L1_SingleMu0_OMTF",
    "L1_SingleMu0_Upt10",
    "L1_SingleMu0_Upt10_BMTF",
    "L1_SingleMu0_Upt10_EMTF",
    "L1_SingleMu0_Upt10_OMTF",
    "L1_SingleMu12_DQ_BMTF",
    "L1_SingleMu12_DQ_EMTF",
    "L1_SingleMu12_DQ_OMTF",
    "L1_SingleMu15_DQ",
    "L1_SingleMu18",
    "L1_SingleMu20",
    "L1_SingleMu22",
    "L1_SingleMu22_BMTF",
    "L1_SingleMu22_DQ",
    "L1_SingleMu22_EMTF",
    "L1_SingleMu22_OMTF",
    "L1_SingleMu22_OQ",
    "L1_SingleMu25",
    "L1_SingleMu3",
    "L1_SingleMu5",
    "L1_SingleMu7",
    "L1_SingleMu7_DQ",
    "L1_SingleMuCosmics",
    "L1_SingleMuCosmics_BMTF",
    "L1_SingleMuCosmics_EMTF",
    "L1_SingleMuCosmics_OMTF",
    "L1_SingleMuOpen",
    "L1_SingleMuOpen_BMTF",
    "L1_SingleMuOpen_EMTF",
    "L1_SingleMuOpen_NotBptxOR",
    "L1_SingleMuOpen_OMTF",
    "L1_SingleMuOpen_er1p1_NotBptxOR_3BX",
    "L1_SingleMuOpen_er1p4_NotBptxOR_3BX",
    "L1_SingleMuShower_Nominal",
    "L1_SingleMuShower_Tight",
    "L1_SingleTau120er2p1",
    "L1_SingleTau130er2p1",
    "L1_SingleTau70er2p1",
    "L1_TOTEM_1",
    "L1_TOTEM_2",
    "L1_TOTEM_3",
    "L1_TOTEM_4",
    "L1_TripleEG16er2p5",
    "L1_TripleEG_18_17_8_er2p5",
    "L1_TripleEG_18_18_12_er2p5",
    "L1_TripleJet_100_80_70_DoubleJet_80_70_er2p5",
    "L1_TripleJet_105_85_75_DoubleJet_85_75_er2p5",
    "L1_TripleJet_95_75_65_DoubleJet_75_65_er2p5",
    "L1_TripleMu0",
    "L1_TripleMu0_OQ",
    "L1_TripleMu0_SQ",
    "L1_TripleMu3",
    "L1_TripleMu3_SQ",
    "L1_TripleMu_3SQ_2p5SQ_0",
    "L1_TripleMu_3SQ_2p5SQ_0_Mass_Max12",
    "L1_TripleMu_3SQ_2p5SQ_0_OS_Mass_Max12",
    "L1_TripleMu_4SQ_2p5SQ_0_OS_Mass_Max12",
    "L1_TripleMu_5SQ_3SQ_0OQ",
    "L1_TripleMu_5SQ_3SQ_0OQ_DoubleMu_5_3_SQ_OS_Mass_Max9",
    "L1_TripleMu_5SQ_3SQ_0_DoubleMu_5_3_SQ_OS_Mass_Max9",
    "L1_TripleMu_5_3_3",
    "L1_TripleMu_5_3_3_SQ",
    "L1_TripleMu_5_3p5_2p5",
    "L1_TripleMu_5_3p5_2p5_DoubleMu_5_2p5_OS_Mass_5to17",
    "L1_TripleMu_5_4_2p5_DoubleMu_5_2p5_OS_Mass_5to17",
    "L1_TripleMu_5_5_3",
    "L1_TwoMuShower_Loose",
    "L1_UnpairedBunchBptxMinus",
    "L1_UnpairedBunchBptxPlus",
    "L1_ZeroBias",
    "L1_ZeroBias_copy",
]

def main(nBins):

    # get list of sample names and remove ZeroBias
    sample_names = list(samples.keys())
    if 'ZeroBias' in sample_names:
        sample_names.remove('ZeroBias')

    # get zerobias and filter out training events
    zero_bias = samples['ZeroBias'].getNewDataframe()

    # determine which trigger bits have prescale factor of 1

    # create and fill CICADA score histograms for zerobias
    for i in range(len(cicada_names)):
        print("    CICADA VERSION: ", cicada_names[i])

        histModel = ROOT.RDF.TH1DModel(
            f"anomalyScore_ZeroBias_test_{cicada_names[i]}",
            f"anomalyScore_ZeroBias_test_{cicada_names[i]}",
            nBins,
            min_score_cicada,
            max_score_cicada
        )
        hist = zero_bias_test.Histo1D(histModel, f"{cicada_names[i]}_score")
        hist.Write()

        histModel = ROOT.RDF.TH1DModel(
            f"anomalyScore_ZeroBias_train_{cicada_names[i]}",
            f"anomalyScore_ZeroBias_train_{cicada_names[i]}",
            nBins,
            min_score_cicada,
            max_score_cicada
        )
        hist = zero_bias_train.Histo1D(histModel, f"{cicada_names[i]}_score")
        hist.Write()

    # create and fill HT histograms for zerobias
    print("    HT")
    zero_bias_test = zero_bias_test.Define("sum_mask", "(sumBx==0) && (sumType==1)")
    zero_bias_test = zero_bias_test.Define("HT", "sumEt[sum_mask]")
    zero_bias_train = zero_bias_train.Define("sum_mask", "(sumBx==0) && (sumType==1)")
    zero_bias_train = zero_bias_train.Define("HT", "sumEt[sum_mask]")

    histModel = ROOT.RDF.TH1DModel(
        f"HT_ZeroBias_test",
        f"HT_ZeroBias_test",
        nBins,
        min_score_ht,
        max_score_ht
    )
    hist = zero_bias_test.Histo1D(histModel, "HT")
    hist.Write()

    histModel = ROOT.RDF.TH1DModel(
        f"HT_ZeroBias_train",
        f"HT_ZeroBias_train",
        nBins,
        min_score_ht,
        max_score_ht
    )
    hist = zero_bias_train.Histo1D(histModel, "HT")
    hist.Write()

    output_file.Write()
    output_file.Close()


    # create and write hists for each sample
    for k in range(len(sample_names)):
        print(f"Sample: {sample_names[k]}")
        try:
            output_file = ROOT.TFile(f"hists_240420_{sample_names[k]}.root", "RECREATE")

            rdf = samples[sample_names[k]].getNewDataframe()

            # create and fill CICADA score histograms
            for i in range(len(cicada_names)):
                print("    CICADA VERSION: ", cicada_names[i])

                histModel = ROOT.RDF.TH1DModel(
                    f"anomalyScore_{sample_names[k]}_{cicada_names[i]}",
                    f"anomalyScore_{sample_names[k]}_{cicada_names[i]}",
                    nBins,
                    min_score_cicada,
                    max_score_cicada
                )
                hist = rdf.Histo1D(histModel, f"{cicada_names[i]}_score")
                hist.Write()

            # create and fill HT histogram
            print("   HT")
            rdf = rdf.Define("sum_mask", "(sumBx==0) && (sumType==1)")
            rdf = rdf.Define("HT", "sumEt[sum_mask]")

            histModel = ROOT.RDF.TH1DModel(
                f"HT_{sample_names[k]}",
                f"HT_{sample_names[k]}",
                nBins,
                min_score_ht,
                max_score_ht
            )
            hist = rdf.Histo1D(histModel, "HT")
            hist.Write()

            output_file.Write()
            output_file.Close()
        except Exception:
            print("    Could not create file. Check contents..")


if __name__ == "__main__":

	parser = argparse.ArgumentParser(
        description="This program creates CICADA score and HT histograms"
    )
	parser.add_argument(
        "-n",
        "--n_bins",
        default=100,
        help="number of bins")

	args = parser.parse_args()

	main( args.n_bins)

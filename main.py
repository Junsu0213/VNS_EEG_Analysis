# -*- coding:utf-8 -*-
# Jun-su Park

from Config.config import PainOpenBCIConfig, OpenBCIConfig
from Analysis.data_preprocessing import EEGDataParser
from Analysis.data_analysis import DataAnalysis
from Analysis.data_plot import FigurePlot
from Analysis.data_csv import ConvertCSV

# subject name
data_name = '표지훈'

# # Analysis biomarker feature
# config = PainOpenBCIConfig(data_name=data_name) # Pain biomarker configuration
# EEGDataParser(config=config).data_epoching(artifact_rejection=True)
# DataAnalysis(config=config).data_analysis()
# FigurePlot(config=config).data_plot()
# ConvertCSV(config=config).convert_csv()

# Analysis all feature
config = OpenBCIConfig(data_name=data_name) # PSD FC features configuration
EEGDataParser(config=config).data_epoching(artifact_rejection=True)
DataAnalysis(config=config).data_analysis()
FigurePlot(config=config).data_plot()
ConvertCSV(config=config).convert_csv()

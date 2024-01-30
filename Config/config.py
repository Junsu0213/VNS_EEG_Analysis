# -*- coding:utf-8 -*-
"""
Created on Thu. Jul. 27 12:03:26 2023
@author: PJS
"""


class OpenBCIConfig:
    def __init__(
            self,
            data_path=r'D:\vns_database',
            data_name=None,
            file_name=None,
            fc_method='coh',
            psd_method='welch',
            sfreq=125,
            biomarker_name=None,
            ch_list=None,
            band_freq=None,
            tri_mapping=None,
            roi=None,
    ):
        if ch_list is None:
            ch_list = ['Fp1', 'F7', 'F3', 'T3', 'C3', 'Cz', 'P3', 'O1',
                       'Fp2', 'F4', 'F8', 'C4', 'T4', 'P4', 'O2']
        if band_freq is None:
            band_freq = {'Delta': (0.5, 4), 'Theta': (4, 8),
                         'Alpha': (8, 13), 'Beta': (13, 30), 'Gamma': (30, 50)}
        if tri_mapping is None:
            tri_mapping = {1: "Baseline", 2: "Stimulation", 3: "Recovery"}
        self.data_path = data_path
        self.data_name = data_name
        self.file_name = file_name
        self.fc_method = fc_method
        self.psd_method = psd_method
        self.sfreq = sfreq
        self.biomarker_name = biomarker_name
        self.ch_list = ch_list
        self.band_freq = band_freq
        self.tri_mapping = tri_mapping
        self.roi = roi


class PainOpenBCIConfig:
    def __init__(
            self,
            data_path=r'D:\vns_database',
            data_name=None,
            file_name=None,
            fc_method='coh',
            psd_method='welch',
            sfreq=125,
            biomarker_name='Pain',
            ch_list=None,
            band_freq=None,
            tri_mapping=None,
            roi=None,
    ):
        if ch_list is None:
            ch_list = ['Fp1', 'F7', 'F3', 'T3', 'C3', 'Cz', 'P3', 'O1',
                       'Fp2', 'F4', 'F8', 'C4', 'T4', 'P4', 'O2']
        if band_freq is None:
            band_freq = {'Theta': (4, 8), 'Beta 3': (23, 30)}
        if tri_mapping is None:
            tri_mapping = {1: "Baseline", 2: "Stim 1", 3: "Recovery 1",
                           4: "Stim 2", 5: "Recovery 2"}
        if roi is None:
            roi = {'L-C': [4], 'L-P': [6]}
        self.data_path = data_path
        self.data_name = data_name
        self.file_name = file_name
        self.fc_method = fc_method
        self.psd_method = psd_method
        self.sfreq = sfreq
        self.biomarker_name = biomarker_name
        self.ch_list = ch_list
        self.band_freq = band_freq
        self.tri_mapping = tri_mapping
        self.roi = roi


class MDDOpenBCIConfig:
    def __init__(
            self,
            data_path=r'D:\vns_database',
            data_name=None,
            file_name=None,
            fc_method='wpli',
            psd_method='welch',
            sfreq=125,
            biomarker_name='MDD',
            ch_list=None,
            band_freq=None,
            tri_mapping=None,
            roi=None
    ):
        if ch_list is None:
            ch_list = ['Fp1', 'F7', 'F3', 'T3', 'C3', 'Cz', 'P3', 'O1',
                       'Fp2', 'F4', 'F8', 'C4', 'T4', 'P4', 'O2']
        if band_freq is None:
            band_freq = {'Low alpha': (7, 10)}
        if tri_mapping is None:
            tri_mapping = {1: "Baseline", 2: "Stimulation", 3: "Recovery",
                           4: "Stim 2", 5: "Recovery 2"}
        if roi is None:
            roi = {'L-F': [0, 1, 2, 3], 'L-P': [5]}
        self.data_path = data_path
        self.data_name = data_name
        self.file_name = file_name
        self.fc_method = fc_method
        self.psd_method = psd_method
        self.sfreq = sfreq
        self.biomarker_name = biomarker_name
        self.ch_list = ch_list
        self.band_freq = band_freq
        self.tri_mapping = tri_mapping
        self.roi = roi


class NeuroFeedbackConfig:
    def __init__(
            self,
            data_path=r'D:\vns_database',
            data_name=None,
            file_name=None,
            fc_method='wpli',
            psd_method='welch',
            sfreq=250,
            biomarker_name=None,
            ch_list=None,
            band_freq=None,
            tri_mapping=None,
            roi=None,
    ):
        if ch_list is None:
            ch_list = ['Fp1', 'Fp2', 'Cz', 'C3', 'C4', 'Oz', 'O1', 'O2']
        if band_freq is None:
            band_freq = {'Delta': (0.5, 4), 'Theta': (4, 8),
                         'Alpha': (8, 13), 'Beta': (13, 30), 'Gamma': (30, 50)}
        if tri_mapping is None:
            tri_mapping = {1: "Resting"}
        self.data_path = data_path
        self.data_name = data_name
        self.file_name = file_name
        self.fc_method = fc_method
        self.psd_method = psd_method
        self.sfreq = sfreq
        self.biomarker_name = biomarker_name
        self.ch_list = ch_list
        self.band_freq = band_freq
        self.tri_mapping = tri_mapping
        self.roi = roi
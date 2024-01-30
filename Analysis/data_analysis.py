# -*- coding:utf-8 -*-
"""
Created on Thu. Jul. 27 22:25:45 2023
@author: PJS
"""
import os
import pickle
from Config.config import PainOpenBCIConfig, OpenBCIConfig
import numpy as np
from mne_connectivity import spectral_connectivity_epochs


class DataAnalysis(object):
    def __init__(self, config):
        self.config = config
        self.data_path = config.data_path
        self.data_name = config.data_name
        self.file_name = config.file_name
        self.ch_list = config.ch_list
        self.band_freq = config.band_freq
        self.band = tuple(zip(*tuple(self.band_freq.values())))
        self.fc_method = config.fc_method
        self.psd_method = config.psd_method
        self.roi = config.roi
        self.biomarker_name = config.biomarker_name
        self.tri_mapping = config.tri_mapping

    def data_analysis(self):
        epoch_flist = os.listdir(fr'{self.data_path}\DataBase\{self.data_name}\epoch')
        if self.biomarker_name is not None:
            feature_flist = os.listdir(fr'{self.data_path}\Feature\{self.data_name}\stage\biomarker')
        else:
            feature_flist = os.listdir(fr'{self.data_path}\Feature\{self.data_name}\stage\psd_fc')

        for epoch_f_name in epoch_flist:
            e_f_name = epoch_f_name.split('.')[0]
            bool_list = []
            for feature_file_name in feature_flist:
                f_file_name = feature_file_name.split('_')[0]
                a = (f_file_name == e_f_name)
                bool_list.append(a)
            if any(bool_list):
                pass
            else:
                self.file_name = e_f_name
                print('File name:', self.file_name)
                # biomarker analysis
                if self.biomarker_name is not None:
                    self.biomarker_analysis()
                # PSD, FC analysis
                else:
                    self.psd_fc_feature_analysis()

    def psd_fc_feature_analysis(self):
        with open(fr'{self.data_path}\DataBase\{self.data_name}\epoch\{self.file_name}.pickle', 'rb') as f:
            data = pickle.load(f)

        # # stage analysis (baseline, stim1, recovery1, stim2, recovery2)
        stage_dict = {}
        for i in range(1, 1+len(self.tri_mapping.keys())):

            stage_name = self.tri_mapping[i]
            stage_data = data[stage_name]

            # PSD analysis --> (channel, band frequency)
            psd_data = self.psd_analysis(epoch=stage_data)

            # FC analysis --> (channel, channel, band frequency)
            _, adj_mat = self.fc_analysis(epoch=stage_data)

            stage_dict[stage_name] = {'psd': psd_data, 'fc': adj_mat}

        # save stage data
        with open(fr'{self.data_path}\Feature\{self.data_name}\stage\psd_fc\{self.file_name}_psd_fc.pickle', 'wb') as f:
            pickle.dump(stage_dict, f)

    def biomarker_analysis(self):
        with open(fr'{self.data_path}\DataBase\{self.data_name}\epoch\{self.file_name}.pickle', 'rb') as f:
            data = pickle.load(f)

        # # sequential analysis: 5 minute time windows with a 10 second interval shift
        whole_epoch_data = data['whole epoch data']
        shift_len = int((whole_epoch_data.get_data().shape[0]-150)/5)

        # 30 epoch: 1 minute
        time_window = 30 * 5
        # 5 epoch: 10 second
        time_interval = 5

        # number of biomarkers
        biomarker_num = len(self.band_freq.keys())

        if biomarker_num > 1:
            bm_list = [[] for _ in range(len(self.band_freq.keys()))]
        else:
            bm_list = []

        for trial in range(shift_len):

            # 10 second interval shift
            split_epoch = whole_epoch_data[time_interval*trial:time_window+time_interval*trial]

            # FC analysis
            _, adj_mat = self.fc_analysis(epoch=split_epoch)

            # ROI (average)
            roi_f_mat = self.roi_conn(adj_mat=adj_mat)

            # append biomarker value
            if biomarker_num > 1:
                for i in range(biomarker_num):
                    bm_data = roi_f_mat[4*i+1]
                    bm_list[i].append(bm_data)
            else:
                bm_list.append(roi_f_mat[1])

        seq_dict = {}
        if biomarker_num > 1:
            for i, band in zip(range(biomarker_num), self.band_freq.keys()):
                seq_dict[f'{band}-{list(self.roi.keys())[0]}-{list(self.roi.keys())[1]}'] = bm_list[i]
        else:
            seq_dict[f'{list(self.band_freq.keys())[0]}-{list(self.roi.keys())[0]}-{list(self.roi.keys())[1]}'] = bm_list

        seq_dict['event list'] = data['event list']

        # save sequential data
        with open(fr'{self.data_path}\Feature\{self.data_name}\sequential\{self.file_name}_{self.biomarker_name}.pickle', 'wb') as f:
            pickle.dump(seq_dict, f)

        # # stage analysis (baseline, stim1, recovery1, stim2, recovery2)
        stage_dict = {}
        for i in range(1, 1+len(self.tri_mapping.keys())):

            bm_dict = {}
            stage_name = self.tri_mapping[i]
            stage_data = data[stage_name]

            # FC analysis
            _, adj_mat = self.fc_analysis(epoch=stage_data)

            # ROI (average)
            roi_f_mat = self.roi_conn(adj_mat=adj_mat)

            # append biomarker value
            if biomarker_num > 1:
                for i, band in zip(range(biomarker_num), self.band_freq.keys()):
                    bm_data = roi_f_mat[4*i+1]
                    bm_dict[f'{band}-{list(self.roi.keys())[0]}-{list(self.roi.keys())[1]}'] = bm_data
            else:
                bm_data = (roi_f_mat[1])
                bm_dict[f'{list(self.band_freq.keys())[0]}-{list(self.roi.keys())[0]}-{list(self.roi.keys())[1]}'] = bm_data
            stage_dict[stage_name] = bm_dict

        # save stage data
        with open(fr'{self.data_path}\Feature\{self.data_name}\stage\biomarker\{self.file_name}_{self.biomarker_name}.pickle', 'wb') as f:
            pickle.dump(stage_dict, f)

    def psd_analysis(self, epoch, relative=True):
        # Power spectral density analysis
        power = epoch.compute_psd(method=self.psd_method, fmin=min(self.band[0]), fmax=max(self.band[1]))

        # Average the spectra across epochs.
        power = power.average()

        # total power
        total_power = power.get_data().sum(axis=1)

        # band name
        band_name = self.band_freq.keys()

        # psd list
        nor_power = []
        for i in band_name:
            fmin, fmax = self.band_freq[i]
            # normalized psd
            if relative:
                nor_power_ = power.get_data(fmin=fmin, fmax=fmax).sum(axis=1)/total_power
            # raw psd
            else:
                nor_power_ = power.get_data(fmin=fmin, fmax=fmax).sum(axis=1)
            nor_power.append(nor_power_)

        # psd (channel, band frequency)
        nor_power = np.array(nor_power).swapaxes(1, 0)
        return nor_power

    def fc_analysis(self, epoch):
        # Functional connectivity analysis
        con = spectral_connectivity_epochs(data=epoch, names=self.ch_list, method=self.fc_method,
                                           fmin=self.band[0], fmax=self.band[1], faverage=True,
                                           mt_adaptive=True, n_jobs=1)

        # Connectivity features (channel*channel, band frequency)
        conmat = con.get_data()

        # Adjacency matrix (channel, channel, band frequency)
        adj_mat = con.get_data(output='dense')
        return conmat, adj_mat

    def roi_conn(self, adj_mat):
        # ROI connectivity mean
        # transpose sum
        def transpose(con_data):
            tr_data = np.transpose(con_data)
            conn_data = con_data + tr_data
            return conn_data

        # frequency band information
        band_names = list(self.band_freq.keys())

        # ROI information
        roi_dic = self.roi
        roi_chlist = list(self.roi.keys())

        flat_mat = []
        for band, band_num in zip(band_names, range(len(band_names))):
            # data transpose
            conn = transpose(adj_mat[:, :, band_num])
            a = []
            for i in roi_chlist:
                for j in roi_chlist:
                    # roi 별 mean 값
                    num_conn = len(roi_dic[i]) * len(roi_dic[j])
                    if j == i:
                        conn_ = conn[roi_dic[i], :]
                        roi_conn = np.array(np.sum(conn_[:, roi_dic[j]]) / (num_conn - (len(roi_dic[j])))).reshape(1, 1)
                        a = np.append(a, roi_conn)
                    else:
                        conn_ = conn[roi_dic[i], :]
                        roi_conn = np.array(np.sum(conn_[:, roi_dic[j]]) / (num_conn)).reshape(1, 1)
                        a = np.append(a, roi_conn)
            flat_mat = np.append(flat_mat, a)
            # print(flat_mat.shape) # --> (roi_num*roi_num*band) ex. (2*2*2)
        return flat_mat


if __name__ == '__main__':
    data_name = 'LGH'
    config = PainOpenBCIConfig(data_name=data_name)
    # config = OpenBCIConfig(data_name=data_name)
    DataAnalysis(config=config).data_analysis()
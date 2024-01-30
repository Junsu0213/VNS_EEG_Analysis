# -*- coding:utf-8 -*-
"""
Created on Thu. Aug. 03 11:48:21 2023
@author: PJS
"""
import os
import glob
import csv
import pickle
import pandas as pd
from Config.config import OpenBCIConfig, PainOpenBCIConfig


class ConvertCSV(object):
    def __init__(self, config):
        self.config = config
        self.data_path = config.data_path
        self.data_name = config.data_name
        self.file_name = config.file_name
        self.biomarker_name = config.biomarker_name
        self.ch_list = config.ch_list
        self.band_freq = config.band_freq
        self.stage_list = ['baseline', 'stimulation', 'recovery']

    def convert_csv(self):
        # biomarker data
        if self.biomarker_name is not None:
            # csv file이 없는 경우 각 stage에 따른 csv 파일 및 columns 생성
            if not os.listdir(fr'{self.data_path}\CSV\{self.biomarker_name}'):
                demographic = ['subject', 'date']
                path = glob.glob(fr'{self.data_path}\Feature\{self.data_name}\stage\biomarker\*_{self.biomarker_name}.pickle')[0]
                with open(path, 'rb') as f:
                    data = pickle.load(f)
                biomarker_column = list(data['Baseline'].keys())
                column = demographic + biomarker_column
                df = pd.DataFrame(columns=column)
                for stage in self.stage_list:
                    df.to_csv(fr'{self.data_path}\CSV\{self.biomarker_name}\{stage}.csv', index=False)

            feature_flist = os.listdir(fr'{self.data_path}\Feature\{self.data_name}\stage\biomarker')
            df = pd.read_csv(fr'{self.data_path}\CSV\{self.biomarker_name}\baseline.csv')
            filtered_rows = df[df['subject'] == self.data_name]
            date_list = list(filtered_rows['date'])

        # PSD, FC data
        else:
            # csv file이 없는 경우 각 stage에 따른 csv 파일 및 columns 생성
            if not os.listdir(fr'{self.data_path}\CSV\psd_fc'):
                demographic = ['subject', 'date']
                psd_column = self.make_psd_columns(ch_name=self.ch_list, band_name=self.band_freq)
                fc_column = self.make_fc_columns(ch_name=self.ch_list, band_name=self.band_freq)
                column = demographic + psd_column + fc_column
                df = pd.DataFrame(columns=column)
                for stage in self.stage_list:
                    df.to_csv(fr'{self.data_path}\CSV\psd_fc\{stage}.csv', index=False)

            feature_flist = os.listdir(fr'{self.data_path}\Feature\{self.data_name}\stage\psd_fc')
            df = pd.read_csv(fr'{self.data_path}\CSV\psd_fc\baseline.csv')
            filtered_rows = df[df['subject'] == self.data_name]
            date_list = list(filtered_rows['date'])

        for f_f_name in feature_flist:
            f_name = f_f_name.split('_')[0]
            bool_list = []
            for date in date_list:
                a = (date == f_name)
                bool_list.append(a)
            if any(bool_list):
                pass
            else:
                self.file_name = f_name
                print('File name:', self.file_name)
                # biomarker csv
                if self.biomarker_name is not None:
                    self.biomarker_feature_csv()
                # PSD, FC csv
                else:
                    self.psd_fc_feature_csv()

    def psd_fc_feature_csv(self):
        # csv file이 없는 경우 각 stage에 따른 csv 파일 및 columns 생성
        if not os.listdir(fr'{self.data_path}\CSV\psd_fc'):
            demographic = ['subject', 'date']
            psd_column = self.make_psd_columns(ch_name=self.ch_list, band_name=self.band_freq)
            fc_column = self.make_fc_columns(ch_name=self.ch_list, band_name=self.band_freq)
            column = demographic + psd_column + fc_column
            df = pd.DataFrame(columns=column)
            for stage in self.stage_list:
                df.to_csv(fr'{self.data_path}\CSV\psd_fc\{stage}.csv', index=False)

        with open(fr'{self.data_path}\Feature\{self.data_name}\stage\psd_fc\{self.file_name}_psd_fc.pickle', 'rb') as f:
            data = pickle.load(f)
        stage = data.keys()
        # VNS stage
        for i, stage in zip(stage, self.stage_list):
            psd = data[i]['psd']
            fc = data[i]['fc']
            psd = psd.reshape(len(self.ch_list) * len(self.band_freq), order='F')
            fc = fc.reshape(len(self.ch_list) * len(self.ch_list), len(self.band_freq))
            fc = fc.reshape(len(self.ch_list) * len(self.ch_list) * len(self.band_freq), order='F')
            data_ = [self.data_name, self.file_name] + list(psd) + list(fc)

            f_name = open(fr'{self.data_path}\CSV\psd_fc\{stage}.csv', 'a', newline='')
            wr_name = csv.writer(f_name)
            wr_name.writerow(data_)

    def biomarker_feature_csv(self):
        # csv file이 없는 경우 각 stage에 따른 csv 파일 및 columns 생성
        if not os.listdir(fr'{self.data_path}\CSV\{self.biomarker_name}'):
            demographic = ['subject', 'date']
            with open(fr'{self.data_path}\Feature\{self.data_name}\stage\biomarker\{self.file_name}_{self.biomarker_name}.pickle',
                      'rb') as f:
                data = pickle.load(f)
            biomarker_column = list(data['Baseline'].keys())
            column = demographic + biomarker_column
            df = pd.DataFrame(columns=column)
            for stage in self.stage_list:
                df.to_csv(fr'{self.data_path}\CSV\{self.biomarker_name}\{stage}.csv', index=False)

        with open(fr'{self.data_path}\Feature\{self.data_name}\stage\biomarker\{self.file_name}_{self.biomarker_name}.pickle', 'rb') as f:
            data = pickle.load(f)
        stage = data.keys()
        # VNS stage
        for i, stage in zip(stage, self.stage_list):
            biomarker_data = []
            for j in data[i].keys():
                biomarker_data.append(data[i][j])
            data_ = [self.data_name, self.file_name] + biomarker_data
            f_name = open(fr'{self.data_path}\CSV\{self.biomarker_name}\{stage}.csv', 'a', newline='')
            wr_name = csv.writer(f_name)
            wr_name.writerow(data_)

    @staticmethod
    def make_fc_columns(band_name, ch_name, data_type=None):
        node_name = []
        if data_type is not None:
            for band in band_name:
                for i in ch_name:
                    for j in ch_name:
                        name = data_type + band + '-' + i + '-' + j
                        node_name.append(name)
        else:
            for band in band_name:
                for i in ch_name:
                    for j in ch_name:
                        name = band + '-' + i + '-' + j
                        node_name.append(name)
        column = node_name
        return column

    @staticmethod
    def make_psd_columns(band_name, ch_name, data_type=None):
        node_name = []
        if data_type is not None:
            for band in band_name:
                for i in ch_name:
                    name = data_type + '-' + band + '-' + i
                    node_name.append(name)
            column = node_name
        else:
            for band in band_name:
                for i in ch_name:
                    name = band + '-' + i
                    node_name.append(name)
            column = node_name
        return column


if __name__ == '__main__':
    data_name = 'LGH'
    # config = PainOpenBCIConfig(data_name=data_name)
    config = OpenBCIConfig(data_name=data_name)
    ConvertCSV(config=config).convert_csv()

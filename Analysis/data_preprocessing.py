# -*- coding:utf-8 -*-
"""
Created on Thu. Jul. 27 17:47:31 2023
@author: PJS
"""
import pickle
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from brainflow.data_filter import DataFilter
import mne
from mne.preprocessing import ICA
from Config.config import PainOpenBCIConfig
import matplotlib
matplotlib.use('Qt5Agg')


# epoch 데이터는 mne.concatenate_raws 함수로 복원가능
class EEGDataParser(object):
    def __init__(self, config):
        self.config = config
        self.data_path = config.data_path
        self.data_name = config.data_name
        self.file_name = config.file_name
        self.tri_mapping = config.tri_mapping
        self.ch_list = config.ch_list
        self.sfreq = config.sfreq

    def data_epoching(self, artifact_rejection=True):
        try:
            os.makedirs(fr'{self.data_path}\Feature\{self.data_name}\stage\biomarker')
            os.mkdir(fr'{self.data_path}\Feature\{self.data_name}\stage\psd_fc')
            os.mkdir(fr'{self.data_path}\Feature\{self.data_name}\sequential')
            os.makedirs(fr'{self.data_path}\Figure\{self.data_name}\stage\biomarker')
            os.mkdir(fr'{self.data_path}\Figure\{self.data_name}\stage\psd_fc')
            os.mkdir(fr'{self.data_path}\Figure\{self.data_name}\sequential')
            os.mkdir(fr'{self.data_path}\DataBase\{self.data_name}\epoch')
            os.mkdir(fr'{self.data_path}\CSV\psd_fc')
        except:
            pass

        path = fr'{self.data_path}\DataBase\{self.data_name}'
        raw_flist = os.listdir(fr'{path}\raw')
        filt_flist = os.listdir(fr'{path}\epoch')

        for file_name in raw_flist:
            file_name = file_name.split('.')[0]
            bool_list = []
            for filt_file_name in filt_flist:
                filt_file_name = filt_file_name.split('.')[0]
                a = (filt_file_name == file_name)
                bool_list.append(a)
            if any(bool_list):
                pass
            else:
                self.file_name = file_name
                print('File name:', self.file_name)
                self.data_preprocessing(artifact_rejection=artifact_rejection)

    def data_preprocessing(self, eeg_product='openbci', artifact_rejection=True):
        try:
            os.makedirs(fr'{self.data_path}\Feature\{self.data_name}\stage\biomarker')
            os.mkdir(fr'{self.data_path}\Feature\{self.data_name}\stage\psd_fc')
            os.mkdir(fr'{self.data_path}\Feature\{self.data_name}\sequential')
            os.makedirs(fr'{self.data_path}\Figure\{self.data_name}\stage\biomarker')
            os.mkdir(fr'{self.data_path}\Figure\{self.data_name}\stage\psd_fc')
            os.mkdir(fr'{self.data_path}\Figure\{self.data_name}\sequential')
            os.mkdir(fr'{self.data_path}\DataBase\{self.data_name}\epoch')
            os.mkdir(fr'{self.data_path}\CSV\psd_fc')
        except:
            pass

        subject_epoch_data = {}
        # select EEG product
        if eeg_product == 'openbci':
            try:
                data = DataFilter.read_file(fr'{self.data_path}\Database\{self.data_name}\raw\{self.file_name}.csv')
            except:
                data = pd.read_csv(fr'{self.data_path}\Database\{self.data_name}\raw\{self.file_name}.csv')
                data = np.array(data).transpose()
            # EEG data
            eeg_data = data[1:16, :] / 1e6

            # creat EEG information
            eeg_info = mne.create_info(ch_names=self.ch_list, sfreq=self.sfreq, ch_types="eeg")
            data_ = mne.io.RawArray(eeg_data, info=eeg_info)

            # filtering
            filt_data = data_.copy().filter(l_freq=.5, h_freq=60.)

            # set montage
            montage = mne.channels.make_standard_montage('standard_1020')
            filt_data.set_montage(montage)

            # # evnet annotation
            # trigger list
            tri_list = self.trigger_list(raw=data)
            # events list: minute
            event_list = self.event_list(raw=data)
            # make annotation data
            annot_from_events = mne.annotations_from_events(events=tri_list, event_desc=self.tri_mapping,
                                                            sfreq=self.sfreq)
            # event duration
            duration = self.set_duration(tri_dict=self.tri_mapping, event_list=event_list)

            # set event duration
            annot_from_events.set_durations(duration)

            # independent component analysis (artifact remove)
            ica = ICA(n_components=15, max_iter='auto', random_state=7)
            ica.fit(filt_data)

            # muscle artifacts removing
            muscle_idx_auto, scores = ica.find_bads_muscle(filt_data)

            # muscle artifacts ICA scoring plot
            print('Automatically found muscle artifact ICA components: '
                  f'{muscle_idx_auto}')

            # apply ICA
            ica.apply(filt_data, exclude=muscle_idx_auto)

            # artifact rejection
            if artifact_rejection:
                # removed artifact signal
                filt_data.plot(duration=30., start=tri_list[0][0]/self.sfreq, highpass=0.5, lowpass=40.)
                plt.show()

            # crop by annotations
            crop_data_list = filt_data.crop_by_annotations(annotations=annot_from_events)

            # whole data
            epoch_data = self.epoching(data=filt_data)
            subject_epoch_data['whole epoch data'] = epoch_data

            # crop data
            for state_data, state_num in zip(crop_data_list, self.tri_mapping.keys()):
                epoch_state_data = self.epoching(data=state_data, artifact_rejection=artifact_rejection)
                subject_epoch_data[self.tri_mapping[state_num]] = epoch_state_data

            subject_epoch_data['event list'] = event_list

            with open(fr'{self.data_path}\Database\{self.data_name}\epoch\{self.file_name}.pickle', 'wb') as f:
                pickle.dump(subject_epoch_data, f)

        return subject_epoch_data

    @staticmethod
    # epoch trigger list
    def trigger_list(raw):
        trigger = raw[-1, :]
        num = 0
        tri_list = []
        for i in trigger:
            i = int(i)
            if i == 0:
                pass
            else:
                tri = [num, 0, i]
                tri_list.append(tri)
            num += 1
        tri_list = np.array(tri_list)
        return tri_list

    @staticmethod
    def event_list(raw):
        trigger = raw[-1, 1:].reshape(1, -1)
        events = np.where(trigger > 0)[1]
        event_num = 0
        event_list = []
        while event_num < len(events):
            try:
                event_time = (events[event_num + 1] - events[event_num]) / (60 * 125)
            except IndexError:
                event_time = (raw.shape[1] - events[event_num]) / (60 * 125)
            event_list.append(int(event_time))
            event_num += 1
        return event_list

    @staticmethod
    def set_duration(tri_dict, event_list):
        duration_dict = {}
        for tri_num, duration in zip(tri_dict.keys(), event_list):
            duration_dict[tri_dict[tri_num]] = duration*60
        return duration_dict

    @staticmethod
    def epoching(data, epoch_duration=2., artifact_rejection=False):
        epoched = mne.make_fixed_length_epochs(raw=data, duration=epoch_duration+0.2,
                                               reject_by_annotation=artifact_rejection)
        return epoched


if __name__ == "__main__":
    data_name = 'LYS'
    config = PainOpenBCIConfig(data_name=data_name)
    EEGDataParser(config=config).data_epoching(artifact_rejection=True)

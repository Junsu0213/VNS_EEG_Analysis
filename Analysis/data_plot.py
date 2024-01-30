# -*- coding:utf-8 -*-
"""
Created on Thu. Aug. 03 17:11:50 2023
@author: PJS
"""
import pickle
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import warnings
import matplotlib
import mne
from mne_connectivity.viz import plot_connectivity_circle
from Config.config import PainOpenBCIConfig, OpenBCIConfig


class FigurePlot(object):
    def __init__(self, config):
        self.config = config
        self.data_path = config.data_path
        self.data_name = config.data_name
        self.file_name = config.file_name
        self.biomarker_name = config.biomarker_name
        self.tri_mapping = config.tri_mapping
        self.ch_list = config.ch_list
        self.fc_method = config.fc_method
        self.psd_method = config.psd_method
        self.data_name = config.data_name
        self.band_freq = config.band_freq
        self.band_keys = self.band_freq.keys()
        self.band_num = len(self.band_keys)

    def data_plot(self):
        if self.biomarker_name is not None:
            feature_flist = os.listdir(fr'{self.data_path}\Feature\{self.data_name}\sequential')
            figure_flist = os.listdir(fr'{self.data_path}\Figure\{self.data_name}\sequential')
        else:
            feature_flist = os.listdir(fr'{self.data_path}\Feature\{self.data_name}\stage\psd_fc')
            figure_flist = os.listdir(fr'{self.data_path}\Figure\{self.data_name}\stage\psd_fc')

        for feature_f_name in feature_flist:
            f_name = feature_f_name.split('_')[0]
            bool_list = []
            for figure_file_name in figure_flist:
                f_file_name = figure_file_name.split('_')[0]
                a = (f_file_name == f_name)
                bool_list.append(a)
            if any(bool_list):
                pass
            else:
                self.file_name = f_name
                print('File name:', self.file_name)
                # sequential plot
                if self.biomarker_name is not None:
                    self.sequential_data_plot()
                # PSD, FC plot
                else:
                    self.psd_fc_plot()

    # sequential data plot (single data)
    def sequential_data_plot(self):
        with open(rf'{self.data_path}\Feature\{self.data_name}\sequential\{self.file_name}_{self.biomarker_name}.pickle', 'rb') as f:
            seq_data = pickle.load(f)

        fig_name_list = list(seq_data.keys())[:-1]

        for fig_name in fig_name_list:
            seq_fc_data = seq_data[fig_name]
            band_name = fig_name.split('-')[0]
            event_list = seq_data['event list']
            self.sequential_plot(event_time=event_list, seq_fc_data=seq_fc_data, band=band_name)

    # sequential figure
    def sequential_plot(self, event_time, seq_fc_data, band):
        length = len(self.tri_mapping.keys())
        plt.figure(figsize=(12, 5))
        sns.set()
        sns.set_palette("muted")
        warnings.filterwarnings("ignore", category=matplotlib.MatplotlibDeprecationWarning)
        for i in range(length):
            if i == 0:
                data = seq_fc_data[:event_time[i] * 6 - 15 + 1]
                x = np.linspace(0, event_time[i], len(data))
            elif i != (length - 1):
                data = seq_fc_data[sum(event_time[:i - 1]) * 6 - 15:sum(event_time[:i]) * 6 - 15 + 1]
                x = np.linspace(sum(event_time[:i - 1]), sum(event_time[:i]), len(data))
            else:
                data = seq_fc_data[sum(event_time[:i - 1]) * 6 - 15:]
                x = np.linspace(sum(event_time[:i - 1]), sum(event_time[:i]), len(data))
            sns.lineplot(x=x, y=data, label=self.tri_mapping[i + 1], linewidth=3)

        plt.legend(fontsize=13)

        plt.tick_params(axis='y', direction="inout", labelsize=13, length=10, pad=7)
        plt.tick_params(axis='x', direction="inout", labelsize=13, length=10, pad=7)
        plt.xlabel('time (m)', fontdict={'size': 10})

        # Pain
        if self.biomarker_name == "Pain":
            plt.title("Left Centro-parietal FC ({})".format(band))
            plt.ylabel('{}'.format(band), fontdict={'size': 10})

        # Major depressive disorder
        elif self.biomarker_name == "MDD":
            plt.axhline(y=0.481, color='b', linewidth=1, linestyle='--')
            plt.text(0.4, 0.481, 'Control Group', fontsize=10, va='center', ha='center', backgroundcolor='w', color='b')
            plt.axhline(y=0.314, color='r', linewidth=1, linestyle='--')
            plt.text(0.4, 0.314, 'MDD Group', fontsize=10, va='center', ha='center', backgroundcolor='w', color='r')
            plt.title("Depression FC biomarker", fontdict={'size': 15})
            plt.ylabel('LHCx [a.u]', fontdict={'size': 10})

        # Schizophrenia
        elif self.biomarker_name == "Schizophrenia":
            plt.axhline(y=0.15, color='b', linewidth=1, linestyle='--')
            plt.text(3.0, 0.15, 'Low Schizotypy Group', fontsize=10, va='center', ha='center', backgroundcolor='w', color='b')
            plt.axhline(y=0.09, color='r', linewidth=1, linestyle='--')
            plt.text(3.0, 0.09, 'High Schizotypy Group', fontsize=10, va='center', ha='center', backgroundcolor='w', color='r')
            plt.title("Schizotypy FC biomarker", fontdict={'size': 15})
            plt.ylabel('Right intra-hemispheric \n connectivity (wPLI)', fontdict={'size': 10})

        plt.tight_layout()
        plt.savefig(rf'{self.data_path}\Figure\{self.data_name}\sequential\{self.file_name}_{self.biomarker_name}_{band}.png', dpi=300)

    def psd_fc_plot(self):
        try:
            os.makedirs(fr'{self.data_path}\Figure\{self.data_name}\stage\psd_fc\{self.file_name}')
            os.mkdir(fr'{self.data_path}\Figure\{self.data_name}\stage\psd_fc\{self.file_name}\circular')
            os.mkdir(fr'{self.data_path}\Figure\{self.data_name}\stage\psd_fc\{self.file_name}\heatmap')
            os.mkdir(fr'{self.data_path}\Figure\{self.data_name}\stage\psd_fc\{self.file_name}\psd')
        except:
            pass
        with open(rf'{self.data_path}\Feature\{self.data_name}\stage\psd_fc\{self.file_name}_psd_fc.pickle', 'rb') as f:
            stage_data = pickle.load(f)
        stage_list = list(stage_data.keys())

        for stage in stage_list:
            data = stage_data[stage]
            psd = data['psd']
            adj = data['fc']
            self.fc_heatmap(adj_mat=adj, stage=stage)
            self.fc_circular(adj_mat=adj, stage=stage)
            self.psd_topo(psd_data=psd, stage=stage)

    # heatmap
    def fc_heatmap(self, adj_mat, stage, fsize=30, cbar=True, cmap='RdBu_r', pvalue=False, cbar_range=False):

        if pvalue:
            fig, axes = plt.subplots(nrows=1, ncols=self.band_num, figsize=(8.3*self.band_num, 9.2), constrained_layout=True)
        else:
            fig, axes = plt.subplots(nrows=1, ncols=self.band_num, figsize=(8.3*self.band_num, 10), constrained_layout=True)

        # band 별 adjacency matrix plotting
        for col in range(self.band_num):
            # heatmap plotting
            ax = axes[col]
            conn_df = pd.DataFrame(adj_mat[:, :, col], self.ch_list, self.ch_list)
            if cbar_range:
                bar_range = abs(np.array(conn_df)).max()
                sns.heatmap(conn_df, ax=ax, xticklabels=1, yticklabels=1, cbar=cbar,
                            cbar_kws=dict(use_gridspec=False, location="bottom"), cmap=cmap, vmin=-bar_range,
                            vmax=bar_range)
            else:
                sns.heatmap(conn_df, ax=ax, xticklabels=1, yticklabels=1, cbar=cbar, cmap=cmap,
                            cbar_kws=dict(use_gridspec=False, location="bottom"))
            sns.set(font_scale=2)
            ax.set_title(label=list(self.band_keys)[col], fontdict={'fontsize': 25})
            ax.set_xticklabels(ax.get_xticklabels(), fontsize=25, rotation=90)
            ax.set_yticklabels(ax.get_yticklabels(), fontsize=25, rotation=0)
        plt.suptitle(f'{stage}', fontsize=fsize)
        plt.savefig(fname=fr"{self.data_path}\Figure\{self.data_name}\stage\psd_fc\{self.file_name}\heatmap\{stage}_{self.fc_method}.png", dpi=300)

    # circular plot
    def fc_circular(self, adj_mat, stage, node_num=10):

        for band, col in zip(self.band_keys, range(self.band_num)):
            fig, axes = plot_connectivity_circle(con=adj_mat[:, :, col], node_names=self.ch_list, n_lines=node_num,
                                                 title=f'{stage} ({band})',
                                                 colorbar_size=0.5, colorbar_pos=(0, 0.4),
                                                 facecolor='white', textcolor='black', colormap='RdBu_r',
                                                 fontsize_colorbar=10, fontsize_names=10,
                                                 fontsize_title=20, show=False)
            fig.savefig(fr'{self.data_path}\Figure\{self.data_name}\stage\psd_fc\{self.file_name}\circular\{stage}_{self.fc_method}_{band}.png', facecolor='white', dpi=300)

    # psd plot
    def psd_topo(self, psd_data, stage, cbar=True):
        fig, axes = plt.subplots(1, self.band_num, figsize=(4 * self.band_num, 6))
        axes = axes.reshape(-1)
        for band, col in zip(self.band_keys, range(self.band_num)):
            im = self.psd_based_topography(ax=axes[col],
                                           power=psd_data[:, col],
                                           title=list(self.band_keys)[col])
            if cbar:
                cb = fig.colorbar(im[0], ax=axes[col], orientation='horizontal', pad=0.05)
                cb.ax.tick_params(labelsize=15)
            else:
                pass
        plt.suptitle(f'{stage}', fontsize=35)
        plt.savefig(fname=fr'{self.data_path}\Figure\{self.data_name}\stage\psd_fc\{self.file_name}\psd\{stage}_{self.psd_method}.png', dpi=300)

    def psd_based_topography(self, ax, power, title=None):

        bio_semi_montage = mne.channels.make_standard_montage('standard_1005')
        vmax = max(power)
        vmin = min(power)
        fake_info = mne.create_info(ch_names=self.ch_list, sfreq=200, ch_types='eeg')
        fake_info.set_montage(bio_semi_montage)
        ax.set_title(title)
        ax.title.set_size(20)
        im = mne.viz.plot_topomap(power, fake_info, axes=ax, cmap='RdBu_r', names=self.ch_list, #mask=np.full(len(ch_list), True), mask_params={'markersize': 30},
                                  ch_type='eeg', image_interp='cubic', show=False, vlim=(vmin, vmax))
        return im


if __name__ == '__main__':
    data_name = 'LGH'
    # sequential biomarker feature plot
    config = PainOpenBCIConfig(data_name=data_name)
    FigurePlot(config=config).data_plot()

    # # PSD, FC figure plot
    # config = OpenBCIConfig(data_name=data_name)
    # FigurePlot(config=config).data_plot()

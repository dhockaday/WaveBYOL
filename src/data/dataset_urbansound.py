from torch.utils.data import Dataset
import src.utils.interface_file_io as file_io
import src.utils.interface_audio_io as audio_io
import src.utils.interface_audio_augmentation as audio_augmentation
import numpy as np
import random
import pandas as pd
import natsort


def get_acoustic_dict(acoustic_list):
    acoustic_dict = {}
    for idx, key in enumerate(acoustic_list):
        acoustic_dict[str(key)] = idx
    return acoustic_dict


def get_audio_file_with_acoustic_info(file_list, index):
    audio_file = get_audio_file_path(file_list, index)
    filename = audio_file.split('/')[5]
    acoustic_id = filename.split('-')[1]
    return audio_file, filename, acoustic_id



def get_audio_file_path(file_list, index):
    audio_file = file_list[index]
    return audio_file[4:]


def load_waveform(audio_file, required_sampling_rate):
    waveform, sampling_rate = audio_io.audio_loader(audio_file)

    assert(
        sampling_rate == required_sampling_rate
    ), "sampling rate is not consistent throughout the dataset"
    return waveform


class UrbanSound8KWaveformDatasetByWaveBYOLTypeA(Dataset):
    def __init__(self, file_path, audio_window=20480, sampling_rate=16000, augmentation=[1, 2, 3, 4, 5, 6],
                 augmentation_count=5, metadata="./dataset/UrbanSound8K/metadata/UrbanSound8K.csv",):
        super(UrbanSound8KWaveformDatasetByWaveBYOLTypeA, self).__init__()
        self.file_path = file_path
        self.audio_window = audio_window
        self.sampling_rate = sampling_rate
        self.augmentation = augmentation
        self.augmentation_count = augmentation_count
        self.file_list = file_io.read_txt2list(self.file_path)

        # data file list
        id_data = open(self.file_path, 'r')
        self.file_list = [x.strip() for x in id_data.readlines()]
        id_data.close()

        self.metadata = None
        if metadata is not None:
            self.metadata = pd.read_csv(metadata)
        self.acoustic_list = natsort.natsorted(list(set(self.metadata['classID'])))
        self.acoustic_dict = get_acoustic_dict(self.acoustic_list)

    def __len__(self):
        return len(self.file_list)

    def __getitem__(self, index):
        audio_file, filename, acoustic_id = get_audio_file_with_acoustic_info(self.file_list, index)
        waveform01 = audio_io.audio_adjust_length(load_waveform(audio_file, self.sampling_rate),
                                                  self.audio_window,
                                                  fit=False)

        pick01 = np.random.randint(waveform01.shape[1] - self.audio_window + 1)
        waveform01 = audio_io.random_cutoff(waveform01, self.audio_window, pick01)
        # print("{} < -> {}".format(pick01, pick02))

        if len(self.augmentation) != 0:
            waveform01 = audio_augmentation.audio_augmentation_pipeline(waveform01, self.sampling_rate,
                                                                        self.audio_window,
                                                                        random.sample(self.augmentation,
                                                                                      random.randint(1, self.augmentation_count)),
                                                                        fix_audio_length=True)

        return waveform01, acoustic_id
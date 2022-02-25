from torch.utils.data import Dataset
import src.utils.interface_file_io as file_io
import src.utils.interface_audio_io as audio_io
import src.utils.interface_audio_augmentation as audio_augmentation
import numpy as np
import random


def get_audio_file_path(file_list, index):
    audio_file = file_list[index]
    return audio_file[4:]


def load_waveform(audio_file, required_sampling_rate):
    waveform, sampling_rate = audio_io.audio_loader(audio_file)

    assert(
        sampling_rate == required_sampling_rate
    ), "sampling rate is not consistent throughout the dataset"
    return waveform


class WaveformDatasetByWaveBYOL(Dataset):
    def __init__(self, file_path, audio_window=20480, sampling_rate=16000, augmentation=[1, 2, 3, 4, 5, 6],
                 augmentation_count=5):
        super(WaveformDatasetByWaveBYOL, self).__init__()
        self.file_path = file_path
        self.audio_window = audio_window
        self.sampling_rate = sampling_rate
        self.augmentation = augmentation
        self.augmentation_count = augmentation_count
        self.file_list = file_io.read_txt2list(self.file_path)

    def __len__(self):
        return len(self.file_list)

    def __getitem__(self, index):
        audio_file = get_audio_file_path(self.file_list, index)
        waveform_original = audio_io.audio_adjust_length(load_waveform(audio_file, self.sampling_rate),
                                                         self.audio_window + 8000,
                                                         fit=False)
        waveform01 = audio_io.audio_adjust_length(load_waveform(audio_file, self.sampling_rate),
                                                  self.audio_window + 8000,
                                                  fit=False)
        waveform02 = audio_io.audio_adjust_length(load_waveform(audio_file, self.sampling_rate),
                                                  self.audio_window + 8000,
                                                  fit=False)

        if len(self.augmentation) != 0:
            pick_index = np.random.randint(
                waveform01.shape[1] - self.audio_window + 1 - 8000)  # 약간 오버사이즈로 자르고 # augmentation하면서 자르기
            waveform_original = audio_io.random_cutoff(waveform_original, self.audio_window, pick_index + 4000)
            waveform01 = audio_io.random_cutoff(waveform01, self.audio_window + 8000, pick_index)
            waveform02 = audio_io.random_cutoff(waveform02, self.audio_window + 8000, pick_index)
            waveform01 = audio_augmentation.audio_augmentation_pipeline(waveform01, self.sampling_rate,
                                                                        self.audio_window,
                                                                        random.sample(self.augmentation,
                                                                                      random.randint(1, self.augmentation_count)),
                                                                        fix_audio_length=True)
            waveform02 = audio_augmentation.audio_augmentation_pipeline(waveform02, self.sampling_rate,
                                                                        self.audio_window,
                                                                        random.sample(self.augmentation,
                                                                                      random.randint(1, self.augmentation_count)),
                                                                        fix_audio_length=True)
        else:
            pick_index = np.random.randint(
                waveform01.shape[1] - self.audio_window + 1)
            waveform_original = audio_io.random_cutoff(waveform_original, self.audio_window, pick_index)
            waveform01 = audio_io.random_cutoff(waveform01, self.audio_window, pick_index)
            waveform02 = audio_io.random_cutoff(waveform02, self.audio_window, pick_index)

        return waveform_original, waveform01, waveform02


class WaveformDatasetByWaveBYOLTypeA(Dataset):
    def __init__(self, file_path, audio_window=20480, sampling_rate=16000, augmentation=[1, 2, 3, 4, 5, 6],
                 augmentation_count=5):
        super(WaveformDatasetByWaveBYOLTypeA, self).__init__()
        self.file_path = file_path
        self.audio_window = audio_window
        self.sampling_rate = sampling_rate
        self.augmentation = augmentation
        self.augmentation_count = augmentation_count
        self.file_list = file_io.read_txt2list(self.file_path)

    def __len__(self):
        return len(self.file_list)

    def __getitem__(self, index):
        audio_file = get_audio_file_path(self.file_list, index)
        waveform01 = audio_io.audio_adjust_length(load_waveform(audio_file, self.sampling_rate),
                                                  self.audio_window,
                                                  fit=False)
        waveform02 = audio_io.audio_adjust_length(load_waveform(audio_file, self.sampling_rate),
                                                  self.audio_window,
                                                  fit=False)

        pick01 = np.random.randint(waveform01.shape[1] - self.audio_window + 1)
        waveform01 = audio_io.random_cutoff(waveform01, self.audio_window, pick01)
        pick02 = np.random.randint(waveform02.shape[1] - self.audio_window + 1)
        waveform02 = audio_io.random_cutoff(waveform02, self.audio_window, pick02)
        # print("{} < -> {}".format(pick01, pick02))

        if len(self.augmentation) != 0:
            waveform01 = audio_augmentation.audio_augmentation_pipeline(waveform01, self.sampling_rate,
                                                                        self.audio_window,
                                                                        random.sample(self.augmentation,
                                                                                      random.randint(1, self.augmentation_count)),
                                                                        fix_audio_length=True)
            waveform02 = audio_augmentation.audio_augmentation_pipeline(waveform02, self.sampling_rate,
                                                                        self.audio_window,
                                                                        random.sample(self.augmentation,
                                                                                      random.randint(1, self.augmentation_count)),
                                                                        fix_audio_length=True)

        return 0, waveform01, waveform02
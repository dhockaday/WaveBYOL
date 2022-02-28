from torch.utils.data import Dataset
import src.utils.interface_file_io as file_io
import src.utils.interface_audio_io as audio_io
import src.utils.interface_audio_augmentation as audio_augmentation
import src.data.dataset as dataset
import random


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
        audio_file = dataset.get_audio_file_path(self.file_list, index)
        waveform01 = audio_io.audio_adjust_length(
            dataset.load_waveform(audio_file, self.sampling_rate),
            self.audio_window, fit=False)
        waveform02 = audio_io.audio_adjust_length(
            dataset.load_waveform(audio_file, self.sampling_rate),
            self.audio_window, fit=False)

        pick01 = dataset.get_random_start_point(waveform01.shape[1], self.audio_window)
        waveform01 = audio_io.random_cutoff(waveform01, self.audio_window, pick01)
        pick02 = dataset.get_random_start_point(waveform02.shape[1], self.audio_window)
        waveform02 = audio_io.random_cutoff(waveform02, self.audio_window, pick02)

        if len(self.augmentation) != 0:
            waveform01 = audio_augmentation.audio_augmentation_pipeline(
                waveform01, self.sampling_rate, self.audio_window,
                random.sample(self.augmentation, random.randint(1, self.augmentation_count)),
                fix_audio_length=True)
            waveform02 = audio_augmentation.audio_augmentation_pipeline(
                waveform02, self.sampling_rate, self.audio_window,
                random.sample(self.augmentation, random.randint(1, self.augmentation_count)),
                fix_audio_length=True)

        return waveform01, waveform02

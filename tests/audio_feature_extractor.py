import unittest
from clapclap.update.audio_feature_extractor import resample_with_ffmpeg, get_duration, get_slices_timestamps
import glob
from pathlib import Path


tests_files_folder = Path("tests/test_files")
tests_output_folder = Path("tests/outputs")

files = glob.glob(str(tests_files_folder / Path("*.flac")))


class TestAudioFeatureExtractor(unittest.TestCase):

    def test_get_duration(self):
        file = Path(files[0])
        with open(file, "rb") as f:
            input_bytes = f.read()
            duration = get_duration(input_bytes)
        self.assertEqual(duration, 249.64)

    def test_resample_with_ffmpeg_slice(self):
        file = Path(files[0])
        resample_duration = 600
        slices = 4
        with open(file, "rb") as f:
            input_bytes = f.read()
            output_bytes = resample_with_ffmpeg(
                input_bytes, "slice", resample_duration=resample_duration, slices=slices)
        output_files = tests_output_folder / \
            (str(file.name) + f"_slice_{resample_duration}_{slices}.raw")
        with open(output_files, "wb") as f:
            f.write(output_bytes)
        # no assert, just check the audio file if the cut is correct

    def test_resample_with_ffmpeg_start(self):
        file = Path(files[0])
        resample_duration = 120
        with open(file, "rb") as f:
            input_bytes = f.read()
            output_bytes = resample_with_ffmpeg(
                input_bytes, "start", resample_duration=resample_duration)
        output_files = tests_output_folder / \
            (str(file.name) + f"_start_{resample_duration}.raw")
        with open(output_files, "wb") as f:
            f.write(output_bytes)
        # no assert, just check the audio file if the cut is correct

    def test_resample_with_ffmpeg_full(self):
        file = Path(files[0])
        with open(file, "rb") as f:
            input_bytes = f.read()
            output_bytes = resample_with_ffmpeg(
                input_bytes, "full")
        output_files = tests_output_folder / \
            (str(file.name) + f"_full.raw")
        with open(output_files, "wb") as f:
            f.write(output_bytes)
        # no assert, just check the audio file if the cut is correct

    def test_get_slices_timestamps(self):
        self.assertEqual([[0.0, 40.0], [70.0, 110.0], [
                         140.0, 180.0]], get_slices_timestamps(180, 120, 3))
        self.assertEqual([[0.0, 60.0], [40.0, 100.0]],
                         get_slices_timestamps(100, 120, 2))
        self.assertEqual([[0.0, 120.0]],
                         get_slices_timestamps(100, 120, 1))
        self.assertEqual([],
                         get_slices_timestamps(100, 120, 0))

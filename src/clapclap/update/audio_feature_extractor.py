import torch
import subprocess
import json
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import io
import base64

from tinytag import TinyTag
from transformers import ClapAudioModelWithProjection, ClapProcessor

from clapclap.utils import Timer
from clapclap.utils.consts import CLAP_PROCESSOR, CLAP_MODEL, CLAP_SAMPLING_RATE
from clapclap.utils.log import logger
from clapclap.utils.config import config


def threadpool_pipeline(func, batch, subpaths, max_workers):
    output = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for audio_bytes, subpath in zip(batch, subpaths):
            futures[executor.submit(func, audio_bytes)] = subpath
        for future in as_completed(futures):
            subpath = futures[future]
            try:
                result = future.result()
            except Exception as e:
                logger.error(f"Can't '{func.__name__}': '{subpath}' \n{e}")
                result = None
            output[subpath] = result
    return [output[subpath] for subpath in subpaths]


def fingerprint_in_tags(audio_bytes):
    bytes_io = io.BytesIO(initial_bytes=audio_bytes)
    tags = TinyTag.get(file_obj=bytes_io)
    possible_keys = ["acoustid_fingerprint"]

    for pk in possible_keys:
        if pk in tags.other:
            for base64_value in tags.other[pk]:
                if base64_value is None:
                    continue
                return base64_value
    return None


def fingerprint_with_fpcalc(audio_bytes):
    result = subprocess.run(
        # use the same args as picard:
        # https://github.com/metabrainz/picard/blob/5a35d3bbde0175558bb2f441fcd952d7f18f4798/picard/acoustid/__init__.py#L285
        ["fpcalc", "-json", "-length", "120", "-"],
        input=audio_bytes,
        capture_output=True,
        check=True,
    )
    fpdata = json.loads(result.stdout)
    fingerprint_base64 = fpdata["fingerprint"]
    return fingerprint_base64


def fingerprint_to_bytes(base64_value):
    missing_padding = len(base64_value) % 4
    if missing_padding:
        base64_value += "=" * (4 - missing_padding)
    binary_value = base64.urlsafe_b64decode(base64_value)
    return binary_value


def get_duration(audio_bytes):
    cmd = [
        "ffprobe",
        "-i", "pipe:0",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1"
    ]
    result = subprocess.run(
        cmd,
        input=audio_bytes,
        capture_output=True,
        check=True
    )
    return float(result.stdout.strip())


def get_slices_timestamps(duration, max_duration, slices):
    slices_timestamps = []
    if slices > 0:
        slice_duration = max_duration / slices
    else:
        slice_duration = max_duration
    discard_duration = duration - max_duration
    if slices > 1:
        duration_between_slice = discard_duration / (slices - 1)
    else:
        duration_between_slice = 0

    for i in range(slices):
        start = i * (slice_duration + duration_between_slice)
        end = start + slice_duration
        slices_timestamps.append([start, end])

    return slices_timestamps


def resample_with_ffmpeg(audio_bytes, method, resample_duration=0, slices=0):
    cmd = [
        "ffmpeg",
        "-nostdin",
        "-threads", "1",
        "-i", "pipe:0",
        "-map", "0:a:0",
        "-ac", "1",
        "-ar", str(CLAP_SAMPLING_RATE),
    ]

    if method == "start":
        cmd.extend(["-t", str(resample_duration)])
    elif method == "slice":
        duration = get_duration(audio_bytes)
        # do nothing (like full) if the clip is smaller than the resample duration
        if resample_duration <= duration:
            between = get_slices_timestamps(
                duration, resample_duration, slices)
            between_text = "+".join(
                [fr"between(t\,{a:.2f}\,{b:.2f})" for a, b in between])
            cmd.extend(["-af", f"aselect='{between_text}',asetpts=N/SR/TB"])

    elif method == "full":
        pass
    else:
        raise Exception("invalid method")

    cmd.extend([
        "-f", "f32le",
        "-acodec", "pcm_f32le",
        # "-v", "quiet",
        "pipe:1"
    ])

    # print(" ".join(cmd))
    result = subprocess.run(
        cmd,
        input=audio_bytes,
        capture_output=True,
        check=True
    )
    logger.debug(result.stderr.decode("utf8"))
    audio_array = np.frombuffer(result.stdout, dtype=np.float32)
    array_copy = audio_array.copy()
    if len(array_copy) <= 0:
        raise Exception("ffmpeg returned an empty output")
    return array_copy


class AudioFeatureExtractor:
    def __init__(self, max_workers, ignore_existing_fingerprint):
        self.embedding_method = config.EMBEDDING_METHOD
        self.embedding_duration = float(config.EMBEDDING_DURATION)
        self.embedding_method_slices = int(config.EMBEDDING_METHOD_SLICES)
        self.max_workers = max_workers
        self.ignore_existing_fingerprint = ignore_existing_fingerprint

        logger.debug(f"max_workers: {self.max_workers}")

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        logger.debug(f"Embedding Projection Device: {self.device}")

        logger.debug("loading clap model...")
        try:
            self.processor = ClapProcessor.from_pretrained(
                CLAP_PROCESSOR, local_files_only=True)
            self.model = ClapAudioModelWithProjection.from_pretrained(
                CLAP_MODEL, local_files_only=True)
        except Exception as e:
            print(e)
            self.processor = ClapProcessor.from_pretrained(CLAP_PROCESSOR)
            self.model = ClapAudioModelWithProjection.from_pretrained(
                CLAP_MODEL)
        logger.debug("clap model loaded")

        self.model = self.model.to(self.device)
        self.model.eval()

    def process_batch(self, batch, subpaths):
        logger.debug("process batch start")

        with Timer("batch fingerprint"):
            fingerprints = threadpool_pipeline(
                self.fingerprint, batch, subpaths, self.max_workers)

        with Timer("batch resample"):
            audio_arrays = threadpool_pipeline(
                self.resample, batch, subpaths, self.max_workers)

        with Timer("batch clap"):
            embeddings = self.clap(audio_arrays)

        batch_size = len(fingerprints)
        output = list(zip(fingerprints, embeddings,
                      batch_size * [self.embedding_method], batch_size * [self.embedding_duration]))

        logger.debug(f"process batch end {len(output)}")
        return output

    def resample(self, audio_bytes):
        with Timer("resample"):
            return resample_with_ffmpeg(audio_bytes, self.embedding_method, self.embedding_duration, self.embedding_method_slices)

    def fingerprint(self, audio_bytes):
        with Timer("fingerprint"):
            if not self.ignore_existing_fingerprint:
                filetag_fingerprint = fingerprint_in_tags(audio_bytes)
                if filetag_fingerprint:
                    return fingerprint_to_bytes(filetag_fingerprint)

            fpcalc_fingerprint = fingerprint_with_fpcalc(audio_bytes)

            return fingerprint_to_bytes(fpcalc_fingerprint)
        return None

    def clap(self, audio_arrays):
        valid_indices = [i for i, a in enumerate(
            audio_arrays) if a is not None]
        valid_audio_arrays = [audio_arrays[i] for i in valid_indices]
        if len(valid_audio_arrays) <= 0:
            return [None] * len(audio_arrays)
        embeddings = []
        with Timer("clap processor"):
            inputs = self.processor(
                audio=valid_audio_arrays,
                sampling_rate=CLAP_SAMPLING_RATE,
                return_tensors="pt"
            )
        with Timer("clap projection"):
            inputs = inputs.to(self.device)
            with torch.no_grad():
                outputs = self.model(**inputs)
                result = outputs.audio_embeds.detach().cpu().numpy()
                for r in result:
                    embeddings.append(r)
        valid_embeddings = [
            embeddings[i] if i in valid_indices else None for i in range(len(audio_arrays))]
        return valid_embeddings

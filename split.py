import os
import re
from typing import List
import ffmpeg
import time


def find_optimal_breakpoints(points: List[float], n: int) -> List[float]:
    result = []
    optimal_length = points[-1] / n
    temp = 0
    temp_a = 0
    l = len(points)
    for i in points[:l - 1]:
        if (i - temp_a) >= optimal_length:
            if optimal_length - (temp - temp_a) < (i - temp_a) - optimal_length:
                result.append(temp)
            else:
                result.append(i)
            temp_a = result[-1]
        temp = i
    return result


def split_audio_into_chunks(input_file: str, max_chunks: int,
                            silence_threshold: str = "-20dB", silence_duration: float = 2.0) -> List[str]:
    def save_chunk_to_temp_file(input_file: str, start: float, end: float, idx: int) -> str:
#        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
#        temp_file.close()
        filename, file_extension = os.path.splitext(input_file)
        temp_file = f'{filename}_{idx}{file_extension}'
        in_stream = ffmpeg.input(input_file)
        (
            ffmpeg.output(in_stream, temp_file, ss=start, t=end - start, c="copy")
            .global_args('-hide_banner')
            .overwrite_output()
            .run()
        )

        return temp_file

    def get_silence_starts(input_file: str) -> List[float]:
        silence_starts = [0.0]

        reader = (
            ffmpeg.input(input_file)
            .filter("silencedetect", n=silence_threshold, d=str(silence_duration))
            .output("pipe:", format="null")
            .global_args('-hide_banner')
            .run_async(pipe_stderr=True)
        )

        silence_end_re = re.compile(
            r" silence_end: (?P<end>[0-9]+(\.?[0-9]*)) \| silence_duration: (?P<dur>[0-9]+(\.?[0-9]*))"
        )

        while True:
            line = reader.stderr.readline().decode("utf-8")
            if not line:
                break

            match = silence_end_re.search(line)
            if match:
                silence_end = float(match.group("end"))
                silence_dur = float(match.group("dur"))
                silence_start = silence_end - silence_dur
                silence_starts.append(silence_start)

        return silence_starts

    file_extension = os.path.splitext(input_file)[1]
    metadata = ffmpeg.probe(input_file)
    duration = float(metadata["format"]["duration"])

    silence_starts = get_silence_starts(input_file)
    silence_starts.append(duration)

    temp_files = []
    current_chunk_start = 0.0

    selected_items = find_optimal_breakpoints(silence_starts, max_chunks)
    selected_items.append(duration)

    for j in range(0, len(selected_items)):
        temp_file_path = save_chunk_to_temp_file(input_file, current_chunk_start, selected_items[j], j)
        temp_files.append(temp_file_path)

        current_chunk_start = selected_items[j]

    return temp_files


from faster_whisper import WhisperModel
import ffmpeg
import multiprocessing
from typing import List
import concurrent.futures
import time
from split import split_audio_into_chunks


def transcribe_file(file_path, model):
    segments, info = model.transcribe(file_path)
    segments = list(segments)
    return segments


def transcribe_audio(input_file: str, max_processes = 0,
                     silence_threshold: str = "-20dB", silence_duration: float = 2.0, model=None) -> str:
    if max_processes > multiprocessing.cpu_count() or max_processes == 0:
        max_processes = multiprocessing.cpu_count()

    # Split the audio into chunks
    temp_files_array = split_audio_into_chunks(input_file, max_processes, silence_threshold, silence_duration)
    start = time.time()
    futures = []
    # Submit each file to the thread pool and store the corresponding future object
    with concurrent.futures.ThreadPoolExecutor(max_processes) as executor:
        for file_path in temp_files_array:
            future = executor.submit(transcribe_file, file_path, model)
            futures.append(future)

    result_string = ""
    for future in futures:
        segments = future.result()
        for seg in segments:
        #    result_string += "".join(segment.text for segment in segments)
            result_string += "[%.2fs -> %.2fs] %s\n" % (seg.start, seg.end, seg.text)

    end = time.time()
    print(end - start)

    # Remember to remove the temporary files after you're done processing them
    for temp_file in temp_files_array:
        os.remove(temp_file)
    return result_string



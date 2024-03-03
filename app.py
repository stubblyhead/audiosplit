import json
import boto3
import split
import urllib.parse
import os
import ffmpeg
from math import ceil

s3 = boto3.client('s3')
dest_bucket = os.environ.get('DEST_BUCKET')
part_duration = float(os.environ.get('PART_DURATION'))
silence_duration = float(os.environ.get('SILENCE_DURATION'))
silence_threshold = os.environ.get('SILENCE_THRESH')

def handler(event, context):
    print('## EVENT')
    print(event)
    try:
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        prefix = os.path.dirname(key)    
        filename = os.path.basename(key)
        audio_file = f'/tmp/{filename}'
        print(f'saving object to {audio_file}')
        s3.download_file(bucket, key, audio_file)
        audio_info = ffmpeg.probe(audio_file)
        dur = float(audio_info['format']['duration'])
        # using 7:30 target for part length to start, adjust in function env vars (use number of seconds)
        parts = ceil(dur / part_duration) 
        # set silence_threshold and duration in function env vars, -20dB and 1.0 (in sec) seem to work well
        split_files = split.split_audio_into_chunks(audio_file, parts, silence_threshold, silence_duration)
        print(f'split audio into {parts} parts')
        for this_f in split_files:
            with open(this_f,mode='rb') as f:
                f_name = os.path.basename(this_f)
                s3.put_object(Bucket=dest_bucket, Key=f'{prefix}/{f_name}', Body=f)
                print(f'copied {this_f} to s3://stubbs-parts/{prefix}/{f_name}')
            os.remove(this_f)
        os.remove(audio_file)
        # will need to update policy to delete input object, not sure if we want to do this though
        # s3.delete_object(Bucket=bucket, Key=key)
        print(f'finished splitting {key}, removed temp files')
        return { "statusCode": 200, "body": f"{audio_file} split up" }
    except Exception as e:
        print(e)
        return { "statusCode": 500, "body": f"error processing the file: {e}" }


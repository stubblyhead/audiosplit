# audiosplit
split dat audio

### usage
define the following environment variables on the lambda function, these are required for the function to work correctly

`DEST_BUCKET` -- name of the destination bucket for split files

`PART_DURATION` -- target length for each split file in seconds, actual length will depend on total file length and where good gaps in the audio are, 450 (7'30") seems like a reasonable starting point

`SILENCE_THRESH` -- how quiet the audio should be to consider it as silent, -20dB seems to work reasonably well (larger negative == quieter)

`SILENCE_DURATION` -- how long in seconds the period of silence should be to consider it as a good breaking point       

### suggested settings
give the lambda around 512mb of memory, should be plenty.  empirically it maxes at around 270mb, so this can probably be shaved down a bit

timeout after 3 minutes, again lots of cushion here

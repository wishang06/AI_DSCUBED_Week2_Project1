# A brief overview of Audio2Text

## What for
An engine that can transcribe audio files into text, auto detect speakers and clean up conversations. It produces a folder containing all the relevant details of the transcription. 

## Usage
1. Upload the audio into "Audio2Text/audio" folder.
2. Start the engine with "**uv run .\engines\voice_processing_engine.py**"
3. Enter exact audio file name (just the file name, not the path name) ie. test-audio.m4a
4. Enter an integer number of speakers involved in this audio
5. The results will be created inside a folder called "**transcribed_audio**", file name will be "{audio_file_name}_YYYY-MM-DD_HH-MM-SS"
6. The final cleaned up conversation is a file ending with "***-merged.json"

## Note
The engine works best with less than 5 people. The performance reduces significantly when more people involved.
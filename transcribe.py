import sys
import os
from pydub import AudioSegment
import requests
# import openai
import whisper
import re
from moviepy.editor import *
# from transformers import GPT2Tokenizer

global model
model = whisper.load_model("base")

root = os.getcwd()
videosFolder = os.path.join(root, 'videos')
transcribeTextFolder = os.path.join(root, 'transcribed')
transcribeWavFolder = os.path.join(root, 'transcribed', 'wavFiles')

try: os.mkdir(transcribeTextFolder)
except: pass
try:os.mkdir(transcribeWavFolder)
except:pass

def convert_audio_to_wav(fileName, filePath, file_extension):
    try:
        # output_file = os.path.splitext(filePath)[0] + ".wav"
        file_extension = os.path.splitext(filePath)[1].lower()
        output_file = os.path.join(transcribeWavFolder, fileName.replace(file_extension, '.wav')) 

        if file_extension == ".mp3":
            audio = AudioSegment.from_mp3(filePath)
        elif file_extension == ".m4a":
            audio = AudioSegment.from_file(filePath, "m4a")
        elif file_extension == ".mp4":
            video = VideoFileClip(filePath)
            video.audio.write_audiofile(output_file, codec="pcm_s16le", verbose=False)
            print(f"Conversion successful! WAV file saved as: {output_file}")
            return output_file
        else:
            raise ValueError("Unsupported audio format")

        audio.export(output_file, format="wav")
        print(f"Conversion successful! WAV file saved as: {output_file}")
        return output_file
    except Exception as e:
        print(f"An error occurred during conversion: {e}")
        return None



def transcribe(video):
    filePath = video['path']
    fileName = video['fileName']
    fileExtension =  os.path.splitext(filePath)[1].lower()

    saved_wav_file_path = convert_audio_to_wav(fileName, filePath, fileExtension)
    result = model.transcribe(saved_wav_file_path)
    text_output = result["text"]

    filePath =  os.path.join(transcribeTextFolder, fileName.replace(fileExtension, '.txt'))
    save_text(text_output, filePath)
    print(f"Transcription saved to: {filePath}")



def save_text(data, filePath):
    with open(filePath, 'w') as file:
        file.write(data)



def getVideo(url, fileName):
    response = requests.get(url, stream=True)
    savePath = os.path.join(os.getcwd(), 'videos', fileName+'.mp4')
    if response.status_code == 200:
        with open(savePath, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print(f"File downloaded successfully to: {savePath}")
    else: print(f"Failed to download the file. Status code: {response.status_code}")



def Videos():
    urlFilepath = os.path.join(os.getcwd(), 'videoURL.txt')
    urls = []
    fileNamePattern = r'\((.*?)\)'
    urlPattern = r'\[(.*)\]'

    with open(urlFilepath, 'r') as file:
        urls = file.readlines()

    urls = [re.findall( r'\((.*?)\)\[(.*)\]', x)[0] for x in urls]
    for url in urls:
       fileName = url[0].replace('.', '').replace('?', '').replace(',', '')
       getVideo(url[1], fileName)


Videos()
videoFiles = [{'path':os.path.join(videosFolder, x), 'fileName':x} for x in os.listdir(videosFolder)]
for videos in videoFiles:
    transcribe(videos)
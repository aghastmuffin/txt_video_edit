import wave, json, sys, os #GENERATES GEN.TXT
from vosk import Model, KaldiRecognizer, SetLogLevel
from moviepy.video.io.VideoFileClip import VideoFileClip
import tkinter as tk #READS GEN.TXT
import difflib
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
SetLogLevel(-1)
import survey, glob, os
print("init complete!")
codec = "libx264"
codec = "h264_nvenc"

file_list = glob.glob('*.mp4') + glob.glob('*.mp3') + glob.glob('*.wav')
print(file_list)
if len(file_list) < 1:
    exit("no supported file types found. (mp4, mp3, wav)")
index = survey.routines.select('Which base video: ',  options = file_list,  focus_mark = '> ',  evade_color = survey.colors.basic('yellow'))
audio_filename = file_list[index]
def separate_audio_video(video_path, audio_output_path):
    video = VideoFileClip(video_path)
    
    # Extract audio
    audio = video.audio
    audio.write_audiofile(audio_output_path)


if ".mp4" in audio_filename:
    separate_audio_video(f"{audio_filename}", "output_audio.mp3")
    audio_filename = "output_audio.mp3"

class Word:
    ''' A class representing a word from the JSON format for vosk speech recognition API '''

    def __init__(self, dict):
        '''
        Parameters:
          dict (dict) dictionary from JSON, containing:
            conf (float): degree of confidence, from 0 to 1
            end (float): end time of the pronouncing the word, in seconds
            start (float): start time of the pronouncing the word, in seconds
            word (str): recognized word
        '''

        self.conf = dict["conf"]
        self.end = dict["end"]
        self.start = dict["start"]
        self.word = dict["word"]

    def to_string(self):
        ''' Returns a string describing this instance '''
        return "{:20} from {:.2f} sec to {:.2f} sec, confidence is {:.2f}%".format(
            self.word, self.start, self.end, self.conf*100)
    def times(self):
        ''' Returns a tuple with start and end times '''
        return (self.start, self.end)
    def word(self):
        ''' Returns the recognized word '''
        return self.word
    def all(self):
        return self.word, self.start, self.end, self.conf*100
if ".mp3" in audio_filename:
    os.system(f'ffmpeg -i {audio_filename} {audio_filename.replace(".mp3", "")}.wav')
    audio_filename = audio_filename.replace(".mp3", ".wav")
    
custom_Word = Word
model = Model(lang="en-us")
wf = wave.open(audio_filename, "rb")
rec = KaldiRecognizer(model, wf.getframerate())
rec.SetWords(True)

if wf.getnchannels() == 1:
    pass
else:
    print("2 chanel audio detected, converting to 1 chanel")
    os.system(f'ffmpeg -i {audio_filename} -ac 1 {audio_filename}') #FIX THIS LINE OF CODE, TK DOESN'T KNOW WHAT THIS ARG IS. ALSO THIS IS NOT NEEDED.
# get the list of JSON dictionaries
print("recognizing audio")
results = []
# recognize speech using vosk model
while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        part_result = json.loads(rec.Result())
        results.append(part_result)
part_result = json.loads(rec.FinalResult())
results.append(part_result)

# convert list of JSON dictionaries to list of 'Word' objects
list_of_Words = []
for sentence in results:
    if len(sentence) == 1:
        # sometimes there are bugs in recognition 
        # and it returns an empty dictionary
        # {'text': ''}
        continue
    for obj in sentence['result']:
        w = custom_Word(obj)  # create custom Word object
        list_of_Words.append(w)  # and add it to list
maindict = {}
wf.close()  # close audiofile
from collections import OrderedDict
import json

# convert list of JSON dictionaries to list of 'Word' objects
list_of_Words = []
for sentence in results:
    if len(sentence) == 1:
        continue
    for obj in sentence['result']:
        w = custom_Word(obj)  # create custom Word object
        list_of_Words.append(w)  # and add it to list

wf.close()  # close audiofile
with open('gen.txt', 'w') as f:
    for word in list_of_Words:
        theword = word.all()
        #f.write(', '.join(map(str, theword)))
        f.write(f"{theword[0]},{theword[1]},{theword[2]}")
        f.write('\n')
    f.close()
#done with audio processing
#now start the GUI up
try:
    os.remove("output_audio.mp3")
except FileNotFoundError:
    pass

def remove_section(video_path, start_time, end_time, output_path):
    video = VideoFileClip(video_path)
    clip1 = video.subclip(0, start_time)
    clip2 = video.subclip(end_time, video.duration)
    final_clip = concatenate_videoclips([clip1, clip2])
    final_clip.write_videofile(output_path, codec=codec)


def open_file():
	with open("gen.txt", 'r') as file:
		content = file.read()
		text_widget.delete(1.0, tk.END) # Clear previous content
		text_widget.insert(tk.END, content)

st, et = 0, 0
def wv():
    st, et = 0, 0
    loops_count = 0
    all_loops_count = 0
    ran = False
    with open("gen.txt", 'r') as file:
        f = file.readlines()
    content = text_widget.get("1.0", tk.END).splitlines(True)
    diff = difflib.unified_diff(
        f,
        content,
        fromfile='gen.txt',
        tofile='text_widget',
    )
    #VERY SLOW, OPTIMIZE LATER
    diff = list(diff)
    for line in diff:
        all_loops_count += 1
        if line.startswith('-'):
            sline = line.replace("-", "").replace("\n", "").split(",")
            if len(sline) == 3:
                loops_count += 1
                if loops_count == 1:
                    print("cap")
                    st = sline[1]
                et = sline[2] #https://stackoverflow.com/questions/1630320/what-is-the-pythonic-way-to-detect-the-last-element-in-a-for-loop
                print(sline)
        else:
            if all_loops_count > 5 and loops_count > 0:
                print("done")
                print(st, et) #RETURN DATA FROM HERE
                remove_section("pvideo.mp4", float(st), float(et), "output.mp4")
                break
            

# Create the main window
import customtkinter as ctk
from tkinter import messagebox
root = ctk.CTk()
root.title("Text Based Video Editor (NON PRODUCTION)")
root.geometry("400x400")

# Create a Text widget to display the content
text_widget = ctk.CTkTextbox(root, wrap="word")
text_widget.pack(pady=10, expand=True, fill="both")
text_widget.insert(ctk.END, "init")
open_file()
sc = ctk.CTkButton(root, text="Write to Video", command=wv)
abt = ctk.CTkButton(root, text="About", command=lambda: messagebox.showinfo("About", "This is a text based video editor. \n developed by aghastmuffin. \n Version 0.1 \n FREE TIER."))
# Run the Tkinter event loop
sc.pack()
root.focus_force()
abt.pack()
root.mainloop()

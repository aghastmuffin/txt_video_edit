import wave, json, sys, os #GENERATES GEN.TXT
from vosk import Model, KaldiRecognizer, SetLogLevel
SetLogLevel(-1)
import survey, glob, os
print("init complete!")

file_list = glob.glob('*.mp4') + glob.glob('*.mp3') + glob.glob('*.wav')
print(file_list)
if len(file_list) < 1:
    exit("no supported file types found. (mp4, mp3, wav)")
index = survey.routines.select('Which base video: ',  options = file_list,  focus_mark = '> ',  evade_color = survey.colors.basic('yellow'))
audio_filename = file_list[index]
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
    os.system(f'ffmpeg -i {audio_filename} -ac 1 {audio_filename}')
    sys.exit(1)
# get the list of JSON dictionaries
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
print("done")

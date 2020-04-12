from pydub import AudioSegment
from pydub.playback import play
import simpleaudio.functionchecks as fc


#BEFORE RUNNING
#pip install pydub  [documentation: https://github.com/jiaaro/pydub]
#pip install simpleaudio [documentation: ] 

# fc.LeftRightCheck.run()
note = AudioSegment.from_wav("note_lib/B_note.wav") #getting .wave file
print("playing note")
play(note) #playing wave file

note2 = AudioSegment.from_wav("note_lib/A_note.wav")

#splice songs
second = 1000
note = note[:1000]
note2 = note2[:1000]

#add songs together!
both = note + note2
play(both)

#play reverse!
play(both.reverse())

#save results!
# both.export("both.wav", format="wav")




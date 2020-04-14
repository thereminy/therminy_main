from pydub import AudioSegment
from pydub.playback import play
import simpleaudio.functionchecks as fc
import array

#BEFORE RUNNING
#pip install pydub  [documentation: https://github.com/jiaaro/pydub]
#pip install simpleaudio
# then uncomment this line and run it!
#fc.LeftRightCheck.run()

note = AudioSegment.from_wav("note_lib/B_note.wav") #getting .wave file
print("playing note")
# play(note) #playing wave file

note2 = AudioSegment.from_wav("note_lib/A_note.wav")

#splice songs!
second = 1000
note = note[:1000]
note2 = note2[:1000]

#add songs together!
both = note + note2
#play(both)

#play reverse!
#play(both.reverse())

#save results!
#both.export("both.wav", format="wav")

current_notes = ['A','B','C','D','E','F','G']
def request_handler(request):
	if request['method'] ==  'GET':
		note  = request['values'].get('note' , None)
		if note == None:
			return 'Must contain a note type'
		### LIBRARY METHODS ##

		#For the server 
		#file_path = '__HOME__/{}_note.wav'.format(note)
		# To test locally 
		file_path = 'note_lib/{}_note.wav'.format(note)

		#WAV FORMAT  METHOD
		audio_note = AudioSegment.from_file(file_path)
		sound_array = audio_note.get_array_of_samples()
		array_stream = array.array(audio_note.array_type, sound_array)
		
		# RAW NOTE METHOD 
		# audio_note = AudioSegment.from_file(file_path)
		# # returns bytes per sample  
		# bytes_per_sample = audio_note.sample_width
		# # returns sample rate 
		# frames_per_second = audio_note.frame_rate
		# # returns bit depth
		# bytes_per_frame = audio_note.frame_width
		# # audio data in the form of a bytestring 
		# raw_audio_data = audio_note.raw_data
		# print(raw_audio_data)

		## NON-LIBRARY METHODS ##

		# BYTE ARRAY METHOD, return byte_array: 
		# byte_array = array.array('B')
		# audio_file = open(file_path, 'rb')
		# byte_array.frombytes(audio_file.read())
		# audio_file.close()
		return array_stream
	return 'Invalid request: must be GET'
	
if __name__ == "__main__":
	# useful for debugging 
	# import doctest 
	# doctest.run_docstring_examples(, globals(), verbose = True)
	# a = request_handler({'method':'GET', 'values':{'note':'A'}})
	# print(a)
	import simpleaudio as sa
	play_obj = sa.play_buffer(a,2, 2, 4)
	with open(a, mode='bx') as f:
		f.write(response)
	b = AudioSegment.from_file(file_path)
	print(sound._spawn(a))
	#scp server.py team091@608dev-2.net:~/	
	pass


from pydub import AudioSegment
from pydub.playback import play
import simpleaudio.functionchecks as fc
import array
import io

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
def request_handler(request, test = ''):
	if request['method'] ==  'GET':
		note  = request['values'].get('note' , None)
		if note == None:
			return 'Must contain a note type'

		# For the server 
		file_path = '__HOME__/{}_note.wav'.format(note)

		# To test Locally 
		#file_path = 'note_lib/{}_note.wav'.format(note)

		## Raw audio data as an array of numeric samples ##

		audio_note = AudioSegment.from_file(file_path)
		sample_array = audio_note.get_array_of_samples()

		if test == 'arr_samples':
			print("Raw audio data:\n", sample_array)
			return (audio_note, sample_array)
		
		## Raw audio library in the form of a bytestring ##

		audio_note = AudioSegment.from_file(file_path)
		# returns bytes per sample  
		bytes_per_sample = audio_note.sample_width
		# returns sample rate 
		frames_per_second = audio_note.frame_rate
		# returns bit depth
		bytes_per_frame = audio_note.frame_width
		# audio data in the form of a bytestring 
		byte_string = audio_note.raw_data

		if test == 'str_bytes':
			print("Raw audio data:\n", byte_string)
			return (audio_note, byte_string)

		## Audio in the form of a byte array ##

		byte_array = array.array('B')
		audio_note = open(file_path, 'rb')
		byte_array.frombytes(audio_note.read())
		audio_note.close()

		if test == 'arr_bytes':
			print("Arr bytes:\n", byte_array)
			return (audio_note, byte_array)

		return byte_array
	return 'Invalid request: must be GET'
	
if __name__ == "__main__":
	##  Test numeric samples ##

	# audio_note, numeric_samples = request_handler({'method':'GET', 'values':{'note':'A'}}, 'arr_samples')
	# play(audio_note._spawn(numeric_samples))

	## Test byte string ##

	# audio_note, raw_audio_data = request_handler({'method':'GET', 'values':{'note':'A'}},'str_bytes')
	# play(audio_note._spawn(raw_audio_data))

	## Test byte array ## 

	# audio_file, byte_array = request_handler({'method':'GET', 'values':{'note':'A'}}, "arr_bytes")
	# song = AudioSegment.from_file(io.BytesIO(byte_array), format="wav")
	# play(song)

	## Server defaults to byte_array 

	#print(request_handler({'method':'GET', 'values':{'note':'A'}}))

	#scp server.py team091@608dev-2.net:~/
	pass

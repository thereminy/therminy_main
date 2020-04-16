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


current_notes = ['A','B','C','D','E','F','G']

note_audio = {
	  'A' : '<audio src="https://drive.google.com/uc?id=114LOpP8CdxC81EzLsgEc3YTtrA4BAMaw" type="audio/wav" controls></audio>',
      'B': '<audio src="https://drive.google.com/uc?id=1AGovI20BijKBleDSPoS7jPdmZCGSRpA4" type="audio/wav" controls></audio>',
      'C': '<audio src="https://drive.google.com/uc?id=19fYil-VsCvQlIe_PeFCZusoGg1gJNsFW" type="audio/wav" controls></audio>',
      'D': '<audio src="https://drive.google.com/uc?id=1mxOFz6Gh66NKrHekCorqdwZnElhr3He_" type="audio/wav" controls></audio>',
      'E': '<audio src="https://drive.google.com/uc?id=1kbg5ftBN8veDloYO20nMPXFeDCKUc9vp" type="audio/wav" controls></audio>',
      'F': '<audio src="https://drive.google.com/uc?id=171ororQ9gmlqf-Cic17trgUihF995vIk" type="audio/wav" controls></audio>',
      'G':'<audio src=https://drive.google.com/uc?id=1Ydqeh87N3yZ0i3CDmkzeHfwArfyXHRXv" type="audio/wav" controls></audio>',
}
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
	else:
		args = request['form']
		note = args['note']

		try:
			note_sound = note_audio[note]
		except KeyError:
			return "This note is not supported"

		

		return """<!DOCTYPE html><html>{}</html>""".format(note_sound)
	
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

	# print(request_handler({'method':'GET', 'values':{'note':'A'}}))

	#scp server.py team091@608dev-2.net:~/

	pass

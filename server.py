from pydub import AudioSegment
from pydub.playback import play
import simpleaudio.functionchecks as fc
import array
import io
import base64
import requests
import sqlite3
import datetime
import time
#import base32

#BEFORE RUNNING
#pip install pydub  [documentation: https://github.com/jiaaro/pydub]
#pip install simpleaudio
# then uncomment this line and run it!
#fc.LeftRightCheck.run()


songs_db = '__HOME__/songs.db'
# songs_db = "songs.db"


current_notes = {'A','B','C','D','E','F','G'}



def create_database():
    conn = sqlite3.connect(songs_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)
    c.execute('''CREATE TABLE song_table (user text, filename text,timing timestamp );''') # run a CREATE TABLE command
    conn.commit() # commit commands
    conn.close() # close connection to database


def request_handler(request, test = ''):
	if request['method'] ==  'GET':
		# user song file path being played
		user = request["values"]['user']

		conn = sqlite3.connect(songs_db)
		c = conn.cursor()

		filename = c.execute('''SELECT filename FROM song_table WHERE user = ? ORDER BY timing DESC ;''',(user,)).fetchone()
		print("f:",filename)

		if filename is None:
			return "No song files have been stored"
		
		user_song_path = "__HOME__/{}".format(filename[0])

		conn.commit()
		conn.close()

		song = open(user_song_path, 'rb')
		b64_encoded= base64.encodebytes(song.read()) #read image and encode it into base64
		return b64_encoded.decode("utf-8")
	else:
		args = request['form']
		song_sequence = args['song']
		user = args['user']
		instrument = args['instrument'] #guitar/bass/piano
		option = args['option'] #add/start/[overlay,user]

		# POST request from ESP32 
		new_song_file = string_to_file(song_sequence,instrument)
		
		filename = "song_{}.wav".format(str(time.time()))
		#new_song_file.export(filename, format="wav")
		
		filepath = "/var/jail/home/team091/{}".format(filename)
		new_song_file.export(filepath, format="wav")

		conn = sqlite3.connect(songs_db)
		c = conn.cursor()
		c.execute('''INSERT into song_table VALUES (?,?,?);''', (user,filename, datetime.datetime.now()))
		conn.commit()  # commit commands
		conn.close()  # close connection to database

		return "Song added to the database!"


def string_to_file(req,instrument):
	"""
	:param req: str in the form of notetime&notetime&notetime
	
	Things to note: 
		- notetime : the note is being playing for duration of time
		- 'S' represents silence
		- time is in milliseconds

	Returns an AudioSegment object 
	"""
	# initializes a zero duration Audio Segment 
	user_sound = AudioSegment.empty()
	# list of lists in the form of [[note,time], [note,time],[note,time]]
	notes_times = [ pair.split(",") for pair in req.split('$')]

	for nt in notes_times:
		note = nt[0]
		if note != "":
			time = float(nt[1])
			print("t:",time)
			if note == 'S':
				# how to add silence: time parameter is in milliseconds
				user_sound+= AudioSegment.silent(time)
			else: 
				file_path = "__HOME__/note_lib/{}_{}_note.wav".format(instrument,note)
				user_sound += AudioSegment.from_wav(file_path)[:time]

	return user_sound


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

	## To play a parsed string 
	#play(new_song)
	#song_open = open(new_song., 'rb') 
	#b64_encoded= base64.encodebytes(new_song.raw_data) #read image and encode it into base64
	#print(b64_encoded)
	# # # how to export 
	# #new_song.export("user_song.wav", format="wav")
	# A = AudioSegment.from_file('note_lib/A_note.wav')
	# B = AudioSegment.from_file('note_lib/B_note.wav')
	# C = AudioSegment.from_file('note_lib/C_note.wav')
	# D = AudioSegment.from_file('note_lib/D_note.wav')
	# E = AudioSegment.from_file('note_lib/E_note.wav')
	# F = AudioSegment.from_file('note_lib/F_note.wav')
	# G = AudioSegment.from_file('note_lib/G_note.wav')



	# GB = G.overlay(B)
	# GBD = GB.overlay(D)
	# play(GB)

	# CE = C.overlay(E)
	# CEG = CE.overlay(G)
	# play(CE)
	# play(CEG)


	pass

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
import json 
#import base32

#BEFORE RUNNING
#pip install pydub  [documentation: https://github.com/jiaaro/pydub]
#pip install simpleaudio
# then uncomment this line and run it!
#fc.LeftRightCheck.run()


songs_db = '__HOME__/songs.db'
# songs_db = "songs.db"


current_notes = {'A','B','C','D','E','F','G'}
instruments = {'guitar','bass','piano'}



def create_database():
    conn = sqlite3.connect(songs_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)
    c.execute('''CREATE TABLE song_table (user text, filename text,timing timestamp);''') # run a CREATE TABLE command
    conn.commit() # commit commands
    conn.close() # close connection to database

music_db = '__HOME__/music.db'
def create_new_database(): 
	"""	
	Creates a database with the new parameter
	"""
	# handles new data base
	conn_music = sqlite3.connect(music_db)
	c_music = conn_music.cursor() 
	c_music.execute('''CREATE TABLE IF NOT EXISTS music_table (user text, filename text, name text, timing timestamp);''')

	# handles old data base 
	conn_songs = sqlite3.connect(songs_db)
	c_songs = conn_songs.cursor() 
	songs = c_songs.execute('''SELECT * FROM song_table ORDER BY timing DESC ;''').fetchall()
	for info in songs: 
		username = info[0]
		filename = info[1]
		time = info[2]
		c_music.execute('''INSERT into music_table VALUES (?,?,?,?);''', (username,filename, "Untitled", time))
	all_music = c_music.execute('''SELECT * FROM music_table ORDER BY timing DESC ;''').fetchall()
	return all_music
	conn_songs.commit()	
	conn_songs.close()
	conn_music.commit()
	conn_music.close()

def request_handler(request, test = ''):
	if request['method'] ==  'GET':
		# user song file path being played
		user = request["values"]['user']

		conn = sqlite3.connect(songs_db)
		c = conn.cursor()

		all_songs = c.execute('''SELECT filename FROM song_table WHERE user = ? ORDER BY timing DESC ;''',(user,)).fetchall()

		if all_songs is None:
			return "No song files have been stored"
		
		songs = []

		for song in all_songs: 
			filename = song[0]
			song = open(get_file_path(filename), 'rb')
			b64_encoded = base64.encodebytes(song.read())
			songs.append(b64_encoded.decode("utf-8"))

		conn.commit()
		conn.close()

		return json.dumps(songs)
	else:
		args = request['form']
		song_sequence = args['song']
		user = args['user1']
		instrument = args['instrument'] #guitar/bass/piano

		if instrument not in instruments:
			return "This instrument is not supported."

		option = args['option'] #add/start/[overlay,user]
		song_file = string_to_file(song_sequence,instrument)

		if option == 'START':
			startSong(user,song_file)
			return "Song added to the database!"
		elif option == 'ADD':
			addSong(user,song_file)
			return "Song added to the database!"
		elif option ==  'OVERLAY':
			user2 = args['user2']
			overlaySong(user,user2,song_file)
			return "Song added to the database!"
		else:
			return "{} is not a supported option.".format(option)


def get_file_path(filename):
	return "__HOME__/{}".format(filename)

def startSong(user,song_file):
	# POST request from ESP32 
	filename = "song_{}.wav".format(str(time.time()))

	filepath = "/var/jail/home/team091/{}".format(filename)
	song_file.export(filepath, format="wav")

	conn = sqlite3.connect(songs_db)
	c = conn.cursor()
	c.execute('''INSERT into song_table VALUES (?,?,?);''', (user,filename, datetime.datetime.now()))
	conn.commit()  # commit commands
	conn.close()  # close connection to database

def addSong(user,song_file):
	song_name = "song_{}.wav".format(str(time.time()))
	filepath = "/var/jail/home/team091/{}".format(song_name)

	conn = sqlite3.connect(songs_db)
	c = conn.cursor()

	filename = c.execute('''SELECT filename FROM song_table WHERE user = ? ORDER BY timing DESC ;''',(user,)).fetchone()

	if filename is None: #the user is can't add current sequence to empty db, create a new file instead
		startSong(user,song_file)
		return "Your database is EMPTY! New song file created for add sequence only"
	else:
	
		user_song_path = "__HOME__/{}".format(filename[0])
		old_song = AudioSegment.from_wav(user_song_path)
		add_song = old_song + song_file
		add_song.export(filepath,format="wav")

		c.execute('''INSERT into song_table VALUES (?,?,?);''', (user,song_name, datetime.datetime.now()))

	conn.commit()
	conn.close()

def overlaySong(user1,user2,song_file):
	song_name = "song_{}.wav".format(str(time.time()))
	filepath = "/var/jail/home/team091/{}".format(song_name)

	conn = sqlite3.connect(songs_db)
	c = conn.cursor()

	filename = c.execute('''SELECT filename FROM song_table WHERE user = ? ORDER BY timing DESC ;''',(user2,)).fetchone()

	if filename is None: #the user is can't add current sequence to empty db, create a new file instead
		return "{} does not exist!".format(user2)
	else:
		user_song_path = "__HOME__/{}".format(filename[0])
		user2_song = AudioSegment.from_wav(user_song_path)

		#prevent song truncation!
		song1_len = len(song_file)
		song2_len = len(user2_song)
		if song1_len != song2_len:
			shorter = min(song1_len,song2_len)
			longer = max(song1_len,song2_len)
			if shorter == song1_len:
				song_file += AudioSegment.silent(duration=longer-shorter) #add silence to shorter song to equalize length!
			else:
				user2_song += AudioSegment.silent(duration=longer-shorter)

		#overlay songs!
		overlay_song = song_file.overlay(user2_song)
		overlay_song.export(filepath,format="wav")
		#save to user1 db!
		c.execute('''INSERT into song_table VALUES (?,?,?);''', (user1,song_name, datetime.datetime.now()))


	conn.commit()
	conn.close()


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

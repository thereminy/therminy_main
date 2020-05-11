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


"""
KEY: 
	file_name: file name
	user_name : user's name
	song_seq : song sequence
	time: timestamp
	song_file: returned from string_to_file function
	title : name of song 
	_s : uses songs_db
	_m : uses to music_db
"""

def create_database():
    conn_s = sqlite3.connect(songs_db)  # connect to that database (will create if it doesn't already exist)
    c_s = conn.cursor()  # move cursor into database (allows us to execute commands)
    c_s.execute('''CREATE TABLE song_table (user text, filename text,timing timestamp);''') # run a CREATE TABLE command
    conn_s.commit() # commit commands
    conn_s.close() # close connection to database

music_db = '__HOME__/music.db'
def create_new_database(): 
	"""	
	Creates a database with the new parameter
	"""
	# handles new data base
	conn_m = sqlite3.connect(music_db)
	c_m = conn_m.cursor() 
	c_m.execute('''CREATE TABLE IF NOT EXISTS music_table (user text, filename text, name text, timing timestamp);''')

	# handles old data base 
	conn_s = sqlite3.connect(songs_db)
	c_s = conn_s.cursor() 

	# adds all the songs from an old database
	songs = c_s.execute('''SELECT * FROM song_table ORDER BY timing DESC ;''').fetchall()
	for info in songs: 
		user_name = info[0]
		file_name = info[1]
		time = info[2]
		c_m.execute('''INSERT into music_table VALUES (?,?,?,?);''', (user_name,file_name, "Untitled", time))

	conn_s.commit()	
	conn_s.close()
	conn_m.commit()
	conn_m.close()

def request_handler(request, test = ''):
	if request['method'] ==  'GET':
		# user song file path being played
		user_name = request["values"].get('user',{})
		if user_name == {}:
			return "Must include user in query parameter!"

		conn_m = sqlite3.connect(music_db)
		c_m = conn_m.cursor() 

		user_songs = c_m.execute('''SELECT filename, name FROM music_table where user = ? ORDER BY timing DESC ;''', (user_name,)).fetchall()

		if user_songs is None:
			return "No song files have been stored"

		html_response = []
		# returns list in the form of [name, bytestring, name, bytestring] for every song in all_music 
		for file_name, title in user_songs: 
			html_response.append(title)
			with open(get_file_path(file_name), 'rb') as song: 
				b64_encoded = base64.encodebytes(song.read())
				html_response.append(b64_encoded.decode("utf-8"))
				song.close()

		conn_m.commit()
		conn_m.close()

		return json.dumps(html_response)
	else:
		args = request['form']
		# checks if this request is for changing the name 
		titles = args.get('edit', {})
		# we need to change the name 
		if titles != {}:
			user_name = args['user']
			new_titles = titles.split(',')

			conn_m  = sqlite3.connect(music_db)
			c_m = conn_m.cursor() 
			user_songs = c_m.execute("""SELECT * FROM music_table WHERE user = ? ORDER BY timing DESC """,(user_name,)).fetchall()
			c_m.execute("""DELETE FROM music_table WHERE user = ? """, (user_name,))
			for ind in range(len(user_songs)):
				file_name = user_songs[ind][1]
				time = user_songs[ind][3]
				title = new_titles[ind]
				c_m.execute("""INSERT into music_table VALUES (?,?,?,?);""", (user_name, file_name, title, time))
			conn_m.commit()
			conn_m.close()
		else:
			song_seq = args['song']
			user_name = args['user1']
			instrument = args['instrument'] #guitar/bass/piano
			title = args.get('title','Untitled')

			if instrument not in instruments:
				return "This instrument is not supported."

			option = args['option'] #add/start/[overlay,user]
			song_file = string_to_file(song_seq,instrument)

			if option == 'START':
				startSong(user_name,song_file,title)
				return "Song added to the database!"
			elif option == 'ADD':
				addSong(user_name,song_file,title)
				return "Song added to the database!"
			elif option ==  'OVERLAY':
				user_2 = args['user2']
				overlaySong(user_name,user_2,song_file,title)
				return "Song added to the database!"
			else:
				return "{} is not a supported option.".format(option)

def get_file_path(file_name):
	return "__HOME__/{}".format(file_name)

def startSong(user_name,song_file,title):
	# POST request from ESP32 
	file_name = "song_{}.wav".format(str(time.time()))
	file_path = "/var/jail/home/team091/{}".format(file_name)
	song_file.export(file_path, format="wav")

	conn_m = sqlite3.connect(music_db)
	c_m = conn_m.cursor()
	c_m.execute('''INSERT into music_table VALUES (?,?,?,?);''', (user_name, file_name, title, datetime.datetime.now()))
	conn_m.commit()  # commit commands
	conn_m.close()  # close connection to database

def addSong(user_name,song_file,title):
	file_name = "song_{}.wav".format(str(time.time()))
	file_path = "/var/jail/home/team091/{}".format(file_name)

	conn_m = sqlite3.connect(music_db)
	c_m = conn_m.cursor()
	recent_file = c_m.execute('''SELECT filename FROM music_table WHERE user = ? ORDER BY timing DESC ;''',(user_name,)).fetchone()

	if recent_file is None: #the user is can't add current sequence to empty db, create a new file instead
		startSong(user_name,song_file)
		return "Your database is EMPTY! New song file created for add sequence only"
	else:
		user_song_path = "__HOME__/{}".format(recent_file[0])
		old_song = AudioSegment.from_wav(user_song_path)
		add_song = old_song + song_file
		add_song.export(file_path,format="wav")
		c_m.execute('''INSERT into music_table VALUES (?,?,?,?);''', (user_name,file_name, title, datetime.datetime.now()))
	conn_m.commit()
	conn_m.close()

def overlaySong(user_1,user_2,song_file,title):
	file_name = "song_{}.wav".format(str(time.time()))
	filepath = "/var/jail/home/team091/{}".format(file_name)

	conn_m = sqlite3.connect(music_db)
	c_m = conn_m.cursor()

	recent_file = c_m.execute('''SELECT filename FROM music_table WHERE user = ? ORDER BY timing DESC ;''',(user_2,)).fetchone()

	if recent_file is None: #the user is can't add current sequence to empty db, create a new file instead
		return "{} does not exist!".format(user_2)
	else:
		user_song_path = "__HOME__/{}".format(recent_file[0])
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
		c_m.execute('''INSERT into music_table VALUES (?,?,?,?);''', (user_1,file_name, title, datetime.datetime.now()))
	conn_m.commit()
	conn_m.close()

def string_to_file(song_seq,instrument):
	"""
	:param song_seq: str in the form of notetime&notetime&notetime
	
	Things to note: 
		- notetime : the note is being playing for duration of time
		- 'S' represents silence
		- time is in milliseconds

	Returns an AudioSegment object 
	"""
	# initializes a zero duration Audio Segment 
	song_file = AudioSegment.empty()
	# list of lists in the form of [[note,time], [note,time],[note,time]]
	notes_times = [pair.split(",") for pair in song_seq.split('$')]

	for nt in notes_times:
		note = nt[0]
		if note != "":
			time = float(nt[1])
			if note == 'S':
				# how to add silence: time parameter is in milliseconds
				song_file += AudioSegment.silent(time)
			else: 
				file_path = "__HOME__/note_lib/{}_{}_note.wav".format(instrument,note)
				song_file += AudioSegment.from_wav(file_path)[:time]
	return song_file

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

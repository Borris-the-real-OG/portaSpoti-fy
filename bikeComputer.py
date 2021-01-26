"""
This project was done using a Raspberry Pi 3 B+ and a 3.5in RPi Display from Sunfounder.
This was last tested working with Python 3 on 1/25/20
This code was mostly unedited with the exception of replacing account info with environment variables, changing imports to Python 3, and adding a few comments
Dependencies:
https://spotipy.readthedocs.io/en/2.16.1/
https://docs.wand-py.org/en/0.6.5/
https://docs.python.org/3/library/urllib.request.html#module-urllib.request

I'm 80% sure you need to configure the screen to be vertical
I'm aware you shouldn't declare functions in a conditional :)
"""


import spotipy # Spotify API Python wrapper
import spotipy.client as client
import spotipy.util as util
from urllib.request import urlopen # for retrieving album art
from tkinter import * # for UI
from wand.image import Image # for image processing
import queue
import threading
import os
import time

root = Tk()
root.title("Spotify")
root.attributes('-fullscreen', True)
q = queue.Queue()

username_var= os.environ.get('SPOTIFY-USER') # or just paste your username in here

# scopes available at https://developer.spotify.com/documentation/general/guides/scopes/
# make sure redirect_uri is the same in your Spotify app
# you could also hardcode your client id and client secret
token = util.prompt_for_user_token(username=username_var, scope='user-modify-playback-state, user-read-playback-state', client_id=os.environ.get('CLIENT_ID'), client_secret=os.environ.get('CLIENT_SECRET'), redirect_uri='http://localhost/')

if token:
	sp = spotipy.client.Spotify(auth=token)
	def play():
		currently_playing()
		playback_data = currently_playing.current_data
		playback_state = playback_data['is_playing']
		if playback_state == False:
			sp.start_playback()
			with Image(filename='pause.gif') as img:
				img.save(filename='playback_state.gif')
			playback_state_img = PhotoImage(file='playback_state.gif') 
		else:
			sp.pause_playback()
			with Image(filename='play.gif') as img:
				img.save(filename='playback_state.gif')
			playback_state_img = PhotoImage(file='playback_state.gif')
		play.configure(image=playback_state_img)
		play.image = playback_state_img
	def shuffle():
		currently_playing()
		playback_data = currently_playing.current_data
		shuffle_state = playback_data['shuffle_state']
		if shuffle_state == True:
			sp.shuffle(False)
			with Image(filename='shuffle_off.gif') as img:
				img.save(filename='shuffle_state.gif')
			shuffle_state_img = PhotoImage(file='shuffle_state.gif')
		else:
			sp.shuffle(True)
			with Image(filename='shuffle_on.gif') as img:
				img.save(filename='shuffle_state.gif')
			shuffle_state_img = PhotoImage(file='shuffle_state.gif')
		shuffle.configure(image=shuffle_state_img)
		shuffle.image = shuffle_state_img
	def repeat():
		currently_playing()
		playback_data = currently_playing.current_data
		repeat_state = playback_data['repeat_state']
		if repeat_state == 'off':
			sp.repeat('context')
			with Image(filename='loop_context.gif') as img:
				img.save(filename='loop_state.gif')
			loop_state_img = PhotoImage(file='loop_state.gif')
		elif repeat_state == 'context':
			sp.repeat('track')
			with Image(filename='loop_track.gif') as img:
				img.save(filename='loop_state.gif')
			loop_state_img = PhotoImage(file='loop_state.gif')
		else:
			sp.repeat('off')
			with Image(filename='loop_off.gif') as img:
				img.save(filename='loop_state.gif')
			loop_state_img = PhotoImage(file='loop_state.gif')
		loop.configure(image=loop_state_img)
		loop.image = loop_state_img
	def previous():
		sp.previous_track()
		currently_playing()
		now_playing()
	def next():
		sp.next_track()
		currently_playing()
		now_playing()
	def currently_playing():
		currently_playing.current_data = sp.current_playback()
		duration = currently_playing.current_data['item']['duration_ms']
		elapsed = currently_playing.current_data['progress_ms']
		time_left = duration - elapsed
		root.after(time_left, currently_playing)
	def now_playing():
		global song
		global album
		global artist
		currently_playing()
		playback_data = currently_playing.current_data
		duration = playback_data['item']['duration_ms']
		elapsed = playback_data['progress_ms']
		time_left = duration - elapsed
		track_data = sp.current_user_playing_track()
		album_data = track_data['item']['album']['name']
		artist_data = track_data['item']['artists'][0]['name']
		song_data = track_data['item']['name']
		if len(album_data) > 25:
			ellipsis = '...'
			name = album_data[0:21] + ellipsis
			album.set(name)
		else:
			album.set(album_data)
		if len(artist_data) > 25:
			ellipsis = '...'
			name = artist_data[0:21] + ellipsis
			artist.set(name)
		else:
			artist.set(artist_data)
		if len(song_data) > 25:
			ellipsis = '...'
			name = song_data[0:21] + ellipsis
			song.set(name)
		else:
			song.set(song_data)
		root.after(time_left, now_playing)
	# pretty sure I had to use multithreading because of how tkinter works
	def update_art():
		def callback():
			try:
				test = PhotoImage(file='cover.gif')
			except:
				os.system("cp blank_cover_art.gif cover.gif")
			else:
				return
			finally:
				global art_label
				track_data = sp.current_user_playing_track()
				playing = track_data['is_playing']
				if playing == True:
					try:
						cover_url = track_data['item']['album']['images'][0]['url']
					except:
						with Image(filename='blank_cover_art.gif') as img:
							img.resize(150, 150)
							img.save(filename='cover.gif')
					else:
									cover_url = track_data['item']['album']['images'][0]['url']
									cover = urlopen(cover_url)
									with Image(file=cover) as img:
											with img.convert('gif') as converted:
													converted.resize(150, 150)
													converted.save(filename='cover.gif')
					finally:
						cover = PhotoImage(file='cover.gif')
						art_label.configure(image=cover)
						art_label.image = cover
				else:
					return
		t = threading.Thread(target=callback)
		t.start()
		q.put(callback)
		root.after(5000, update_art)
	#def progress():
	#	currently_playing()
	#	playback_data = currently_playing.current_data
	#	time_elapsed = playback_data['progress_ms']
	#	duration = playback_data['item']['duration_ms']
	#	time_left = duration - time_elapsed
	#	text = time_elapsed, "__________", time_left
	#	e = Entry(root)
	#	e.pack()
	#	if time_left != 0:
	#		time_elapsed += 500
	#		time_left -= 500
	#		e.delete(0, END)
	#		e.insert(0, text)
	#		root.update()
	#	else:
	#		playback_data = currently_playing.current_data
	#	  		time_elapsed = playback_data['progress_ms']
	#			duration = playback_data['item']['duration_ms']
	#	 		time_left = duration - time_elapsed
		#print(duration)
		#print(time_elapsed)
	def bootFunc():
		currently_playing()
		playback_data = currently_playing.current_data

		repeat_state = playback_data['repeat_state']
		if repeat_state == 'context':
			with Image(filename='loop_context.gif') as img:
				img.save(filename='loop_state.gif')
		elif repeat_state == 'track':
			with Image(filename='loop_track.gif') as img:
				img.save(filename='loop_state.gif')
		else:
			with Image(filename='loop_off.gif') as img:
				img.save(filename='loop_state.gif')
		shuffle_state = playback_data['shuffle_state']
		if shuffle_state == True:
			with Image(filename='shuffle_on.gif') as img:
				img.save(filename='shuffle_state.gif')
		else:
			with Image(filename='shuffle_off.gif') as img:
				img.save(filename='shuffle_state.gif')

		playback_state = playback_data['is_playing']
		if playback_state == False:
			with Image(filename='play.gif') as img:
				img.save(filename='playback_state.gif')
		else:
			with Image(filename='pause.gif') as img:
				img.save(filename='playback_state.gif')
	bootFunc()
else:
	print("Error")

album = StringVar()
song = StringVar()
artist = StringVar()

forward_img = PhotoImage(file='forward.gif')
back_img = PhotoImage(file='back.gif')
loop_img = PhotoImage(file='loop_state.gif')
shuffle_img = PhotoImage(file='shuffle_state.gif')
playback_img = PhotoImage(file='playback_state.gif')
art_img = PhotoImage(file='blank_cover_art.gif')

def powerButton():
	off = os.system('sudo shutdown -h now')
	os.system(off)
power_img = PhotoImage(file='power.gif')
power = Button(root, image=power_img, command=powerButton)
power.grid(row=0, column=0, sticky=N+W)

forward = Button(root, image=forward_img, command=next)
forward.grid(row=5, column=3)
backward = Button(root, image=back_img, command=previous)
backward.grid(row=5, column=1)
loop = Button(root, image=loop_img, command=repeat)
loop.grid(row=6, column=3)
shuffle = Button(root, image=shuffle_img, command=shuffle)
shuffle.grid(row=6, column=1)
play = Button(root, image=playback_img, command=play)
play.grid(row=5, column=2)

now_playing()
update_art()

song_label = Label(root, textvariable=song, bg='#282828', fg='#f4f4f4')
song_label.grid(row=2, column=2, columnspan=1, sticky=W)
album_label = Label(root, textvariable=album, bg='#282828', fg='#d3d3d3')
album_label.grid(row=3, column=2, columnspan=1, sticky=W)
artist_label = Label(root, textvariable=artist, bg='#282828', fg='#b0b0b0')
artist_label.grid(row=4, column=2, columnspan=1, sticky=W)
art_label = Label(root, image=art_img)
art_label.grid(row=0, column=2, rowspan=2, columnspan=1)

clock_label = Label(root, bg="#282828", fg="#f4f4f4", font=('Helvetica', 15, 'bold'))
clock_label.grid(row=0, column=3, sticky=N)
date_label = Label(root, bg="#282828", fg="#d3d3d3", anchor=N)
date_label.grid(row=1, column=3, sticky=N)
def clock():
	time_str = time.strftime('%H:%M')
	date_str = time.strftime('%a %m/%d')
	clock_label.config(text=time_str)
	date_label.configure(text=date_str)
	root.after(500, clock)
clock()

def check_queue():
	while True:
		try:
			task = q.get(block=False)
		except:
			break
		else:
			root.after_idle(task)
	root.after(1000, check_queue)
check_queue()
mainloop()

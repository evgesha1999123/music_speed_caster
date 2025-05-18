import os
import tkinter as tk
from tkinter import *
from tkinter import filedialog
import tkinter.messagebox as mb
import customtkinter as ctk
from PIL import Image, ImageTk
import pygame
from pygame import mixer
import pydub
from pydub import AudioSegment
from pydub.playback import play
import threading
import sys
import re
import time
from mutagen.mp3 import MP3
from CTkListbox import *
import eyed3
from pathlib import Path
import music_downloader
from concurrent.futures import ThreadPoolExecutor


# Set the theme and color options
ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green
AUDIO_ALLOW_ANY_CHANGE:int

is_path_valid = False

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title('Music speed caster')
        self.geometry("1300x800")
        self.resizable(False, False)

        self._filepath_ = ''
        self.current_song = None
        self.is_path_valid = False
        self.first_file_start = True
        self.song_lenght = 0
        self.current_slider_pos = 0
        self.magic_button_pressed = False
        self.time_slider_hold = False
        self.speed_multiplier = 0.8
        self.is_stop = True
        self.is_pause = False
        self.current_time = 0

        self.playlist_list = []
        self.last_index_of_playlist = 0

        self.ms_gothic_font = ctk.CTkFont(family = "@MS Gothic", size = 14)

        self.image_open_file = Image.open('resources/icon_open_file.png')
        self.image_play_button = Image.open('resources/icon_play.png')
        self.image_stop_button = Image.open('resources/icon_stop.png')
        self.image_pause_button = Image.open('resources/icon_pause.png')
        self.image_change_speed_button = Image.open('resources/icon_magic.png')
        self.image_settings = Image.open('resources/icon_settings.png')
        self.image_next_track = Image.open('resources/icon_next_track.png')
        self.image_previous_track = Image.open('resources/icon_previous_track.png')
        self.image_rewind_forward = Image.open('resources/icon_rewind_forward.png')
        self.image_rewind_back = Image.open('resources/icon_rewind_back.png')
        self.image_show_playlist = Image.open('resources/icon_show_playlist.png')
        self.image_hide_playlist = Image.open('resources/icon_hide_playlist.png')
        self.image_unknown_almub = Image.open('resources/unknown_album.png')
        self.image_add_track_to_playlist = Image.open('resources/icon_add_track_to_playlist.png')
        self.image_clear_playlist = Image.open('resources/icon_clear_playlist.png')
        self.image_download_tracks = Image.open('resources/icon_download.png')

        self.photo_open_file = ImageTk.PhotoImage(self.image_open_file)
        self.photo_play_button = ImageTk.PhotoImage(self.image_play_button)
        self.photo_stop_button = ImageTk.PhotoImage(self.image_stop_button)
        self.photo_pause_button = ImageTk.PhotoImage(self.image_pause_button)
        self.photo_change_speed_button = ImageTk.PhotoImage(self.image_change_speed_button)
        self.photo_settings_button = ImageTk.PhotoImage(self.image_settings)
        self.photo_next_track = ImageTk.PhotoImage(self.image_next_track)
        self.photo_previous_track = ImageTk.PhotoImage(self.image_previous_track)
        self.photo_rewind_forward = ImageTk.PhotoImage(self.image_rewind_forward)
        self.photo_rewind_back = ImageTk.PhotoImage(self.image_rewind_back)
        self.photo_show_playlist = ImageTk.PhotoImage(self.image_show_playlist)
        self.photo_hide_playlist = ImageTk.PhotoImage(self.image_hide_playlist)
        self.photo_add_track_to_playlist = ImageTk.PhotoImage(self.image_add_track_to_playlist)
        self.photo_clear_playlist = ImageTk.PhotoImage(self.image_clear_playlist)
        self.photo_download_tracks = ImageTk.PhotoImage(self.image_download_tracks)


        self.img = self.image_unknown_almub.resize((400, 400), )

        self.title_image = ImageTk.PhotoImage(image=self.img)

        self.canvas = ctk.CTkLabel(self, text=None, fg_color='gray', image=self.title_image); self.canvas.place(relx=0.4, rely=0.2)

        self.img.close()


        self.pan_button_frame = ctk.CTkFrame(self, width=self._current_width, height=100, fg_color = 'black', bg_color = 'black'); self.pan_button_frame.pack(side = tk.BOTTOM, fill = tk.BOTH, expand = False)

        self.pan_status_frame = ctk.CTkFrame(self, width = self._current_width, height = 100, fg_color = 'dark orange', border_color = 'black', border_width = 10); self.pan_status_frame.pack(side = tk.BOTTOM, fill = tk.BOTH, expand = False)

        self.pan_playlist = ctk.CTkFrame(self, width = 800, height = 800, fg_color = 'black', bg_color = 'black'); self.pan_playlist.pack(side = tk.RIGHT, fill = Y)

        self.button_hide_playlist = ctk.CTkButton(self.pan_playlist, text = None, width = 50, height = 50, image = self.photo_hide_playlist, command = self.hide_playlist); self.button_hide_playlist.place(relx = 0.8, rely = 0.01)

        self.button_show_playlist = ctk.CTkButton(self, text = None, width = 50, height = 50, image = self.photo_show_playlist, command = self.show_playlist)

        self.button_download_tracks = ctk.CTkButton(self.pan_playlist, text="Download tracks", text_color="black", image=self.photo_download_tracks, command=self.download_tracks_and_add_to_playlist)
        self.button_download_tracks.place(relx=0.3, rely=0.9)

        self.button_add_to_playlist = ctk.CTkButton(self.pan_playlist, text="Add tracks", text_color="black", image=self.photo_add_track_to_playlist, command=self.add_to_playlist)
        self.button_add_to_playlist.pack()

        self.button_clear_playlist = ctk.CTkButton(self.pan_playlist, width=50, height=50, text="Clear playlist", text_color="black", image=self.photo_clear_playlist, command=self.clear_playlist)
        self.button_clear_playlist.place(relx=0.3, rely=0.095)

        self.filename_label = ctk.CTkLabel(self.pan_status_frame, text = 'Waiting for opening file', text_color = 'black', font = self.ms_gothic_font)
        self.filename_label.place(relx = 0.4, rely = 0.1)

        self.song_lenght_label = ctk.CTkLabel(self.pan_status_frame, text_color = 'black', font = self.ms_gothic_font)

        self.open_file_button = ctk.CTkButton(self.pan_button_frame, text="Open", font = self.ms_gothic_font, text_color = 'black',
                                               width = 50, height = 50, image = self.photo_open_file, command=self.open_file)
        
        self.open_file_button.place(relx = 0.88, rely = 0.35, anchor = W)

        self.pause_and_play_button = ctk.CTkButton(self.pan_button_frame, text = None, width = 50, height = 50, 
                                                             image = self.photo_play_button, command = self.pause_and_play_button_click_event)
        
        self.pause_and_play_button.place(relx = 0.35, rely = 0.35, anchor = W)

        self.stop_button = ctk.CTkButton(self.pan_button_frame, text = None, width = 50, height = 50, 
                                                   image = self.photo_stop_button, command = self.stop_music)

        self.stop_button.place(relx = 0.55, rely = 0.35, anchor = W)


        self.button_rewind_forward = ctk.CTkButton(self.pan_button_frame, text = None, width = 50, height = 50,
                                                    image = self.photo_rewind_forward, command = self.rewind_forward_click_event)
        
        self.button_rewind_forward.place(relx = 0.4, rely = 0.35, anchor = W)

        self.button_rewind_back = ctk.CTkButton(self.pan_button_frame, text = None, width = 50, height = 50,
                                                 image = self.photo_rewind_back, command = self.rewind_back_click_event)
        
        self.button_rewind_back.place(relx = 0.3, rely = 0.35, anchor = W)

        self.button_next_track = ctk.CTkButton(self.pan_button_frame, text = None, width = 50, height = 50,
                                                image = self.photo_next_track, command = self.next_track_click_event)
        
        self.button_next_track.place(relx = 0.45, rely = 0.35, anchor = W)

        self.button_previous_track = ctk.CTkButton(self.pan_button_frame, text = None, width = 50, height = 50,
                                                    image = self.photo_previous_track, command = self.previous_track_click_event)
        
        self.button_previous_track.place(relx = 0.25, rely = 0.35, anchor = W)

        self.change_speed_button = ctk.CTkButton(self.pan_button_frame, text = None, width = 50, height = 50,
                                                 image = self.photo_change_speed_button, command = self.init_speed_changer_thread)
        
        self.change_speed_button.place(relx = 0.8, rely = 0.35, anchor = W)

        self.time_slider = ctk.CTkSlider(self.pan_status_frame, from_ = 0, to = self.song_lenght, width = 1250, progress_color = 'DodgerBlue4')
        self.time_slider.bind("<ButtonRelease-1>", self.time_slider_event_release)

        self.volume_slider = ctk.CTkSlider(self.pan_button_frame, from_ = 0, to = 1, orientation = "horizontal", progress_color = 'DodgerBlue4')
        self.volume_slider.place(relx = 0.6, rely = 0.5, anchor = W)
        self.volume_slider.bind("<ButtonRelease-1>", self.volume_slider_event)
        self.volume_slider.set(1)

        self.info_label_volume = ctk.CTkLabel(self.pan_button_frame, font = self.ms_gothic_font, text = 'Volume:')
        self.info_label_volume.place(relx = 0.605, rely = 0.1)

        self.settings_button = ctk.CTkButton(self, width = 50, height = 50, text = None, 
                                             image = self.photo_settings_button, command = self.settings_click_event)

        self.settings_button.place(relx = 0.01, rely = 0.01)

        self.progressbar = ctk.CTkProgressBar(self.pan_status_frame, mode = "indeterminate")

        self.playlist = CTkListbox(self.pan_playlist, width = 300, height = 400, bg_color = 'black', command = self.select_track)
        self.playlist.pack(side = 'right')
        

#----------------------------------------------------------------------------Playlist

    def add_to_playlist(self):
        playlist_tuple_abspath = filedialog.askopenfilenames(title="open audiofile", initialdir="~/Музыка", filetypes=[("audio", "*.mp3"), ("audio", "*.wav")])
        playlist_to_add = list(playlist_tuple_abspath)
        step_value = 0
        index = 0

        while index < playlist_to_add.__len__(): 
            self.playlist_list.append(playlist_to_add[index])                                                       #Добавление в глобальный список с треками
            index += 1
            self.last_index_of_playlist += 1
        index = 0

        while index < self.playlist_list.__len__() :
            self.playlist.insert(index, os.path.basename(self.playlist_list[index]))                                #Добавление в плейлист
            index += 1  


    def clear_playlist(self):
        self.playlist.delete(index=ALL)
        self.playlist_list.clear()

    def hide_playlist(self):
        self.pan_playlist.pack_forget()
        self.button_show_playlist.place(relx = 0.95, rely = 0.01)

    def show_playlist(self):
        self.pan_playlist.pack(side = tk.RIGHT, fill = Y)
        self.button_show_playlist.place_forget()

    def download_tracks_and_add_to_playlist(self):
        # downloader_thread = threading.Thread(target=music_downloader.download_tracks, daemon=True)
        # downloader_thread.start()
        # downloader_thread.join()
        # del downloader_thread
        # print(threading.enumerate())
        self.playlist_list = music_downloader.download_tracks()
        # self.filename_label.configure(text = music_downloader.download_tracks.download_status)    
        for index, track in enumerate(self.playlist_list):
            self.playlist.insert(index, os.path.basename(self.playlist_list[index]))


    
    def select_track(self, selected_track):
        print(f'{selected_track} {[self.playlist.curselection()]} {self.playlist_list[self.playlist.curselection()]}')
        self.magic_button_pressed = False
        self.is_path_valid = True
        self.first_file_start = True
        self._filepath_ = self.playlist_list[self.playlist.curselection()]

        if mixer.music.get_busy() == True : self.stop_music()

        self.img.close()

        self.parse_title_image_from_file()

        self.current_song = mixer.Sound(self._filepath_)
        self.filename_label.configure(text = f'Now playing : {selected_track}')
        self.song_lenght = mixer.Sound.get_length(self.current_song)
        self.song_lenght = round(self.song_lenght, 1)

        #if self._filepath_ != '' and self._filepath_ != None : self.stop_music()

        self.time_slider.pack()
        self.time_slider.place(relx = 0.5, rely = 0.5, anchor = CENTER)
        self.time_slider.configure(from_ = 0, to = self.song_lenght)
        self.time_slider.set(0)
        self.song_lenght_label.configure(text = '00:00 / 00:00')
        self.song_lenght_label.pack()
        self.song_lenght_label.place(relx = 0.48, rely = 0.55)
        self.change_speed_button.configure(state = 'normal')

        self.pause_and_play_button_click_event()



    def next_track_click_event(self):
        if self.playlist.curselection() == self.playlist.size() - 1 : return
        else:
            self._filepath_ = self.playlist_list[self.playlist.curselection() + 1]
            self.playlist.activate(self.playlist.curselection() + 1)

    def previous_track_click_event(self):
        if self.playlist.curselection() == 0 : return
        else:
            self._filepath_ = self.playlist_list[self.playlist.curselection() - 1]
            self.playlist.activate(self.playlist.curselection() - 1)


    def parse_title_image_from_file(self):
        audio_file = eyed3.load(self._filepath_)
        try:
            album_name = audio_file.tag.album
            artist_name = audio_file.tag.artist
            for image in audio_file.tag.images:
                image_file = open("cached images/{0} - {1}({2}).jpg".format(artist_name, album_name, image.picture_type), "wb")
                image_name = ('cached images/{0} - {1}({2}).jpg'.format(artist_name, album_name, image.picture_type))
                image_file.write(image.image_data)
                image_file.close()
            
            print(f'>>>>>>>>>>>>IMAGE FILE ::: {image_name}')
            
            self.img = Image.open(image_name)

            self.img = self.img.resize((400, 400), )

            self.title_image = ImageTk.PhotoImage(image = self.img)

            self.canvas.configure(image = self.title_image)
        except: 
            self.img = self.image_unknown_almub

            self.img = self.img.resize((400, 400), )

            self.title_image = ImageTk.PhotoImage(image = self.img)
            self.canvas.configure(image = self.title_image)



    def to_number(self, value):
        if re.match("^\d+?\.\d+?$", value) is None:
            return value.isdigit()
        return True



#-------------------------------------------------------------------------------- Settings Window



    def settings_click_event(self):
        self.settings_button.configure(state = 'disabled')


        self.settings_window = ctk.CTkToplevel(self)
        self.settings_window.attributes("-topmost", True)
        self.settings_window.title('Настройки')
        self.settings_window.geometry('600x300')

        self.settings_window.protocol("WM_DELETE_WINDOW", self.enable_settings_button)

        self.entry_speed_multiplier = ctk.CTkEntry(self.settings_window, width = 50); self.entry_speed_multiplier.pack()
        self.entry_speed_multiplier.place(relx = 0.7, rely = 0.2)
        self.entry_speed_multiplier.bind('<Return>', self.parse_speed_player_value)

        self.button_cancel = ctk.CTkButton(self.settings_window, text = 'Отмена', command = self.enable_settings_button); self.button_cancel.pack()
        self.button_cancel.place(relx = 0.15, rely = 0.9, anchor = S)

        self.button_save_config = ctk.CTkButton(self.settings_window, text = 'Применить', command = self.button_save_config_event); self.button_save_config.pack()
        self.button_save_config.place(relx = 0.85, rely = 0.9, anchor = S)

        self.settings_slider_set_track_speed = ctk.CTkSlider(self.settings_window, from_ = 0.1, to = 3); self.settings_slider_set_track_speed.pack()
        self.settings_slider_set_track_speed.place(relx = 0.3, rely = 0.3) 
        self.settings_slider_set_track_speed.set(0.8)

        self.settings_slider_set_track_speed.bind('<ButtonRelease-1>', self.slider_set_track_speed_event)

        self.settings_slider_set_track_speed_info_label = ctk.CTkLabel(self.settings_window, text = 'Значение скорости воспроизведения:')
        self.settings_slider_set_track_speed_info_label.pack()
        self.settings_slider_set_track_speed_info_label.place(relx = 0.3, rely = 0.2)

        self.speed_multiplier_label_value = ctk.CTkLabel(self.settings_window, text = self.speed_multiplier); self.speed_multiplier_label_value.pack()
        self.speed_multiplier_label_value.place(relx = 0.3, rely = 0.37)



    def enable_settings_button(self):
        self.settings_button.configure(state = 'normal')
        self.settings_window.destroy()



    def button_save_config_event(self):
        self.speed_multiplier = self.speed_multiplier_label_value._text #<---set global value
        if self.entry_speed_multiplier.get() != None and self.entry_speed_multiplier.get() != '' and self.to_number(self.entry_speed_multiplier.get()) == True and (float(self.entry_speed_multiplier.get()) > 0.1 and float(self.entry_speed_multiplier.get()) <= 4):
            self.speed_multiplier = float(self.entry_speed_multiplier.get())
            print(self.speed_multiplier)
            self.settings_button.configure(state = 'normal')
            self.change_speed_button.configure(state = 'normal')
            self.init_speed_changer_thread()
            self.settings_window.destroy()
        else : 
            self.entry_speed_multiplier.configure(border_color = 'red')
            return



    def slider_set_track_speed_event(self, event):
        self.entry_speed_multiplier.configure(border_color = 'gray')
        speed_multiplier_value = self.settings_slider_set_track_speed.get()
        speed_multiplier_value = round(speed_multiplier_value, 2)
        self.speed_multiplier_label_value.configure(text = speed_multiplier_value)

        self.entry_speed_multiplier.delete(0, 'end')
        self.entry_speed_multiplier.insert(1, self.speed_multiplier_label_value._text)



    def parse_speed_player_value(self, event):
        is_number = self.to_number(self.entry_speed_multiplier.get())
        if is_number == True : float_entry_speed_multiplier_value = float(self.entry_speed_multiplier.get())
        else :
            self.entry_speed_multiplier.configure(border_color = 'red')
            return

        if float_entry_speed_multiplier_value >= 0.1 and float_entry_speed_multiplier_value <= 3:
            self.entry_speed_multiplier.configure(border_color = 'gray')
            self.speed_multiplier_label_value.configure(text = float_entry_speed_multiplier_value)
            self.settings_slider_set_track_speed.set(float_entry_speed_multiplier_value)
        else :
            self.entry_speed_multiplier.configure(border_color = 'red')
            return



#------------------------------------------------------------------------------------------- 



    def rewind_forward_click_event(self):
        self.current_time = int(self.time_slider.get())
        if self.current_time >= self.song_lenght or self.is_stop == True or self.is_pause == True : return
        else :
            mixer.music.play(loops = 0, start = int(self.time_slider.get()) + 1)
            self.current_time += 3



    def rewind_back_click_event(self):
        self.current_time = int(self.time_slider.get())
        if self.is_stop == True or self.is_pause == True or self.current_time <= 0 : return
        else:
            if self.current_time <= 3 :
                mixer.music.play(loops = 0, start = - self.time_slider.get())
                self.time_slider.set(0)
                self.song_lenght_label.configure(text = f'00:00 / {time.strftime('%M:%S', time.gmtime(self.song_lenght))}')
                
            else:
                mixer.music.play(loops = 0, start = int(self.time_slider.get()) - 3)
                self.current_time -= 3



    def open_file(self):
        self._filepath_ = filedialog.askopenfilename(title="open audiofile", initialdir="~/Музыка", filetypes=[("audio", "*.mp3"), ("audio", "*.wav"), ("All files", "*.*")])
        if self._filepath_ != '' : 
            self.magic_button_pressed = False
            self.is_path_valid = True
            self.first_file_start = True
            filename = os.path.basename(self._filepath_)
            self.current_song = mixer.Sound(self._filepath_)
            print(self._filepath_)
            self.filename_label.configure(text = f'Now playing : {filename}')
            self.song_lenght = mixer.Sound.get_length(self.current_song)
            self.song_lenght = round(self.song_lenght, 1)

            self.time_slider.pack()
            self.time_slider.place(relx = 0.5, rely = 0.5, anchor = CENTER)
            self.time_slider.configure(from_ = 0, to = self.song_lenght)
            self.time_slider.set(0)
            self.song_lenght_label.configure(text = '00:00 / 00:00')
            self.song_lenght_label.pack()
            self.song_lenght_label.place(relx = 0.48, rely = 0.55)
            self.change_speed_button.configure(state = 'normal')

            self.stop_music()

    def stop_music(self):
        if self._filepath_ != None  and self._filepath_ != '': 
            mixer.music.stop()
            self.pause_and_play_button.configure(image = self.photo_play_button)
            self.first_file_start = True
            self.is_stop = True
            self.song_lenght_label.configure(text = '00:00 / 00:00')
            self.current_time = 0
            self.time_slider.set(0)

    


    def pause_and_play_button_click_event(self):
        if self.magic_button_pressed == True:
            if self.first_file_start == True:
                self._filepath_ = 'tmp/tmp_audiofile.mp3'
                self.current_song = mixer.Sound(self._filepath_)
                self.song_lenght = mixer.Sound.get_length(self.current_song)
                self.song_lenght = round(self.song_lenght, 1)
                self.time_slider.configure(from_ = 0, to = self.song_lenght)

        if self.first_file_start == True:
            if self.is_path_valid == True:
                self.is_stop = False
                self.is_pause = False
                self.first_file_start = False
                mixer.music.load(self._filepath_)
                mixer.music.play()
                self.pause_and_play_button.configure(image = self.photo_pause_button)
                self.watch_track_progress()
        else: 
            if self.is_pause == False:
                mixer.music.pause()
                self.pause_and_play_button.configure(image = self.photo_play_button)
                self.is_pause = True
                
            elif self.is_pause == True:
                mixer.music.unpause()
                self.pause_and_play_button.configure(image = self.photo_pause_button)
                self.is_pause = False
            

    def time_slider_event_release(self, event):
        if self._filepath_ == None or self._filepath_ == '' : return
        else :
            if self.is_pause != True and self.is_stop != True:
                mixer.music.play(loops = 0, start = int(self.time_slider.get()))
                self.current_time = int(self.time_slider.get())
        
        

    def volume_slider_event(self, event):
        mixer.music.set_volume(self.volume_slider.get())

    def change_speed(self):
            self.change_speed_button.configure(state = 'disabled')
            n_song = AudioSegment.from_file(self.playlist_list[self.playlist.curselection()])
            # Manually override the frame_rate. This tells the computer how many
            # samples to play per second
            sound_with_altered_frame_rate = n_song._spawn(n_song.raw_data, overrides={
                "frame_rate": int(n_song.frame_rate * self.speed_multiplier)
            })

            # convert the sound with altered frame rate to a standard frame rate
            # so that regular playback programs will work right. They often only
            # know how to play audio at standard frame rate (like 44.1k)
            try:
                if not os.path.isdir("tmp"): Path("tmp/").mkdir(parents=True, exist_ok=True)
                sound_with_altered_frame_rate.export('tmp/tmp_audiofile.mp3', format = 'mp3')
                self.magic_button_pressed = True
                self.progressbar.place_forget()
                self.stop_music()
                self.pause_and_play_button_click_event()
            except PermissionError:
                mixer.quit()
                sound_with_altered_frame_rate.export('tmp/tmp_audiofile.mp3', format = 'mp3')
                self.magic_button_pressed = True
                self.progressbar.place_forget()
                mixer.init()
                self.stop_music()
                self.pause_and_play_button_click_event()

    
    def init_speed_changer_thread(self):
        if self._filepath_ != None and self._filepath_ != '' :
            self.alt_speed_thread = threading.Thread(target = self.change_speed, daemon = True)
            self.alt_speed_thread.start()
            self.progressbar.place(relx = 0.8, rely = 0.2)
            self.progressbar.start()

    def close_window_event(self):
        try:
            if os.listdir('tmp/') != '':
                os.remove('tmp/tmp_audiofile.mp3')
            app.destroy()
        except PermissionError:
            app.destroy()
        except FileNotFoundError:
            app.destroy()

    def watch_track_progress(self):
        if self.is_stop == True : return
        if self.is_pause == True : pass

        player_time = mixer.music.get_pos() / 1000

        if player_time < 0 : 
            self.stop_music() 
            return

        current_time =  self.current_time + player_time
        
        converted_current_time = time.strftime('%M:%S', time.gmtime(current_time))

        converted_song_lenght = time.strftime('%M:%S', time.gmtime(self.song_lenght))

        if int(current_time) >= int(self.song_lenght) : 
                string_timebar = f'{converted_song_lenght} / {converted_song_lenght}'
                self.song_lenght_label.configure(text = string_timebar)
                self.stop_music()
                return
        
        if current_time < self.song_lenght: current_time += 1

        string_timebar = f'{converted_current_time} / {converted_song_lenght}'

        self.time_slider.set(int(current_time))

        self.song_lenght_label.configure(text = string_timebar)
        self.song_lenght_label.after(450, self.watch_track_progress)

                

# Define app and Create our app's mainloop
if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.close_window_event)
    pygame.init()
    mixer.pre_init(frequency=44100, size = -16, channels=2, buffer=512, devicename=None, allowedchanges=0)
    mixer.init(frequency=44100, size = -16, channels=2, buffer=512, devicename=None, allowedchanges=0)
    app.mainloop()
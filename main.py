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

# AudioSegment.converter = 'D:/VS/Projects/audio/ffmpeg/bin/ffmpeg.exe'
# AudioSegment.ffmpeg = 'D:/VS/Projects/audio/ffmpeg/bin/ffmpeg.exe'
print(">>>>>>>>>>>>>>>>>>>>>>>>>" + AudioSegment.ffmpeg)

# Set the theme and color options
ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

is_path_valid = False

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        #root = customtkinter.CTk()
        pygame.init()

        self.title('Music speed caster')
        self.geometry("400x220")

        self._filepath_ = ''
        self.current_song = None
        self.is_path_valid = False
        self.first_file_start = True
        self.is_play = False
        self.song_lenght = 0
        self.current_slider_pos = 0
        self.magic_button_pressed = False

        self.image_open_file = Image.open('icon_open_file.png')
        self.photo_open_file = ImageTk.PhotoImage(self.image_open_file)
        self.image_play_button = Image.open('icon_play.png')
        self.photo_play_button = ImageTk.PhotoImage(self.image_play_button)
        self.image_stop_button = Image.open('icon_stop.png')
        self.photo_stop_button = ImageTk.PhotoImage(self.image_stop_button)
        self.image_pause_button = Image.open('icon_pause.png')
        self.photo_pause_button = ImageTk.PhotoImage(self.image_pause_button)
        self.image_change_speed_button = Image.open('icon_magic.png')
        self.photo_change_speed_button = ImageTk.PhotoImage(self.image_change_speed_button)

        self.filename_label = ctk.CTkLabel(self, text = 'Waiting for opening file')
        self.filename_label.pack(side = tk.BOTTOM)

        self.song_lenght_label = ctk.CTkLabel(self)

        self.open_file_button = ctk.CTkButton(self, text="load", 
                                                        image = self.photo_open_file, command=self.open_file)
        self.open_file_button.pack()

        self.pause_and_play_button = ctk.CTkButton(self, text = None, width = 50, height = 50, 
                                                             image = self.photo_play_button, command = self.pause_and_play_button_click_event)
        self.pause_and_play_button.pack(side = tk.BOTTOM)
        self.pause_and_play_button.place(relx = 0.35, rely = 0.35, anchor = W)

        self.stop_button = ctk.CTkButton(self, text = None, width = 50, height = 50, 
                                                   image = self.photo_stop_button, command = self.stop_music)
        self.stop_button.pack(side = tk.BOTTOM)
        self.stop_button.place(relx = 0.55, rely = 0.35, anchor = W)

        self.change_speed_button = ctk.CTkButton(self, text = None, width = 50, height = 50,
                                                image = self.photo_change_speed_button, command = self.init_speed_changer_thread)
        self.change_speed_button.pack(side = tk.TOP); self.change_speed_button.place(relx = 0.8, rely = 0)

        self.time_slider = ctk.CTkSlider(self, from_ = 0, to = self.song_lenght)
        self.time_slider.bind("<ButtonRelease-1>", self.time_slider_event)

        self.volume_slider = ctk.CTkSlider(self, from_ = 0, to = 1, orientation = "horizontal"); self.volume_slider.pack()
        self.volume_slider.place(relx = 0.5, rely = 0.7, anchor = CENTER)
        self.volume_slider.bind("<ButtonRelease-1>", self.volume_slider_event)
        self.volume_slider.set(1)

    def open_file(self):
        self._filepath_ = filedialog.askopenfilename(title="open .wav file", filetypes=[("audio", "*.mp3"), ("audio", "*.wav"), ("All files", "*.*")])
        if self._filepath_ != '' : 
            self.magic_button_pressed = False
            self.is_path_valid = True
            self.first_file_start = True
            filename = os.path.basename(self._filepath_)
            self.current_song = mixer.Sound(self._filepath_)
            self.filename_label.configure(text = f'Current track : {filename}')
            self.song_lenght = mixer.Sound.get_length(self.current_song)
            print(self.song_lenght)
            self.song_lenght = round(self.song_lenght, 1)

            self.time_slider.pack()
            self.time_slider.place(relx = 0.5, rely = 0.5, anchor = CENTER)
            self.time_slider.configure(from_ = 0, to = self.song_lenght)
            self.time_slider.set(0)
            self.song_lenght_label.configure(text = self.song_lenght)
            self.song_lenght_label.pack()
            self.song_lenght_label.place(relx = 0.48, rely = 0.55)

    def stop_music(self):
        if self.is_play == True: 
            mixer.music.stop()
            self.pause_and_play_button.configure(image = self.photo_play_button)
            self.is_play = False
            self.first_file_start = True


    def pause_and_play_button_click_event(self):
        if self.magic_button_pressed == True:
            self._filepath_ = 'tmp/tmp_audiofile.mp3'


        if self.first_file_start == True:
            if self.is_path_valid == True:
                mixer.music.load(self._filepath_)
                mixer.music.play()
                print(f'VOLUME {mixer.music.get_volume()}')
                self.pause_and_play_button.configure(image = self.photo_pause_button)
                self.first_file_start = False
                self.is_play = True
        else: 
            if self.is_play == True:
                mixer.music.pause()
                self.pause_and_play_button.configure(image = self.photo_play_button)
                self.is_play = False
            elif self.is_play == False:
                mixer.music.unpause()
                self.pause_and_play_button.configure(image = self.photo_pause_button)
                self.is_play = True
            

    def time_slider_event(self, event):
        print(self.time_slider.get())
        self.current_slider_pos = self.time_slider.get()
        self.current_slider_pos = int(self.current_slider_pos)
        self.song_lenght_label.configure(text = self.current_slider_pos)
        mixer.music.set_pos(self.current_slider_pos)

    def volume_slider_event(self, event):
        mixer.music.set_volume(self.volume_slider.get())
        print(mixer.music.get_volume())

    def change_speed(self, speed = 0.8):
        n_song = AudioSegment.from_mp3(self._filepath_)
        # Manually override the frame_rate. This tells the computer how many
        # samples to play per second
        sound_with_altered_frame_rate = n_song._spawn(n_song.raw_data, overrides={
            "frame_rate": int(n_song.frame_rate * speed)
        })

        # convert the sound with altered frame rate to a standard frame rate
        # so that regular playback programs will work right. They often only
        # know how to play audio at standard frame rate (like 44.1k)
        sound_with_altered_frame_rate.export('tmp/tmp_audiofile.mp3', format = 'mp3')
        self.magic_button_pressed = True
        msg = "Магия работает, используйте на здоровье =)"
        mb.showinfo("Информация", msg)
    
    def init_speed_changer_thread(self):
        self.alt_speed_thread = threading.Thread(target = self.change_speed, daemon = True)
        self.alt_speed_thread.start()

# Define app and Create our app's mainloop
if __name__ == "__main__":
    app = App()
    app.mainloop()
import os
import tkinter as tk
from tkinter import *
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image, ImageTk
import pygame
from pygame import mixer
import wave
import pydub

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
        self.geometry("300x200")

        self._filepath_ = ''
        self.current_song = None
        self.is_path_valid = False
        self.first_file_start = True
        self.is_play = False
        self.song_lenght = 0
        self.current_slider_pos = 0

        self.image_open_file = Image.open('icon_open_file.png')
        self.photo_open_file = ImageTk.PhotoImage(self.image_open_file)
        self.image_play_button = Image.open('icon_play.png')
        self.photo_play_button = ImageTk.PhotoImage(self.image_play_button)
        self.image_stop_button = Image.open('icon_stop.png')
        self.photo_stop_button = ImageTk.PhotoImage(self.image_stop_button)
        self.image_pause_button = Image.open('icon_pause.png')
        self.photo_pause_button = ImageTk.PhotoImage(self.image_pause_button)

        self.filename_label = ctk.CTkLabel(self, text = 'Waiting for opening file')
        self.filename_label.pack(side = tk.BOTTOM)

        self.song_lenght_label = ctk.CTkLabel(self)

        self.open_file_button = ctk.CTkButton(self, text="load", 
                                                        image = self.photo_open_file, command=self.open_file)
        self.open_file_button.pack()

        self.pause_and_play_button = ctk.CTkButton(self, text = None, width = 50, height = 50, 
                                                             image = self.photo_play_button, command = self.pause_and_play_button_click_event)
        self.pause_and_play_button.pack(side = tk.BOTTOM)
        self.pause_and_play_button.place(relx = 0.35, rely = 0.5, anchor = W)

        self.stop_button = ctk.CTkButton(self, text = None, width = 50, height = 50, 
                                                   image = self.photo_stop_button, command = self.stop_music)
        self.stop_button.pack(side = tk.BOTTOM)
        self.stop_button.place(relx = 0.55, rely = 0.5, anchor = W)

        self.time_slider = ctk.CTkSlider(self, from_ = 0, to = self.song_lenght)
        self.time_slider.bind("<ButtonRelease-1>", self.slider_event)

    def open_file(self):
        self._filepath_ = filedialog.askopenfilename(title="open .wav file", filetypes=[("audio", "*.mp3"), ("audio", "*.wav"), ("All files", "*.*")])
        if self._filepath_ != '' : 
            self.is_path_valid = True
            self.first_file_start = True
            filename = os.path.basename(self._filepath_)
            self.current_song = mixer.Sound(self._filepath_)
            self.filename_label.configure(text = f'Current track : {filename}')
            self.song_lenght = mixer.Sound.get_length(self.current_song)
            print(self.song_lenght)
            self.song_lenght = round(self.song_lenght, 1)

            self.time_slider.pack()
            self.time_slider.configure(from_ = 0, to = self.song_lenght)
            self.time_slider.set(0)
            self.song_lenght_label.configure(text = self.song_lenght)
            self.song_lenght_label.pack()

    def stop_music(self):
        if self.is_play == True: 
            mixer.music.stop()
            self.pause_and_play_button.configure(image = self.photo_play_button)
            self.is_play = False
            self.first_file_start = True

    def pause_and_play_button_click_event(self):
        if self.first_file_start == True:
            if self.is_path_valid == True:
                mixer.music.load(self._filepath_)
                mixer.music.play()
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
            

    def slider_event(self, event):
        print(self.time_slider.get())
        self.current_slider_pos = self.time_slider.get()
        self.current_slider_pos = int(self.current_slider_pos)
        self.song_lenght_label.configure(text = self.current_slider_pos)
        mixer.music.set_pos(self.current_slider_pos)

# Define app and Create our app's mainloop
if __name__ == "__main__":
    app = App()
    app.mainloop()
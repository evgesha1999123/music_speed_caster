from tkinter import *
from tkinter import filedialog
import customtkinter
import wave
import pygame
import pydub

# Set the theme and color options
customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

file_path = ''
is_path_valid = False

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        #root = customtkinter.CTk()
        pygame.init()

        self.title('.wav speed changer')
        self.geometry("300x200")

        self._filepath_ = ''
        self.is_path_valid = False
        self.is_player_paused = False

        self.open_file_button = customtkinter.CTkButton(self, text="load .wav", command=self.open_file)
        self.open_file_button.pack(pady=20)
        self.start_button = customtkinter.CTkButton(self, text = 'PLAY', command = self.play_music)
        self.start_button.pack()
        self.stop_button = customtkinter.CTkButton(self, text = 'STOP', command = self.stop_music)
        self.stop_button.pack()
        self.pause_button = customtkinter.CTkButton(self, text = 'PAUSE', command = self.pause_music)
        self.pause_button.pack()

    def open_file(self):
        self._filepath_ = filedialog.askopenfilename(title="open .wav file", filetypes=[("audio", "*.wav"), ("All files", "*.*")])
        if self._filepath_ != '' : 
            print(f'file_path: {self._filepath_}')
            self.is_path_valid = True
    
    def play_music(self):
        if self.is_path_valid == True:
            print(pygame.mixer.get_busy())
            if pygame.mixer.get_busy() == False:
                #wave.open(self._filepath_, mode = 'rb')
                audiofile_to_play = pygame.mixer.Sound(self._filepath_)
                audiofile_to_play.play()
                print(pygame.mixer.get_busy())

    def stop_music(self):
        if pygame.mixer.get_busy() == True : pygame.mixer.stop()

    def pause_music(self):
        if pygame.mixer.get_busy() == True:
            if self.is_player_paused == False: 
                pygame.mixer.pause()
                self.pause_button.configure(text = 'UNPAUSE')
                self.is_player_paused = True
            else:
                pygame.mixer.unpause()
                self.pause_button.configure(text = 'PAUSE')
                self.is_player_paused = False

# Define app and Create our app's mainloop
if __name__ == "__main__":
    app = App()
    app.mainloop()
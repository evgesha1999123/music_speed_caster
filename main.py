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
        self.time_slider_button_release = False
        self.speed_multiplier = 0.8

        self.image_open_file = Image.open('icon_open_file.png')
        self.image_play_button = Image.open('icon_play.png')
        self.image_stop_button = Image.open('icon_stop.png')
        self.image_pause_button = Image.open('icon_pause.png')
        self.image_change_speed_button = Image.open('icon_magic.png')
        self.image_settings = Image.open('icon_settings.png')

        self.photo_open_file = ImageTk.PhotoImage(self.image_open_file)
        self.photo_play_button = ImageTk.PhotoImage(self.image_play_button)
        self.photo_stop_button = ImageTk.PhotoImage(self.image_stop_button)
        self.photo_pause_button = ImageTk.PhotoImage(self.image_pause_button)
        self.photo_change_speed_button = ImageTk.PhotoImage(self.image_change_speed_button)
        self.photo_settings_button = ImageTk.PhotoImage(self.image_settings)

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
        self.change_speed_button.pack(); self.change_speed_button.place(relx = 0.8, rely = 0)

        self.time_slider = ctk.CTkSlider(self, from_ = 0, to = self.song_lenght)
        self.time_slider.bind("<ButtonRelease-1>", self.time_slider_event)

        self.volume_slider = ctk.CTkSlider(self, from_ = 0, to = 1, orientation = "horizontal"); self.volume_slider.pack()
        self.volume_slider.place(relx = 0.5, rely = 0.7, anchor = CENTER)
        self.volume_slider.bind("<ButtonRelease-1>", self.volume_slider_event)
        self.volume_slider.set(1)

        self.settings_button = ctk.CTkButton(self, width = 50, height = 50, text = None, 
                                             image = self.photo_settings_button, command = self.settings_click_event)
        self.settings_button.pack()
        self.settings_button.place(relx = 0.1)

        self.progressbar = ctk.CTkProgressBar(self, mode = "indeterminate"); self.progressbar.pack(); self.progressbar.place(relx = 0.25, rely = 0.8)
        self.progressbar.set(-10)



#----------------------------------------------------------------------------Settings window



    def to_number(self, value):
        if re.match("^\d+?\.\d+?$", value) is None:
            return value.isdigit()
        return True

    def settings_click_event(self):
        self.settings_button.configure(state = 'disabled')


        self.settings_window = ctk.CTkToplevel(self)
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
        self.settings_window.destroy()

    def slider_set_track_speed_event(self, event):
        speed_multiplier_value = self.settings_slider_set_track_speed.get()
        speed_multiplier_value = round(speed_multiplier_value, 2)
        self.speed_multiplier_label_value.configure(text = speed_multiplier_value)

        self.entry_speed_multiplier.delete(0, 'end')
        self.entry_speed_multiplier.insert(1, self.speed_multiplier_label_value._text)

    def parse_speed_player_value(self, event):
        is_number = self.to_number(self.entry_speed_multiplier.get())
        if is_number == True : float_entry_speed_multiplier_value = float(self.entry_speed_multiplier.get())
        else : return

        if float_entry_speed_multiplier_value >= 0.1 and float_entry_speed_multiplier_value <= 3:
            self.speed_multiplier_label_value.configure(text = float_entry_speed_multiplier_value)
            self.settings_slider_set_track_speed.set(float_entry_speed_multiplier_value)
        else : return


    def open_file(self):
        self._filepath_ = filedialog.askopenfilename(title="open audiofile", filetypes=[("audio", "*.mp3"), ("audio", "*.wav"), ("All files", "*.*")])
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
            self.song_lenght_label.configure(text = self.song_lenght)
            self.song_lenght_label.pack()
            self.song_lenght_label.place(relx = 0.48, rely = 0.55)
            self.change_speed_button.configure(state = 'normal')

    def stop_music(self):
        if self.is_play == True: 
            mixer.music.stop()
            self.pause_and_play_button.configure(image = self.photo_play_button)
            self.is_play = False
            self.first_file_start = True
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
                mixer.music.load(self._filepath_)
                mixer.music.play()
                self.init_track_len_watcher_thread()
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
                self.init_track_len_watcher_thread()
            

    def time_slider_event(self, event):
        print(self.time_slider.get())
        self.current_slider_pos = self.time_slider.get()
        self.current_slider_pos = int(self.current_slider_pos)
        self.song_lenght_label.configure(text = self.current_slider_pos)
        self.time_slider_button_release = True
        mixer.music.set_pos(self.current_slider_pos)
        self.track_len_watcher_thread.start()


    def volume_slider_event(self, event):
        mixer.music.set_volume(self.volume_slider.get())
        print(mixer.music.get_volume())

    def change_speed(self):
        if self._filepath_ == None or self._filepath_ == '' : return
        else :
            self.change_speed_button.configure(state = 'disabled')
            n_song = AudioSegment.from_file(self._filepath_)
            # Manually override the frame_rate. This tells the computer how many
            # samples to play per second
            sound_with_altered_frame_rate = n_song._spawn(n_song.raw_data, overrides={
                "frame_rate": int(n_song.frame_rate * self.speed_multiplier)
            })

            # convert the sound with altered frame rate to a standard frame rate
            # so that regular playback programs will work right. They often only
            # know how to play audio at standard frame rate (like 44.1k)
            try:
                sound_with_altered_frame_rate.export('tmp/tmp_audiofile.mp3', format = 'mp3')
                self.magic_button_pressed = True
                msg = "Магия работает, используйте на здоровье =)"
                mb.showinfo("Информация", msg)
                self.stop_music()
            except PermissionError:
                print('>>>>>>>>>>>>>ERROR!!! PermissionError')
                mixer.quit()
                sound_with_altered_frame_rate.export('tmp/tmp_audiofile.mp3', format = 'mp3')
                self.magic_button_pressed = True
                msg = "Магия работает, используйте на здоровье =)"
                mb.showinfo("Информация", msg)
                mixer.init()
            self.progressbar.stop()
    
    def init_speed_changer_thread(self):
        self.alt_speed_thread = threading.Thread(target = self.change_speed, daemon = True)
        self.alt_speed_thread.start()
        self.progressbar.start()

    def init_track_len_watcher_thread(self):
        self.track_len_watcher_thread = threading.Thread(target = self.watch_track_progress, daemon = True)
        self.track_len_watcher_thread.start()
        
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
        print(self.is_play)
        while self.is_play == True:
                current_track_progress = mixer.music.get_pos()
                if self.time_slider_button_release == True: 
                    print(f'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>{self.current_slider_pos}')
                    mixer.music.set_pos(self.current_slider_pos)
                    self.time_slider_button_release = False
                    break
                else:
                    current_track_progress = current_track_progress / 1000
                    current_track_progress = round(current_track_progress, 1)
                    print(current_track_progress)
                    self.time_slider.set(current_track_progress)
                    self.song_lenght_label.configure(text = current_track_progress)
                    if self.is_play == False : break
                    if current_track_progress >= self.song_lenght :
                        self.time_slider.set(0)
                        self.stop_music()
                        break

# Define app and Create our app's mainloop
if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.close_window_event)
    app.mainloop()
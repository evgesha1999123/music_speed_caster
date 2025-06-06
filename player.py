import os
import random
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from typing import Literal

import customtkinter as ctk
import pygame
from pygame import mixer
from pydub import AudioSegment
import threading
import time
from CTkListbox import *
import eyed3
from pathlib import Path

import music_downloader
import asyncio

from utils import Utils
from settings_window import SettingsWindow
from utils.platforms import osinfo

# Set the theme and color options
ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

OS = osinfo()

if OS["system"] == "Linux":
    os.environ['TK_SILENCE_DEPRECATION'] = '1'
    os.environ['XDG_SESSION_TYPE'] = 'x11'  # Принудительно X11 вместо Wayland
    os.environ["__GL_SYNC_TO_VBLANK"] = "1"  # Синхронизация с вертикальной разверткой
    os.environ["__GL_YIELD"] = "USLEEP"  # Оптимизация рендеринга

class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title('Music speed caster')
        self.geometry("782x800")
        self.minsize(782, 800)
        self.resizing = False
        self.last_window_width = self.winfo_width()
        self.last_window_height = self.winfo_height()

        self._filepath_: Path | str = ''
        self.current_song = None
        self.first_file_start = True
        self.song_length = 0
        self.current_slider_pos = 0
        self.magic_button_pressed = False
        self.speed_multiplier = 0.8
        self.is_stop = True
        self.is_pause = False
        self.current_time = 0
        self.zero_time_text = "00:00"

        self.player_mode = "NORMAL"
        self.playlist_state = "SHOW"
        self.album_box_rely = 0.2
        self.album_box_relx_closed_playlist = 0.45
        self.album_box_relx_min_opened_playlist = 0.35
        self.album_box_relx_max_opened_playlist = 0.15
        self.min_win_width_for_playlist: int = 1024
        self.muted = False
        self.playlist_list = []
        self.next_track_index_offset = 1
        self.previous_track_index_offset = -1

        self.album_covers_cache_folder = os.getenv("ALBUM_COVERS_CACHE_FOLDER")

        self.ms_gothic_font = ctk.CTkFont(family = "@MS Gothic", size = 14)

        self.photo_open_file = Utils.get_photo_image_from_source_file("ICON_OPEN_FILE")
        self.photo_play_button = Utils.get_photo_image_from_source_file("ICON_PLAY")
        self.photo_stop_button = Utils.get_photo_image_from_source_file("ICON_STOP")
        self.photo_pause_button = Utils.get_photo_image_from_source_file("ICON_PAUSE")
        self.photo_change_speed_button = Utils.get_photo_image_from_source_file("ICON_MAGIC")
        self.photo_settings_button = Utils.get_photo_image_from_source_file("ICON_SETTINGS")
        self.photo_next_track = Utils.get_photo_image_from_source_file("ICON_NEXT_TRACK")
        self.photo_previous_track = Utils.get_photo_image_from_source_file("ICON_PREVIOUS_TRACK")
        self.photo_rewind_forward = Utils.get_photo_image_from_source_file("ICON_REWIND_FORWARD")
        self.photo_rewind_back = Utils.get_photo_image_from_source_file("ICON_REWIND_BACK")
        self.photo_show_playlist = Utils.get_photo_image_from_source_file("ICON_SHOW_PLAYLIST")
        self.photo_hide_playlist = Utils.get_photo_image_from_source_file("ICON_HIDE_PLAYLIST")
        self.photo_add_track_to_playlist = Utils.get_photo_image_from_source_file("ICON_ADD_TRACK_TO_PLAYLIST")
        self.photo_delete_track_from_playlist = Utils.get_photo_image_from_source_file("ICON_DELETE_TRACK")
        self.photo_clear_playlist = Utils.get_photo_image_from_source_file("ICON_CLEAR_PLAYLIST")
        self.photo_download_tracks = Utils.get_photo_image_from_source_file("ICON_DOWNLOAD")
        self.photo_album_cover = Utils.get_photo_image_from_source_file("ICON_UNKNOWN_ALBUM")
        self.photo_shuffle_tracks = Utils.get_photo_image_from_source_file("ICON_SHUFFLE_TRACKS")
        self.photo_repeat_tracks = Utils.get_photo_image_from_source_file("ICON_REPEAT_TRACKS")
        self.photo_repeat_tracks_enabled = Utils.get_photo_image_from_source_file("ICON_REPEAT_TRACKS_ENABLED")
        self.photo_muted = Utils.get_photo_image_from_source_file("ICON_MUTED")
        self.photo_volume_min = Utils.get_photo_image_from_source_file("ICON_VOLUME_MIN")
        self.photo_volume_normal = Utils.get_photo_image_from_source_file("ICON_VOLUME_NORMAL")
        self.photo_volume_max = Utils.get_photo_image_from_source_file("ICON_VOLUME_MAX")
        self.photo_normal_mode = Utils.get_photo_image_from_source_file("ICON_NORMAL_MODE")

        self.album_box = ctk.CTkLabel(self, text="", fg_color='gray', image=self.photo_album_cover)
        self.album_box.place(relx=self.album_box_relx_closed_playlist, rely=self.album_box_rely)

        self.pan_button_frame = ctk.CTkFrame(self, width=self._current_width, height=100, fg_color='black', bg_color='black')
        self.pan_button_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False)

        self.pan_status_frame = ctk.CTkFrame(self, width=self._current_width, height=100, fg_color='dark orange', border_color='black', border_width=10)
        self.pan_status_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False)

        self.pan_playlist = ctk.CTkFrame(self, width=800, height=800, fg_color='black', bg_color='black')
        self.pan_playlist.pack(side=tk.RIGHT, fill=Y)

        self.button_hide_playlist = ctk.CTkButton(self.pan_playlist, text="", width=50, height=50, image=self.photo_hide_playlist, command=self.hide_playlist)
        self.button_hide_playlist.place(relx=0.8, rely=0.01)

        self.button_show_playlist = ctk.CTkButton(self, text="", width=50, height=50, image=self.photo_show_playlist, command=self.show_playlist)

        self.button_download_tracks = ctk.CTkButton(self.pan_playlist, text="", text_color="black", width=50, height=50, image=self.photo_download_tracks, command=self.download_tracks_and_add_to_playlist)
        self.button_download_tracks.place(relx=0.1, rely=0.9)

        self.button_add_to_playlist = ctk.CTkButton(self.pan_playlist, text="", width=50, height=50, text_color="black", image=self.photo_add_track_to_playlist, command=self.add_to_playlist)
        self.button_add_to_playlist.place(relx=0.3, rely=0.9)

        self.button_delete_track_from_playlist = ctk.CTkButton(self.pan_playlist, text="", width=50, height=50, image=self.photo_delete_track_from_playlist, command=self.on_delete_track_click)
        self.button_delete_track_from_playlist.place(relx=0.5, rely=0.9)

        self.button_clear_playlist = ctk.CTkButton(self.pan_playlist, width=50, height=50, text="", text_color="black", image=self.photo_clear_playlist, command=self.clear_playlist)
        self.button_clear_playlist.place(relx=0.7, rely=0.9)

        self.filename_label = ctk.CTkLabel(self.pan_status_frame, text='Waiting for opening file', text_color='black', font=self.ms_gothic_font, width=self.winfo_width()*0.9)
        self.filename_label.place(relx=0.1, rely=0.1)

        self.song_length_label = ctk.CTkLabel(self.pan_status_frame, text_color='black', font=self.ms_gothic_font)

        self.pause_and_play_button = ctk.CTkButton(self.pan_button_frame, text="", width=50, height=50, image=self.photo_play_button, command=self.pause_and_play_button_click_event)
        self.pause_and_play_button.place(x=10, y=40, anchor=W)

        self.stop_button = ctk.CTkButton(self.pan_button_frame, text="", width=50, height=50, image=self.photo_stop_button, command=self.stop_music)
        self.stop_button.place(x=70, y=40, anchor=W)

        self.button_rewind_back = ctk.CTkButton(self.pan_button_frame, text="", width=50, height=50, image=self.photo_rewind_back, command=self.rewind_back_click_event)
        self.button_rewind_back.place(x=130, y=40, anchor=W)

        self.button_rewind_forward = ctk.CTkButton(self.pan_button_frame, text="", width=50, height=50, image=self.photo_rewind_forward, command=self.rewind_forward_click_event)
        self.button_rewind_forward.place(x=190, y=40, anchor=W)

        self.button_previous_track = ctk.CTkButton(self.pan_button_frame, text="", width=50, height=50,image=self.photo_previous_track,command=lambda: self.next_or_previous_track_click_event(self.previous_track_index_offset))
        self.button_previous_track.place(x=250, y=40, anchor=W)

        self.button_next_track = ctk.CTkButton(self.pan_button_frame, text="", width=50, height=50, image=self.photo_next_track, command=lambda: self.next_or_previous_track_click_event(self.next_track_index_offset))
        self.button_next_track.place(x=310, y=40, anchor=W)

        self.change_speed_button = ctk.CTkButton(self.pan_button_frame, text="", width=50, height=50, image=self.photo_change_speed_button, command=self.init_speed_changer_thread)
        self.change_speed_button.place(x=370, y=40, anchor=W)

        self.button_switch_player_mode = ctk.CTkButton(self.pan_button_frame, text="", width=50, height=50, image=self.photo_normal_mode, command=self.on_switch_player_mode)
        self.button_switch_player_mode.place(x=430, y=40, anchor=W)

        self.time_slider = ctk.CTkSlider(self.pan_status_frame, from_=0, to=self.song_length, width=self.winfo_width() * 0.9, height=20, progress_color='DodgerBlue4')
        self.time_slider.bind("<ButtonRelease-1>", self.time_slider_event_release)

        self.volume_slider = ctk.CTkSlider(self.pan_button_frame, from_=0, to=1, orientation="horizontal", progress_color='DodgerBlue4', width=150, height=20)
        self.volume_slider.place(relx=0.77, rely=0.4, anchor=W)

        self.volume_slider.bind("<B1-Motion>", self.update_volume_drag)
        self.volume_slider.bind("<ButtonRelease-1>", self.end_volume_drag)

        self.volume_slider.set(1)

        self.volume_button = ctk.CTkButton(self.pan_button_frame, text="", width=50, height=50, image=self.photo_volume_max, command=self.on_volume_button_click)
        self.volume_button.place(relx=0.7, rely=0.4, anchor=W)

        self.settings_button = ctk.CTkButton(self, width=50, height=50, text="", image=self.photo_settings_button, command=self.settings_click_event)
        self.settings_button.place(relx=0.01, rely=0.01)

        self.progressbar = ctk.CTkProgressBar(self.pan_status_frame, mode="indeterminate")

        self.playlist = CTkListbox(self.pan_playlist, width=300, height=400, bg_color='black', command=self.select_track)
        self.playlist.pack(side='right')

        if OS["system"] == "Linux":
            self.playlist.bind_all("<Button-4>", lambda event: self.playlist._parent_canvas.yview("scroll", -1, "units"))
            self.playlist.bind_all("<Button-5>", lambda event: self.playlist._parent_canvas.yview("scroll", 1, "units"))

        self.bind("<Configure>", self.on_window_resize)


    def on_window_resize(self, event):
        #print(f"{self.winfo_width()}x{self.winfo_height()}")
        if event.widget != self: return
        if event.width != self.last_window_width or event.height != self.last_window_height:
            self.last_window_width = event.width
            self.last_window_height = event.height

            if not self.resizing:
                self.resizing = True
                if self.playlist_state == "HIDE":
                    self.button_show_playlist.place_forget()
                self.pan_playlist.pack_forget()
                self.pan_button_frame.pack_forget()
                self.pan_status_frame.pack_forget()
                self.album_box.place_forget()
                self.after(0, self.update_layouts)


    def update_layouts(self):
        self.update_time_slider_width()
        self.pan_button_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False)
        self.pan_status_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False)
        if self.playlist_state == "SHOW":
            self.pan_playlist.pack(side=tk.RIGHT, fill=Y)
            self.button_show_playlist.place_forget()
        if self.playlist_state == "HIDE":
            self.button_show_playlist.place(relx=0.9, rely=0.01)
            self.adapt_album_box_widget()
        self.adapt_album_box_widget()
        self.resizing = False


    def adapt_album_box_widget(self):
        if self.playlist_state == "SHOW":
            if self.winfo_width() < self.min_win_width_for_playlist:
                self.album_box.place(relx=self.album_box_relx_max_opened_playlist, rely=self.album_box_rely)
            else:
                self.album_box.place(relx=self.album_box_relx_min_opened_playlist, rely=self.album_box_rely)
        else:
            if self.winfo_width() < self.min_win_width_for_playlist:
                self.album_box.place(relx=self.album_box_relx_min_opened_playlist, rely=self.album_box_rely)
            else:
                self.album_box.place(relx=self.album_box_relx_closed_playlist, rely=self.album_box_rely)


    def update_time_slider_width(self):
        new_time_slider_width = self.winfo_width() * 0.9
        self.time_slider.configure(width=new_time_slider_width)


    def on_volume_button_click(self):
        if not self.muted:
            mixer.music.set_volume(0)
            self.volume_slider.set(0)
            self.volume_button.configure(image=self.photo_muted)
            self.muted = True
        else:
            mixer.music.set_volume(1)
            self.volume_slider.set(1)
            self.volume_button.configure(image=self.photo_volume_max)
            self.muted = False


    def update_volume_slider_width(self):
        new_volume_slider_width = self.winfo_width() * 0.01
        self.volume_slider.configure(width=new_volume_slider_width)
#----------------------------------------------------------------------------Playlist


    def on_switch_player_mode(self):
        match self.player_mode:
            case "NORMAL":
                self.player_mode = "SHUFFLE"
                self.button_switch_player_mode.configure(image=self.photo_shuffle_tracks)
            case "SHUFFLE":
                self.player_mode = "REPEAT"
                self.button_switch_player_mode.configure(image=self.photo_repeat_tracks)
            case "REPEAT":
                self.player_mode = "NORMAL"
                self.button_switch_player_mode.configure(image=self.photo_normal_mode)


    def switch_track(self, next_index, repeat_track=False):
        if repeat_track:
            self.pause_and_play_button_click_event()
            return
        self._filepath_ = self.playlist_list[next_index]
        self.playlist.activate(next_index)


    def next_or_previous_track_click_event(self, offset):
        """
        Бай дефолт CTkListBox, при условии, если выбран первый элемент,
        и мы хотим переключиться на предыдущий, то он будет свитчиться
        в конец списка, поэтому обрабатывать этот случай не нужно.
        """
        playlist_length = len(self.playlist_list) - 1
        current_playlist_selection = self.playlist.curselection()
        first_playlist_element = 0
        is_next_track = offset > 0
        if current_playlist_selection is None: return
        if not self._validate_filepath(): return
        else:
            if self.player_mode == "SHUFFLE":
                self.switch_track(random.randint(0, playlist_length))
            else:
                if current_playlist_selection == playlist_length and is_next_track:
                   self.switch_track(first_playlist_element)
                else:
                    self.switch_track(current_playlist_selection + offset)


    def set_next_track_when_time_ends(self):
        current_playlist_selection = self.playlist.curselection()
        playlist_length = len(self.playlist_list) - 1
        first_playlist_element = 0
        match self.player_mode:
            case "NORMAL":
                if current_playlist_selection == playlist_length:
                    self.switch_track(first_playlist_element)
                else:
                    self.switch_track(current_playlist_selection + 1)
            case "SHUFFLE":
                random_index = random.randint(0, playlist_length)
                self.switch_track(random_index)
            case "REPEAT":
                self.switch_track(current_playlist_selection, repeat_track=True)


    def _validate_filepath(self):
        if self._filepath_ in {"", None}:
            return False
        else: return True


    def add_to_playlist(self):
        playlist_paths_collection: Literal[""] | tuple[str, ...] = filedialog.askopenfilenames(
                title="open audiofile",
                initialdir=os.getenv("SELECT_TRACK_INITIALDIR"),
                filetypes=[("audio", "*.mp3"), ("audio", "*.wav")]
            )
        index = 0
        while index < playlist_paths_collection.__len__():
            #Добавляем только уникальные треки в список
            if playlist_paths_collection[index] in self.playlist_list:
                index += 1
                continue
            self.playlist_list.append(playlist_paths_collection[index])  # Добавление с треками
            self.playlist.insert(index, os.path.basename(self.playlist_list[index])) #Добавление в плейлист
            index += 1

    def on_delete_track_click(self):
        if self.playlist.size() > 0:
            if self.playlist.curselection() is not None:
                self.playlist_list.pop(self.playlist.curselection())
                self.playlist.delete(self.playlist.curselection())
                self.stop_music()
                self._filepath_ = ""

    def download_tracks_and_add_to_playlist(self):
        """Запускает загрузку треков в фоновом потоке"""
        def download_in_thread():
            async def async_download():
                tracks = []
                async for track_path in music_downloader.track_downloader():
                    # Добавляем только уникальные треки в список
                    if track_path in self.playlist_list: continue
                    tracks.append(track_path)
                    # Обновляем UI после каждой загрузки
                    self.after(0, self._update_playlist_item, track_path)
                return tracks

            asyncio.run(async_download())

        # Запускаем в отдельном потоке
        threading.Thread(target=download_in_thread, daemon=True).start()

    def _update_playlist_item(self, track_path):
        """Добавляет один трек в плейлист"""
        track_name = os.path.basename(track_path)
        self.playlist.insert(tk.END, track_name)
        self.playlist_list.append(track_path)


    def clear_playlist(self):
        print(f">>>>>>>>>>>>>>>>{self.playlist.curselection()}")
        self.playlist.delete(index=ALL)
        self.playlist_list.clear()


    def hide_playlist(self):
        if self.playlist_state == "SHOW":
            self.pan_playlist.pack_forget()
            #self.album_box.place(relx=self.album_box_relx_closed_playlist, rely=self.album_box_rely)
            self.button_show_playlist.place(relx = 0.9, rely = 0.01)
            self.playlist_state = "HIDE"
            self.adapt_album_box_widget()


    def show_playlist(self):
        if self.playlist_state == "HIDE":
            self.pan_playlist.pack(side = tk.RIGHT, fill = Y)
            self.button_show_playlist.place_forget()
            self.playlist_state = "SHOW"
            self.adapt_album_box_widget()
    

    def select_track(self, selected_track):
        self.magic_button_pressed = False
        self.first_file_start = True
        self._filepath_ = self.playlist_list[self.playlist.curselection()]

        if mixer.music.get_busy(): self.stop_music()

        self.parse_album_cover_photo_from_file()

        self.current_song = mixer.Sound(self._filepath_)
        self.filename_label.configure(text = f'Now playing : {selected_track}')
        self.song_length = mixer.Sound.get_length(self.current_song)
        self.song_length = round(self.song_length, 1)

        self.time_slider.pack()
        self.time_slider.place(relx = 0.5, rely = 0.5, anchor = CENTER)
        self.time_slider.configure(from_ = 0, to = self.song_length)
        self.time_slider.set(0)
        self.song_length_label.configure(text =f'{self.zero_time_text} / {self.zero_time_text}')
        self.song_length_label.pack()
        self.song_length_label.place(relx = 0.48, rely = 0.55)
        self.change_speed_button.configure(state = 'normal')

        self.pause_and_play_button_click_event()

    
    def parse_album_cover_photo_from_file(self):
        """Извлекает обложку альбома из аудиофайла и сохраняет в кэш, если её там нет"""
        audio_file = eyed3.load(self._filepath_)
        
        # Создаем папку для кэша, если не существует
        os.makedirs(self.album_covers_cache_folder, exist_ok=True)
        
        try:
            album_name = audio_file.tag.album or "Unknown"
            artist_name = audio_file.tag.artist or "Unknown"
            
            # Генерируем уникальное имя файла на основе artist и album
            filename = f"{artist_name}-{album_name}.jpg".replace("/", "_").replace("\\", "_")
            source_image_path = os.path.join(self.album_covers_cache_folder, filename)
            
            # Если файл уже существует - загружаем его
            if os.path.exists(source_image_path):
                self.photo_album_cover = Utils.get_photo_image_from_source_file(source_image_path)
            else:
                # Если файла нет - сохраняем обложку из тегов
                if audio_file.tag.images:
                    image = audio_file.tag.images[0]  # Берем первую обложку
                    with open(source_image_path, "wb") as f:
                        f.write(image.image_data)
                    print(f"Обложка сохранена в кэш: {source_image_path}")
                    self.photo_album_cover = Utils.get_photo_image_from_source_file(source_image_path)
                else:
                    raise Exception("No album art in tags")
                    
        except Exception as e:
            print(f"Ошибка загрузки обложки: {e}")
            # Загружаем обложку по умолчанию
            self.photo_album_cover = Utils.get_photo_image_from_source_file(
                os.getenv("ICON_UNKNOWN_ALBUM")
            )
    
        self.album_box.configure(image=self.photo_album_cover)


    def settings_click_event(self):
        self.settings_button.configure(state='disabled')
        SettingsWindow(self)


    def _validate_rewind_state(self):
        if self.current_time >= self.song_length or self.is_stop or self.is_pause:
            return False
        if self.is_stop or self.is_pause or self.current_time <= 0:
            return False
        return True


    def rewind_forward_click_event(self):
        self.current_time = int(self.time_slider.get())
        if not self._validate_rewind_state() : return
        else :
            mixer.music.play(loops = 0, start = int(self.time_slider.get()) + 3)
            self.current_time += 3


    def rewind_back_click_event(self):
        self.current_time = int(self.time_slider.get())
        if self.is_stop == True or self.is_pause == True or self.current_time <= 0: return
        else:
            if self.current_time <= 3 :
                mixer.music.play(loops=0, start=-self.time_slider.get())
                self.time_slider.set(0)
                self.song_length_label.configure(text=f'{self.zero_time_text} / {time.strftime('%M:%S', time.gmtime(self.song_length))}')
            else:
                mixer.music.play(loops=0, start=int(self.time_slider.get()) - 3)
                self.current_time -= 3


    def stop_music(self):
        if self._validate_filepath(): 
            mixer.music.stop()
            self.pause_and_play_button.configure(image=self.photo_play_button)
            self.first_file_start = True
            self.is_stop = True
            self.song_length_label.configure(text=f'{self.zero_time_text} / {self.zero_time_text}')
            self.current_time = 0
            self.time_slider.set(0)


    def pause_and_play_button_click_event(self):
        if self.magic_button_pressed:
            if self.first_file_start:
                self._filepath_ = os.getenv("ALT_SPEED_CACHE_FILE")
                self.current_song = mixer.Sound(self._filepath_)
                self.song_length = mixer.Sound.get_length(self.current_song)
                self.song_length = round(self.song_length, 1)
                self.time_slider.configure(from_=0, to=self.song_length)

        if self.first_file_start:
            if self._validate_filepath():
                self.is_stop = False
                self.is_pause = False
                self.first_file_start = False
                mixer.music.load(self._filepath_)
                mixer.music.play()
                self.pause_and_play_button.configure(image=self.photo_pause_button)
                self.watch_track_progress()
        else: 
            if not self.is_pause:
                mixer.music.pause()
                self.pause_and_play_button.configure(image=self.photo_play_button)
                self.is_pause = True
                
            elif self.is_pause:
                mixer.music.unpause()
                self.pause_and_play_button.configure(image=self.photo_pause_button)
                self.is_pause = False
            

    def time_slider_event_release(self, event):
        if not self._validate_filepath(): return
        else :
            if self.is_pause != True and self.is_stop != True:
                mixer.music.play(loops=0, start=int(self.time_slider.get()))
                self.current_time = int(self.time_slider.get())

    def update_volume_drag(self, event):
        self.set_volume_and_change_icon()

    def end_volume_drag(self, event):
        self.set_volume_and_change_icon()

    def set_volume_and_change_icon(self):
        mixer.music.set_volume(self.volume_slider.get())
        if self.volume_slider.get() >= 0.6:
            self.volume_button.configure(image=self.photo_volume_max)
        if self.volume_slider.get() < 0.6 >= 0.3:
            self.volume_button.configure(image=self.photo_volume_normal)
        if self.volume_slider.get() < 0.3 > 0:
            self.volume_button.configure(image=self.photo_volume_min)
        if self.volume_slider.get() == 0:
            self.volume_button.configure(image=self.photo_muted)

    
    def set_alter_speed_track(self, sound_with_altered_frame_rate:AudioSegment, force_mixer_reinit=False):
        """
        Принимает аудиосегмент с преобразованной скоростью воспроизведения
        Флаг force_mixer_reinit - для обработки исключения PermissionError
        """
        if force_mixer_reinit: 
            mixer.quit()
        sound_with_altered_frame_rate.export(os.getenv("ALT_SPEED_CACHE_FILE"), format = 'mp3')
        self.magic_button_pressed = True
        self.progressbar.place_forget()
        if force_mixer_reinit: 
            mixer.init()
        self.stop_music()
        self.pause_and_play_button_click_event()



    def change_speed(self):
            self.change_speed_button.configure(state = 'disabled')
            n_song = AudioSegment.from_file(self.playlist_list[self.playlist.curselection()])
            """
            Manually override the frame_rate. This tells the computer how many
            samples to play per second
            """
            sound_with_altered_frame_rate = n_song._spawn(n_song.raw_data, overrides={
                "frame_rate": int(n_song.frame_rate * self.speed_multiplier)
            })

            # convert the sound with altered frame rate to a standard frame rate
            # so that regular playback programs will work right. They often only
            # know how to play audio at standard frame rate (like 44.1k)
            try:
                if not os.path.isdir(os.getenv("ALT_SPEED_CACHE_DIR")): 
                    Path(os.getenv("ALT_SPEED_CACHE_DIR")).mkdir(parents=True, exist_ok=True)
                self.set_alter_speed_track(sound_with_altered_frame_rate)
            except PermissionError:
                self.set_alter_speed_track(sound_with_altered_frame_rate, force_mixer_reinit=True)

    
    def init_speed_changer_thread(self):
        if self._validate_filepath():
            self.alt_speed_thread = threading.Thread(target = self.change_speed, daemon = True)
            self.alt_speed_thread.start()
            self.progressbar.place(relx = 0.8, rely = 0.2)
            self.progressbar.start()


    @staticmethod
    def close_window_event():
        try:
            if os.listdir(os.getenv("ALT_SPEED_CACHE_DIR")) != '':
                os.remove(os.getenv("ALT_SPEED_CACHE_FILE"))
            app.destroy()
        except PermissionError:
            app.destroy()
        except FileNotFoundError:
            app.destroy()


    def watch_track_progress(self):
        if self.is_stop:
            return

        if not self.is_pause:
            player_time = mixer.music.get_pos() / 1000

            # Обработка случая, когда трек закончился
            if player_time < 0:
                # Добавляем небольшую задержку для уверенности, что трек действительно закончился
                if hasattr(self, '_end_timer'):
                    self.stop_music()
                    print("END")
                    self.set_next_track_when_time_ends()
                    return
                else:
                    self._end_timer = True
                    self.song_length_label.after(500, self.watch_track_progress)
                    return
            elif hasattr(self, '_end_timer'):
                del self._end_timer

            current_time = self.current_time + player_time
            converted_current_time = time.strftime('%M:%S', time.gmtime(current_time))
            converted_song_length = time.strftime('%M:%S', time.gmtime(self.song_length))

            # Проверка окончания трека с небольшим допуском
            if current_time >= self.song_length - 0.5:  # -0.5 секунды как допуск
                string_timebar = f'{converted_song_length} / {converted_song_length}'
                self.song_length_label.configure(text=string_timebar)
                self.time_slider.set(int(self.song_length))
                self.stop_music()
                print("END")
                self.set_next_track_when_time_ends()
                return

            # Обновление интерфейса
            string_timebar = f'{converted_current_time} / {converted_song_length}'
            self.time_slider.set(int(current_time))
            self.song_length_label.configure(text=string_timebar)

        self.song_length_label.after(450, self.watch_track_progress)

                

# Define app and Create our app's mainloop
if __name__ == "__main__":
    app = App()
    app.update_idletasks()
    app.protocol("WM_DELETE_WINDOW", app.close_window_event)
    pygame.init()
    mixer.pre_init(frequency=44100, size = -16, channels=2, buffer=512, devicename=None, allowedchanges=0)
    mixer.init(frequency=44100, size = -16, channels=2, buffer=512, devicename=None, allowedchanges=0)
    app.mainloop()
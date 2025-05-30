from tkinter import S
import customtkinter as ctk
from utils import Utils


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent  # Сохраняем ссылку на родительское окно
        self.title('Настройки')
        self.geometry('600x300')
        self.attributes("-topmost", True)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.speed_multiplier = self.parent.speed_multiplier

        self.create_widgets()

    def create_widgets(self):
        self.entry_speed_multiplier = ctk.CTkEntry(self, width=50)
        self.entry_speed_multiplier.place(relx=0.7, rely=0.2)
        self.entry_speed_multiplier.bind('<Return>', self.parse_speed_player_value)

        self.button_cancel = ctk.CTkButton(
            self,
            text='Отмена',
            command=self.on_close
        )
        self.button_cancel.place(relx=0.15, rely=0.9, anchor=S)

        self.button_save_config = ctk.CTkButton(
            self,
            text='Применить',
            command=self.button_save_config_event
        )
        self.button_save_config.place(relx=0.85, rely=0.9, anchor=S)

        self.settings_slider_set_track_speed = ctk.CTkSlider(self, from_=0.1, to=3)
        self.settings_slider_set_track_speed.place(relx=0.3, rely=0.3)
        self.settings_slider_set_track_speed.set(self.speed_multiplier)

        self.settings_slider_set_track_speed.bind('<ButtonRelease-1>', self.slider_set_track_speed_event)

        self.settings_slider_set_track_speed_info_label = ctk.CTkLabel(
            self,
            text='Значение скорости воспроизведения:'
        )
        self.settings_slider_set_track_speed_info_label.place(relx=0.3, rely=0.2)

        self.speed_multiplier_label_value = ctk.CTkLabel(
            self,
            text=str(self.speed_multiplier)
        )
        self.speed_multiplier_label_value.place(relx=0.3, rely=0.37)

    def on_close(self):
        self.parent.settings_button.configure(state='normal')
        self.destroy()

    def button_save_config_event(self):
        try:
            value = float(self.entry_speed_multiplier.get())
            if 0.1 < value <= 4:
                self.speed_multiplier = value
                self.parent.speed_multiplier = value
                self.parent.settings_button.configure(state='normal')
                self.parent.change_speed_button.configure(state='normal')
                self.destroy()
            else:
                self.entry_speed_multiplier.configure(border_color='red')
        except (ValueError, AttributeError):
            self.entry_speed_multiplier.configure(border_color='red')

    def slider_set_track_speed_event(self, event):
        """Обработчик изменения слайдера"""
        value = round(self.settings_slider_set_track_speed.get(), 2)
        self.speed_multiplier_label_value.configure(text=str(value))
        self.entry_speed_multiplier.delete(0, 'end')
        self.entry_speed_multiplier.insert(0, str(value))
        self.entry_speed_multiplier.configure(border_color='gray')

    def parse_speed_player_value(self, event):
        """Обработчик ввода значения скорости"""
        value = self.entry_speed_multiplier.get()
        if Utils.to_number(value) and 0.1 <= float(value) <= 3:
            self.settings_slider_set_track_speed.set(float(value))
            self.entry_speed_multiplier.configure(border_color='gray')
        else:
            self.entry_speed_multiplier.configure(border_color='red')
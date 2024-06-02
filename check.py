from pydub import AudioSegment, playback
from pydub.playback import play
import simpleaudio as sa
import keyboard
import pygame
sound = AudioSegment.from_wav('Music folder/file_example_WAV_1MG.wav')

pygame.init()

def speed_change(sound, speed=1.0):
    # Manually override the frame_rate. This tells the computer how many
    # samples to play per second
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed)
    })

    # convert the sound with altered frame rate to a standard frame rate
    # so that regular playback programs will work right. They often only
    # know how to play audio at standard frame rate (like 44.1k)
    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

# alt = speed_change(sound, 0.8)
# alt.export("filename.mp3", format="mp3")
# pygame.mixer.music.load('Music folder/file_example_WAV_1MG.wav')
# pygame.mixer.music.play()
alt = speed_change(sound, 0.8)
play(alt)
# slow_sound = speed_change(sound, 0.75)
# fast_sound = speed_change(sound, 2.0)
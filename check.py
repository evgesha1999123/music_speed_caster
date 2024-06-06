import yandex_music
import requests

from yandex_music import Client

client = Client()
client.init()
client = Client('token').init()

client.logger
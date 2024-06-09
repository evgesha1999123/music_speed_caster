import eyed3

audio_file = eyed3.load("C:/Users/evgesha/Documents/projects/audio/AAA/Music folder/Only Real - Yesterdays.mp3")
album_name = audio_file.tag.album
artist_name = audio_file.tag.artist
for image in audio_file.tag.images:
    image_file = open("{0} - {1}({2}).jpg".format(artist_name, album_name, image.picture_type), "wb")
    print("Writing image file: {0} - {1}({2}).jpg".format(artist_name, album_name, image.picture_type))
    image_file.write(image.image_data)
    image_file.close()
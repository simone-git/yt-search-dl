from ytmusicapi import YTMusic
from AthenaColor import Fore, Style
import time
from yt_dlp import YoutubeDL
import os
import ffmpeg
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, APIC
from sanitize_filename import sanitize


class TrackInfo:
    def __init__(self):
        self.title = None
        self.artist = None
        self.video_id = None
        self.thumbnail_url = None


# ===== SEARCH ===== #

print(f"{Fore.BlueViolet}Enter your search: {Fore.Yellow}", end="")
search_query = input()
print(Style.Reset, end="")

res = None
try:
    yt = YTMusic()
    res = yt.search(query=search_query, filter="songs")
except:
    print(f"{Style.Bold}{Fore.Orange}Could not search for entries, bye{Style.Reset}")
    exit()


choices = []
ids = []
counter = 0
for i in res:
    if i["resultType"] != "song":
        continue

    duration = i["duration"]

    artist = []
    for a in i["artists"]:
        artist.append(a["name"])
    artist = ", ".join(artist)

    title = i["title"]


    entry = f"{Fore.White}{duration} {Style.Bold}{Fore.Red}{artist}{Style.Reset} {Fore.LimeGreen}{title}"

    print(f"{Fore.Yellow}{counter + 1}{Style.Reset} \t{entry}")
    counter += 1


    obj = TrackInfo()
    obj.title = title
    obj.artist = artist
    obj.video_id = i["videoId"]
    obj.thumbnail_url = i["thumbnails"][-1]["url"]

    choices.append(obj)



# ===== EMPTY RESULT SET ===== #

if len(choices) == 0:
    print(f"{Style.Bold}{Fore.Orange}There are no results for your query, bye{Style.Reset}")
    exit()


# ===== CHOOSE ===== #

print(f"{Fore.BlueViolet}Choose an entry, type anything else to exit: {Fore.Yellow}", end="")
index = input()
print(Style.Reset, end="")


if not str(index).isnumeric():
    print(f"{Style.Bold}{Fore.Orange}Bad index, bye{Style.Reset}")
    exit()
index = int(index) - 1

if index < 0 or index >= counter:
    print(f"{Style.Bold}{Fore.Orange}Out of range, bye{Style.Reset}")
    exit()

choice: TrackInfo = choices[index]


# ===== DOWNLOAD ===== #

dest_parent = os.getcwd()
dest_temp_name = int(time.time() * 1000)
dest_temp_path = f"{dest_parent}/{dest_temp_name}"


dl_opts_track = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioquality': 0,
    "no_warnings": True,
    "outtmpl": f"{dest_temp_path}_track"
}

with YoutubeDL(dl_opts_track) as ydl:
    try:
        error_code = ydl.download([f"https://music.youtube.com/watch?v={choice.video_id}"])
    except:
        print(f"{Style.Bold}{Fore.Orange}Could not download the track, bye{Style.Reset}")
        exit()


exit_code = os.system(f"wget -O \"{dest_temp_path}_thumbnail\" {choice.thumbnail_url}")
if exit_code != 0:
    print(f"{Style.Bold}{Fore.Orange}Could not download the cover art, skip{Style.Reset}")


# ===== CONVERT ===== #

# Track to mp3
dest_name = choice.artist + " - " + choice.title
dest_mp3 = f"{dest_parent}/{sanitize(dest_name)}.mp3"
ffmpeg.input(f"{dest_temp_path}_track").output(dest_mp3).run()


# ===== TAG ===== #

track = MP3(dest_mp3, ID3=ID3)

try:
    track.add_tags()
except:
    pass

track.tags.add(TIT2(encoding=3, text=choice.title))
track.tags.add(TPE1(encoding=3, text=choice.artist))

with open(f"{dest_temp_path}_thumbnail", "rb") as cover_art:
    track.tags.add(
        APIC(
            encodings=3,
            mime="image/jpeg",  # detected MIME type
            type=3,  # front cover art
            desc="Cover Art",
            data=cover_art.read()
        )
    )

track.save()


os.system(f"rm \"{dest_temp_path}_track\"")
os.system(f"rm \"{dest_temp_path}_thumbnail\"")
print(f"{Style.Bold}{Fore.YellowGreen}Done! Bye{Style.Reset}")

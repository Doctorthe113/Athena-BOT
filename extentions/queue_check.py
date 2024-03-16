import nextcord
import random

queues = {} # {guild_id: [url_list, title_list, current_index, loop]}
FFMPEG_OPTIONS = {
    "options": "-vn",
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 60",
}

def queue_make(voice):
    queues[voice.guild.id] = [[], [], 0, False]

def queue_add(voice, songURL, title):
    queues[voice.guild.id][0].append(songURL)
    queues[voice.guild.id][1].append(title)

def queue_del(voice):
    del queues[voice.guild.id]

def queue_grab(voice):
    return queues[voice.guild.id][1]

def queue_loop(voice):
    if queues[voice.guild.id][3]:
        queues[voice.guild.id][3] = False
    else:
        queues[voice.guild.id][3] = True
    return queues[voice.guild.id][3]

def queue_shuffle(voice):
    zippedQueue = zip(queues[voice.guild.id][0], queues[voice.guild.id][1])
    zippedQueue = list(zippedQueue)
    random.shuffle(zippedQueue)
    a, b = zip(*zippedQueue)
    queues[voice.guild.id][0], queues[voice.guild.id][1] = list(a), list(b)

def queue_remove(voice, index):
    del queues[voice.guild.id][0][index]
    del queues[voice.guild.id][1][index]

#? rename the function?
def queue_check(voice):
    queues[voice.guild.id][2] += 1
    index = queues[voice.guild.id][2]
    loop = queues[voice.guild.id][3]
    try:
        songURL = queues[voice.guild.id][0][index]
        track = nextcord.FFmpegPCMAudio(
            songURL,
            **FFMPEG_OPTIONS
        )
        voice.play(track, after=lambda e: queue_check(voice))
    except IndexError:
        if loop == True:
            index = 0
            queues[voice.guild.id][2] = -1
            queue_check(voice)
        else:
            voice.disconnect()
            del queues[voice.guild.id]
        return None
    except nextcord.errors.ClientException:
        return None
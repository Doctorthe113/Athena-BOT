import asyncio
import random
import nextcord
import yt_dlp
from nextcord import Interaction, Embed, Button, ButtonStyle
from nextcord.ui import View, Select
from ytmusicapi import YTMusic


async def delete_message_after_delay(message, delay):
    await asyncio.sleep(delay)
    await message.delete()


class Music_Player:
    def __init__(self):
        # fmt: off
        self.embeds: dict = {} # {guild_id: embed}
        self.voiceCallObjects: dict = {} # {guild_id: VoiceClient}
        self.queues: dict = {} # {guild_id: [url_list, title_ list, current_index, loop, currentSong]}
        self.FFMPEG_OPTIONS: dict = {
            "options": "-vn -ac 2 -acodec libopus -b:a 128k -ar 48000",
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 60 -ac 2",
        }
        self.ytdlObj: yt_dlp.YoutubeDL = yt_dlp.YoutubeDL(
            {
                "format": "bestaudio",
                "quiet": True,
                "no_warnings": True,
                "extract_flat": "in_playlist",
                "cookiefile": "./cookies.txt",


            }
        )
        self.ytMusicObj: YTMusic = YTMusic()
        # fmt: on

    # makes embeds
    async def embed_maker(
        self, descr: str, one: tuple, two: tuple, three: tuple
    ) -> Embed:
        embedObj = Embed(
            title="`================== Music player ==================`",
            description=descr,
            color=0x88B3FA,
        )
        embedObj.set_author(
            name="Athena",
            icon_url="https://cdn.discordapp.com/avatars/1085635807773208616/18fb82af41c2481b7c7c5393496b6c54.webp?size=1024&format=webp&width=0&height=233",
        )
        embedObj.add_field(name=one[0], value=one[1], inline=False)
        embedObj.add_field(name=two[0], value=two[1], inline=False)
        embedObj.add_field(name=three[0], value=three[1], inline=False)
        embedObj.set_footer(
            text="Use the `/` commands and buttons to interact with the music player."
        )
        return embedObj

    # searches for songs on ytmusic. This is used when user wont give a url as input
    def music_search(self, query: str) -> tuple:
        searchRes: dict = self.ytMusicObj.search(query, "songs")
        titles: list = []
        urls: list = []
        for i in searchRes:
            title: str = i.get("title")
            url: str = "https://www.youtube.com/watch?v=" + i.get("videoId")
            titles.append(title)
            urls.append(url)
        return (titles, urls)

    # this is used to intiate the queue for that guild and called when bot joins a vc
    def queue_make(
        self,
        guild: nextcord.Guild,
        voiceCallObj: nextcord.VoiceChannel,
        embedMsg: nextcord.Message,
    ) -> None:
        self.queues[guild.id] = [[], [], 0, False, ""]
        self.voiceCallObjects[guild.id] = voiceCallObj
        self.embeds[guild.id] = embedMsg

    # this is queue_add function "exposed" to the user. User can give both playlist or
    # single song url as input
    async def queue_add_handler(self, guild: nextcord.Guild, query: str) -> None:
        data: dict = self.ytdlObj.extract_info(
            query,
            download=False,
        )
        mediaType: str = data.get("_type", "video")
        if mediaType == "playlist":
            for i in data["entries"]:
                await self.queue_add(guild, i["url"])
        else:
            await self.queue_add(guild, query)

    # this queue is not exposed to the user. It is used internally
    async def queue_add(self, guild: nextcord.Guild, songURL: str) -> None:
        data: dict = self.ytdlObj.extract_info(
            songURL,
            download=False,
        )
        streamUrl: str = data.get("url")
        title: str = data.get("title")
        self.queues[guild.id][0].append(streamUrl)
        self.queues[guild.id][1].append(title)
        await self.queue_list_updater(guild)

    # this is called when bot leaves the vc
    async def queue_del(self, guild: nextcord.Guild) -> None:
        self.queues.pop(guild.id, None)
        self.voiceCallObjects.pop(guild.id, None)
        await self.embeds[guild.id].delete()
        self.embeds.pop(guild.id, None)

    # this is used to grab the queue for that quild. Used for the embed. Returns titles
    def queue_grab(self, guild: nextcord.Guild) -> list:
        return self.queues[guild.id]

    # this is used to toggle the loop. Exposed to the user
    async def queue_loop(self, guild: nextcord.Guild) -> None:
        self.queues[guild.id][3] = not self.queues[guild.id][3]
        await self.queue_list_updater(guild)

    # this is used to shuffle the queue. Exposed to the user
    async def queue_shuffle(self, guild: nextcord.Guild) -> None:
        zippedQueue = zip(self.queues[guild.id][0], self.queues[guild.id][1])
        zippedQueue = list(zippedQueue)
        random.shuffle(zippedQueue)
        a, b = zip(*zippedQueue)
        self.queues[guild.id][0] = list(a)
        self.queues[guild.id][1] = list(b)
        await self.queue_list_updater(guild)

    # this is used to remove a song from the queue. Exposed to the user
    def queue_remove(self, guild: nextcord.Guild, index: int) -> None:
        self.queues[guild.id][0].pop(index)
        self.queues[guild.id][1].pop(index)

    # this is used to update the queue list in the embed. This is used internally
    async def queue_list_updater(self, guild: nextcord.Guild) -> None:
        voiceCallObj: nextcord.VoiceClient = self.voiceCallObjects[guild.id]
        embedMsg: nextcord.PartialInteractionMessage = self.embeds[guild.id]
        loop: bool = self.queues[guild.id][3]

        title: str = "Songs in queue"
        currentSongName: str = self.queues[guild.id][4]
        queueList: str = "\n".join(
            f"{i}. {s}" for i, s in enumerate(self.queues[guild.id][1])
        )
        trancuated: str = ""

        if len(queueList) > 1024:
            queueList = queueList[:1021] + "..."
            trancuated = "Trancuated the list. Use `/queue_show` to see the queue"

        if loop:
            title = "Songs in queue (Looping)"

        embed: nextcord.Embed = await self.embed_maker(
            "Music player",
            (title, queueList),
            ("Currently playing <:player:1214062123953422386>", currentSongName),
            ("", trancuated),
        )

        await embedMsg.edit(embed=embed, view=Player_Buttons(self, voiceCallObj))

    # for next song. This is not exposed to the user
    async def queue_next(self, voiceCallObj: nextcord.VoiceClient) -> None:
        guild: nextcord.Guild = voiceCallObj.guild
        self.queues[guild.id][2] += 1  # increasing the index by 1
        currentSongIndex: int = self.queues[guild.id][2]
        loop: bool = self.queues[guild.id][3]

        try:
            nextSongUrl: str = self.queue_grab(guild)[0][currentSongIndex]
            nextSongName: str = self.queue_grab(guild)[1][currentSongIndex]
            self.queues[guild.id][4] = nextSongName
            await self.queue_list_updater(guild)
            source = await nextcord.FFmpegOpusAudio.from_probe(
                nextSongUrl, **self.FFMPEG_OPTIONS
            )
            voiceCallObj.play(
                source,
                after=lambda e: self.queue_next(voiceCallObj),
            )
        except IndexError:
            if loop:
                currentSongIndex = 0
                self.queues[guild.id][2] = -1  # setting to -1 so when this function is
                await self.queue_next(voiceCallObj)  # called again it will start from 0
            else:
                await self.queue_del(guild)
                await voiceCallObj.disconnect()
                return None
        except nextcord.errors.ClientException:
            return None

    # for start playing. This also works for pause and resuming
    async def play(self, guild: nextcord.Guild) -> None:
        voiceCallObj: nextcord.VoiceClient = self.voiceCallObjects[guild.id]
        if voiceCallObj.is_playing():
            voiceCallObj.pause()
            return None
        if voiceCallObj.is_paused():
            voiceCallObj.resume()
            return None

        firstSongUrl: str = self.queue_grab(guild)[0][0]
        firstSongName: str = self.queue_grab(guild)[1][0]
        self.queues[guild.id][4] = firstSongName
        await self.queue_list_updater(guild)
        source = await nextcord.FFmpegOpusAudio.from_probe(
            firstSongUrl, **self.FFMPEG_OPTIONS
        )
        voiceCallObj.play(
            source,
            after=lambda e: self.queue_next(voiceCallObj),
        )
        return None

    # for skipping
    async def skip(self, guild: nextcord.Guild) -> None:
        voiceCallObj: nextcord.VoiceClient = self.voiceCallObjects[guild.id]
        voiceCallObj.pause()
        await self.queue_next(voiceCallObj)
        return None

    # for previous
    async def previous(self, guild: nextcord.Guild) -> None:
        voiceCallObj: nextcord.VoiceClient = self.voiceCallObjects[guild.id]
        voiceCallObj.pause()
        self.queues[guild.id][2] -= 2  # decreasing the index by 2 so after queue_next()
        await self.queue_next(voiceCallObj)  # it will play the previous song
        return None


class Player_Buttons(View):
    def __init__(
        self, musicPlayerObj: Music_Player, voiceCallObj: nextcord.VoiceChannel
    ):
        self.musicPlayerObj = musicPlayerObj
        self.guild = voiceCallObj.guild
        self.musicPlayerObj.voiceCallObjects[self.guild.id] = voiceCallObj
        super().__init__()
        self.timeout = 3600

    @nextcord.ui.button(label="Repeat", style=ButtonStyle.secondary)
    async def loop_callback(self, button: Button, interaction: Interaction):
        await self.musicPlayerObj.queue_loop(interaction.guild)
        res: nextcord.PartialInteractionMessage = (
            await interaction.response.send_message("Resonse received", ephemeral=True)
        )
        await delete_message_after_delay(res, 0.5)

    @nextcord.ui.button(label="⏮", style=ButtonStyle.primary)
    async def previous_callback(self, button: Button, interaction: Interaction):
        await self.musicPlayerObj.previous(interaction.guild)
        res: nextcord.PartialInteractionMessage = (
            await interaction.response.send_message("Resonse received", ephemeral=True)
        )
        await delete_message_after_delay(res, 0.5)

    @nextcord.ui.button(label="⏯", style=ButtonStyle.danger)
    async def pause_callback(self, button: Button, interaction: Interaction):
        await self.musicPlayerObj.play(interaction.guild)
        res: nextcord.PartialInteractionMessage = (
            await interaction.response.send_message("Resonse received", ephemeral=True)
        )
        await delete_message_after_delay(res, 0.5)

    @nextcord.ui.button(label="⏭", style=ButtonStyle.primary)
    async def skip_callback(self, button: Button, interaction: Interaction):
        await self.musicPlayerObj.skip(interaction.guild)
        res: nextcord.PartialInteractionMessage = (
            await interaction.response.send_message("Resonse received", ephemeral=True)
        )
        await delete_message_after_delay(res, 0.5)

    @nextcord.ui.button(label="Shuffle", style=ButtonStyle.secondary)
    async def shuffle_callback(self, button: Button, interaction: Interaction):
        await self.musicPlayerObj.queue_shuffle(interaction.guild)
        res: nextcord.PartialInteractionMessage = (
            await interaction.response.send_message("Resonse received", ephemeral=True)
        )
        await delete_message_after_delay(res, 0.5)


class Dropdown_Button(Select):
    def __init__(self, urls: list, musicPlayerObj: Music_Player):
        self.urls = urls
        self.musicPlayerObj = musicPlayerObj
        options = [
            nextcord.SelectOption(label=f"Song {i+1}", value=i)
            for i in range(len(urls))
        ]
        super().__init__(
            placeholder="Select a song", min_values=1, max_values=1, options=options
        )

    # this function needs to be named "callback" or it won't work
    async def callback(self, interaction: nextcord.Interaction):
        index: int = int(self.values[0])
        await self.musicPlayerObj.queue_add(interaction.guild, self.urls[index])
        res: nextcord.PartialInteractionMessage = (
            await interaction.response.send_message("Resonse received", ephemeral=True)
        )
        await delete_message_after_delay(res, 0.5)


class Dropdown_View(View):
    def __init__(self, urls: list, musicPlayerObj: Music_Player):
        super().__init__()
        self.add_item(Dropdown_Button(urls, musicPlayerObj))
        self.timeout = 3600

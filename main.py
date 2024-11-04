import discord
import random
import yt_dlp
import asyncio

# Configurações de Intents e opções do FFmpeg/YoutubeDL
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

FFMPEG_OPTIONS = {'options': '-vn'}
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}

client = discord.Client(intents=intents)

# fila de musicas
queue = []

@client.event
async def on_ready():
    print('Bot Online - Hello, World!')
    print(f'Name: {client.user.name}')
    print(f'ID: {client.user.id}')
    print('-------------------------')


# Evento on_message para comandos personalizados
@client.event
async def on_message(message):
    # Ignora mensagens do próprio bot
    if message.author == client.user:
        return

    command = message.content.lower()


    commands_map = {
        '!ola mango': send_greeting,
        '!jogar outra': play_game,
        '!join': join_voice_channel,
        '!leave': stop_voice_channel,
        '!play': play_music,
        '!skip': skip_music,
        '!stop': stop_voice_channel
    }

    # Verifica se o comando está no mapeamento e executa a função correspondente do comando
    if command.split(" ")[0] in commands_map:
        await commands_map[command.split(" ")[0]](message)
    else:
        await message.channel.send("Comando não reconhecido.")



async def send_greeting(message):
    await message.channel.send('Olá! 😁')


async def play_game(message):
    choice = random.randint(1, 2)
    if choice == 1:
        await message.channel.send('Joga mais! 😂')
    else:
        await message.channel.send('Não joga mais, vai se arrepender! 😡😐')


async def join_voice_channel(message):
    if message.author.voice:
        channel = message.author.voice.channel
        try:
            await channel.connect()
        except discord.errors.ClientException:
            await message.channel.send("O bot já está conectado a um canal de voz!")
    else:
        await message.channel.send("Você precisa estar em um canal de voz!")


async def stop_voice_channel(message):
    if message.guild.voice_client:
        await message.guild.voice_client.disconnect()
        await message.channel.send("Desconectado do canal de voz!")
    else:
        await message.channel.send("O bot não está conectado a um canal de voz!")


async def play_music(message):
    if not message.author.voice:
        return await message.channel.send("Você precisa estar em um canal de voz!")

    voice_channel = message.author.voice.channel
    if not message.guild.voice_client:
        await voice_channel.connect()

    search = message.content[len("!play "):]
    if not search:
        return await message.channel.send("Por favor, forneça uma busca ou URL para tocar música.")

    async with message.channel.typing():
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)
            if 'entries' in info:
                info = info['entries'][0]
        url = info['url']
        title = info['title']

    if not message.guild.voice_client.is_playing():
        source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
        message.guild.voice_client.play(source, after=lambda _: asyncio.run_coroutine_threadsafe(play_next(message),
                                                                                                 client.loop))
        await message.channel.send(f"Tocando agora: **{title}**")
    else:
        queue.append((url, title))
        await message.channel.send(f"Adicionado à fila: **{title}**")


async def play_next(message):
    if queue:
        url, title = queue.pop(0)
        source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
        message.guild.voice_client.play(source, after=lambda _: asyncio.run_coroutine_threadsafe(play_next(message),
                                                                                                 client.loop))
        await message.channel.send(f"Tocando agora: **{title}**")
    else:
        await message.channel.send("A fila está vazia!")


async def skip_music(message):
    if message.guild.voice_client and message.guild.voice_client.is_playing():
        message.guild.voice_client.stop()
        await message.channel.send("Pulou ⏩")
    else:
        await message.channel.send("Não há música tocando no momento.")

client.run("")

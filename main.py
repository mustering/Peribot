import discord
import requests
import time
import youtube_dl
import random
from mongoengine import *
import asyncio
from pymongo import MongoClient
import pymongo
import config

connect('autorole_db')

mc = MongoClient()

db = mc.pdb

botUsers = db.botUsers

class ServerAR(Document):
    server_id = StringField(required=True, max_length=22)
    role_id = StringField(required=True, max_length=22)


def moneyInit(gUserId):
    if botUsers.find_one({"id": gUserId}) is None:
        userFile = {
            "id": gUserId,
            "bal": 0
        }
        botUsers.insert_one(userFile)
    return botUsers.find_one({"id" : gUserId})['bal']

def moneyF(gUserId, gBalAdd):
    userBal = moneyInit(gUserId)
    userBal += gBalAdd
    botUsers.update_one({"id": gUserId}, {"$set": {"bal": userBal}})

client = discord.Client()
player = ""
playerList = {}
queList = {}
botJson = ""
hangmanOn = []
autoroleEnabled = {}

with open("hangman.txt") as f:
    hangList = f.read().splitlines()

print(hangList)


async def changeLoop():
    await client.wait_until_ready()
    while True:
        await client.change_presence(game=discord.Game(name="Camp Pining Hearts", type=3))
        await asyncio.sleep(25)
        await client.change_presence(game=discord.Game(name="Lapis", type=2))
        await asyncio.sleep(25)
        await client.change_presence(game=discord.Game(name="peri.help for help"))
        await asyncio.sleep(25)

client.loop.create_task(changeLoop())


def check_que(serverid):
    global queList, playerList
    if queList[serverid] != []:
        playerIn = queList[serverid].pop(0)
        playerList[serverid] = playerIn
        playerIn.start()
    elif queList[serverid] == []:
        del playerList[serverid]


@client.event
async def on_ready():
    rParams = {"user": "CjIOSCi1Ac99Fyy1", "key": "ynWAeatMsLhMrDygahjPvfhW7buBvjqO", "nick": "Peribot"}
    botInstance = requests.post("https://cleverbot.io/1.0/create", data=rParams)
    print(botInstance.json())
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------------------")


@client.event
async def on_member_join(member):
    if ServerAR.objects(server_id=member.server.id) != []:
        for post in ServerAR.objects(server_id=member.server.id):
            roleID = post.role_id
            print(roleID)
        troleTA = discord.utils.get(member.server.roles, id=roleID)
        print(troleTA)
        await client.add_roles(member, troleTA)


@client.event
async def on_message(message):
    global playerList
    global queList
    global player

    print(message.content)

    if message.author == client.user or message.author.bot:
        return

    if message.content.startswith("<@!461190298761035777> ") or message.content.startswith("<@461190298761035777> "):
        if message.content.startswith("<@!461190298761035777> "):
            toSub = "<@!461190298761035777> "
        elif message.content.startswith("<@461190298761035777> "):
            toSub = "<@461190298761035777> "
        subLen = len(message.content) - len(toSub)
        theIndice = int("-" + str(subLen))
        msgContent = message.content[theIndice:]
        rParams = {"user": config.cleverUser, "key": config.cleverKey, "nick": "Peribot",
                   "text": msgContent}
        await client.send_typing(message.channel)
        botResponse = requests.post("https://cleverbot.io/1.0/ask", data=rParams)
        botJson = botResponse.json()
        embed = discord.Embed(color=0x99e70e, description=message.author.mention + " " + botJson['response'])
        embed.set_author(name="Peribot - Cleverbot", icon_url=client.user.avatar_url)
        await client.send_message(message.channel, embed=embed)

    elif message.content.startswith("peri.say "):
        subLen = len(message.content) - len("peri.say ")
        theIndice = int("-" + str(subLen))
        msgContent = message.content[theIndice:]
        if msgContent.startswith("peri.say"):
            theMsg = "You CLOD! Don't try to play tricks with me!"
        else:
            theMsg = msgContent
        embed = discord.Embed(description=theMsg, color=0x99e70e)
        embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
        await client.send_message(message.channel, embed=embed)

    elif message.content.startswith("peri.help"):
        if message.content == 'peri.help':
            embed = discord.Embed(color=0x99e70e, description="Mention me with a message and I will give an adequate response. Use peri.help (category) for information about the commands.\n\n***CATEGORIES:***\n\n**GENERAL**\nGeneral commands that the bot can do.\n\n**GAMES**\nPlay games and have some fun!\n\n**STEVEN UNIVERSE**\nCommands that have everything to do with Steven Universe.\n\n**MUSIC**\nListen to some sweet tunes!\n\n**ADMIN**\nModerate your server better!")
            embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
            await client.send_message(message.channel, embed=embed)
        elif message.content != 'peri.help' and message.content.startswith("peri.help "):
            subLen = len(message.content) - len("peri.help ")
            theIndice = subLen * -1
            msgCons = str.lower(message.content[theIndice:])
            if msgCons == "general":
                embed = discord.Embed(color=0x99e70e, description="***GENERAL COMMANDS:***\n\n**peri.help**\nGet help with the bot.\n\n**peri.say (phrase)**\nGet Peribot to say something that you provide.\n\n**peri.servers**\nGet a list of all the servers Peribot is currently in.\n\n**peri.invite**\nGet a link to invite Peribot to your server.\n\n**peri.poll (question)**\nCreate a poll for a yes/no question.\n\n**peri.suggest (suggestion)**\nSend a suggestion to the bot developers!\n\n**peri.bal/peri.gems/peri.balance**\nFind out how much gems you have obtained.")
                embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
                await client.send_message(message.channel, embed=embed)
            elif msgCons == "games":
                embed = discord.Embed(color=0x99e70e, description="***GAME COMMANDS:***\n\n**peri.8ball (question)**\nGet your question answered with the power of the magic 8Ball.\n\n**peri.rps (rock/paper/scissors)**\nPlay a game of rock paper scissors against Peribot.\n\n**peri.hangman**\nBegins a game of hangman")
                embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
                await client.send_message(message.channel, embed=embed)
            elif msgCons == "steven universe":
                embed = discord.Embed(color=0x99e70e, description="***STEVEN UNIVERSE COMMANDS:***\n\n**peri.searchsu (search query)**\nSearch the Steven Universe Wiki.\n\n**peri.sugif**\nGenerates a random Steven Universe gif from Giphy.")
                embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
                await client.send_message(message.channel, embed=embed)
            elif msgCons == "music":
                embed = discord.Embed(color=0x99e70e, description="***MUSIC COMMANDS:***\n\n**peri.music (YouTube URL)**\nStarts playing music from a YouTube video.\n\n**peri.addmusic (YouTube URL)**\nAdds music to the queue.\n\n**peri.getqueue**\nShow all items that are currently in the music queue.\n\n**peri.musicleave**\nGets the bot to leave the voice channel after music has finished.\n\n**peri.nowplaying**\nShows what is currently playing.")
                embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
                await client.send_message(message.channel, embed=embed)
            elif msgCons == "admin":
                embed = discord.Embed(color=0x99e70e, description="***ADMIN COMMANDS:***\n\n**peri.autorole (role)**\nAutomatically assigns a role to users when they join the server.\n\n**peri.disautorole**\nStops automatically assigning users a role when they join the server.")
                embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
                await client.send_message(message.channel, embed=embed)
            else:
                await client.send_message(message.channel, "That is not a valid help category.")

    elif message.content.startswith("peri.servers"):
        if len(client.servers) == 1:
            plural = "SERVER"
        elif len(client.servers) > 1:
            plural = "SERVERS"
        fMsg = "**CURRENTLY IN " + str(len(client.servers)) + " " + plural + ":**\n"
        for i in client.servers:
            fMsg += "\n" + i.name
        embed = discord.Embed(description=fMsg, color=0x99e70e)
        embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
        await client.send_message(message.channel, embed=embed)

    elif message.content.startswith("peri.music "):
        if message.server.id not in playerList:
            subLen = len(message.content) - len("peri.music ")
            theIndice = int("-" + str(subLen))
            msgUrl = message.content[theIndice:]
            voiceChannel = message.author.voice.voice_channel
            if voiceChannel == None:
                await client.send_message(message.channel, message.author.mention + " you are not currently in a voice channel.")
                return
            voice = client.voice_client_in(message.server)
            if voice is None:
                voice = await client.join_voice_channel(voiceChannel)
            try:
                playerList[message.server.id] = await voice.create_ytdl_player(msgUrl, after=lambda: check_que(message.server.id))
                queList[message.server.id] = []
                playerList[message.server.id].start()
            except:
                await client.send_message(message.channel, "Invalid YouTube URL.")
        else:
            await client.send_message(message.channel, "Music is already playing. Use peri.addmusic to add music to the queue.")

    elif message.content.startswith("peri.addmusic "):
        if message.server.id in playerList:
            subLen = len(message.content) - len("peri.addmusic ")
            theIndice = int("-" + str(subLen))
            msgUrl = message.content[theIndice:]
            voice = client.voice_client_in(message.server)
            try:
                playerList[message.server.id] = await voice.create_ytdl_player(msgUrl, after=lambda: check_que(message.server.id))
                queList[message.server.id].append(playerList[message.server.id])
                await client.send_message(message.channel, "Added to the queue.")
            except:
                await client.send_message(message.channel, "Invalid YouTube URL.")
        else:
            await client.send_message(message.channel, "No music is playing. Use peri.music to start playing music.")

    elif message.content.startswith("peri.getqueue"):
        finalMsg = "**CURRENT VIDEOS IN QUEUE:**\n"
        numcount = 0
        if message.server.id in queList:
            if len(queList[message.server.id]) > 0:
                for i in queList[message.server.id]:
                    numcount += 1
                    finalMsg += "\n" + str(numcount) + ". " + i.title + " - " + time.strftime("%M:%S", time.gmtime(i.duration))
            else:
                finalMsg += "\nThere are no items in the queue."
        else:
            finalMsg += "\nThere are no items in the queue."
        embed = discord.Embed(description=finalMsg, color=0x99e70e)
        embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
        await client.send_message(message.channel, embed=embed)

    elif message.content.startswith("peri.searchsu "):
        subLen = len(message.content) - len("peri.searchsu ")
        theIndice = subLen * -1
        msgConts = message.content[theIndice:]
        params = {"query": msgConts}
        try:
            sureq = requests.get("https://steven-universe.wikia.com/api/v1/Search/List", params=params)
            sujson = sureq.json()
            url = sujson['items'][0]['url']
            await client.send_message(message.channel, url)
        except:
            await client.send_message(message.channel, "No results found.")

    elif message.content.startswith("peri.sugif"):
        reqmake = requests.get("https://api.giphy.com/v1/gifs/random?api_key=" + config.gifKey + "&tag=steven universe&rating=PG")
        reqjson = reqmake.json()
        embedurl = reqjson['data']['images']['original']['url']
        print(embedurl)
        embed = discord.Embed(title="Random Steven Universe Gif Generated by Giphy", color=0x99e70e)
        embed.set_image(url=embedurl)
        embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
        await client.send_message(message.channel, embed=embed)

    elif message.content.startswith("peri.invite"):
        await client.send_message(message.channel, "Invite me to your server: https://discordapp.com/oauth2/authorize?client_id=461190298761035777&scope=bot&permissions=0")


    elif message.content.startswith("peri.musicleave"):
        voice = client.voice_client_in(message.server)
        if voice is not None and message.server.id not in playerList:
            await voice.disconnect()
        elif message.server.id in playerList:
            await client.send_message(message.channel, "The bot can't leave while playing music!")
        else:
            pass

    elif message.content.startswith("peri.poll "):
        subLen = len(message.content) - len("peri.poll")
        tLen = subLen * -1
        msgConts = message.content[tLen:]
        embed = discord.Embed(title=msgConts, description="React :thumbsup: for yes or react :thumbsdown: for no.", color=0x99e70e)
        embed.set_author(name="Poll created by " + message.author.name, icon_url=message.author.avatar_url)
        sentMsg = await client.send_message(message.channel, embed=embed)
        await client.add_reaction(sentMsg, "👍")
        await client.add_reaction(sentMsg, "👎")

    elif message.content.startswith("peri.8ball "):
        subLen = len(message.content) - len("peri.8ball ")
        suLen = subLen * -1
        msgCons = message.content[suLen:]
        responses = ["It is certain.", "It is decidedly so.", "Without a doubt.", "Yes, definitely.", "You may rely on it.", "As I see it, yes.", "Most likely.", "Signs point to yes.", "Reply hazy, try again.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.", "My reply is no.", "My sources say no.", "The outlook is not so good.", "Very doubtful."]
        theResponse = random.choice(responses)
        embed = discord.Embed(title=message.author.name + " asks: " + msgCons, color=0x99e70e, description="🎱 " + theResponse)
        embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
        await client.send_message(message.channel, embed=embed)


    elif message.content.startswith("peri.rps "):
        subLen = len(message.content) - len("peri.rps ")
        suLen = subLen * -1
        userC = str.lower(message.content[suLen:])
        cpC = random.randint(1, 3)
        givenamount = random.randint(1,3)
        print(givenamount)
        if userC != "rock" and userC != "paper" and userC != "scissors":
            await client.send_message(message.channel, "Please enter rock, paper, or scissors.")
        else:
            if userC == "rock" and cpC == 1:
                getBack = "Peribot chose 👊.\n\nIt's a tie."
            elif userC == "rock" and cpC == 2:
                getBack = "Peribot chose 📰.\n\nYou lose."
            elif userC == "rock" and cpC == 3:
                getBack = "Peribot chose ✂.\n\nYou win.\nYou won " + str(givenamount) + " 💎"
                moneyF(message.author.id, givenamount)
            elif userC == "paper" and cpC == 1:
                getBack = "Peribot chose 👊.\n\nYou win.\nYou won " + str(givenamount) + " 💎"
                moneyF(message.author.id, givenamount)
            elif userC == "paper" and cpC == 2:
                getBack = "Peribot chose 📰.\n\nIt's a tie."
            elif userC == "paper" and cpC == 3:
                getBack = "Peribot chose ✂.\n\nYou lose."
            elif userC == "scissors" and cpC == 1:
                getBack = "Peribot chose 👊.\n\nYou lose."
            elif userC == "scissors" and cpC == 2:
                getBack = "Peribot chose 📰.\n\nYou win.\nYou won " + str(givenamount) + " 💎"
                moneyF(message.author.id, givenamount)
            elif userC == "scissors" and cpC == 3:
                getBack = "Peribot chose ✂.\n\nIt's a tie."
        embed = discord.Embed(color=0x99e70e, description=getBack)
        embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
        await client.send_message(message.channel, embed=embed)

    elif message.content.startswith("peri.nowplaying"):
        if message.server.id in playerList:
            playerhere = playerList[message.server.id]
            messageto = "**NOW PLAYING:**\n" + playerhere.title + " - " + time.strftime("%M:%S", time.gmtime(playerhere.duration))
            embed = discord.Embed(color=0x99e70e, description=messageto)
            embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
            await client.send_message(message.channel, embed=embed)
        elif message.server.id not in playerList:
            await client.send_message(message.channel, "No music is currently playing.")

    elif message.content.startswith("peri.hangman"):
        global hangmanOn
        if message.server.id not in hangmanOn:
            guessedLetters = []
            lives = 10
            right = False
            word = str.lower(random.choice(hangList))
            print(word)
            hangmanOn.append(message.server.id)
            hangString = ""
            alphabet = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
            for i in range(len(word)):
                hangString += "?"
            while lives > 0:
                if not right:
                    embed = discord.Embed(color=0x99e70e, description=hangString, title="Guess a letter.")
                    embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
                    embed.set_footer(text=' '.join(guessedLetters))
                    await client.send_message(message.channel, embed=embed)
                guessMsg = await client.wait_for_message(channel=message.channel, author=message.author)
                guess = str.lower(guessMsg.content)
                if guess not in alphabet:
                    await client.send_message(message.channel, "That's not a valid letter.")
                elif guess in guessedLetters:
                    print(guessedLetters)
                    await client.send_message(message.channel, "You already guessed this letter.")
                elif guess not in word:
                    lives -= 1
                    embed = discord.Embed(color=0x99e70e, description="That letter is not in the word. You have " + str(lives) + " lives remaining.", title="Oops!")
                    embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
                    guessedLetters.append(guess)
                    right = False
                    await client.send_message(message.channel, embed=embed)
                elif guess in word:
                    indexes = [index for index in range(len(word)) if word[index] == guess]
                    for i in indexes:
                        print(i)
                        hangLists = list(hangString)
                        hangLists[i] = str.upper(guess)
                        hangString = ''.join(hangLists)
                    embed = discord.Embed(color=0x99e70e, description=hangString, title="You guessed it!")
                    embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
                    guessedLetters.append(guess)
                    embed.set_footer(text=' '.join(guessedLetters))
                    right = True
                    await client.send_message(message.channel, embed=embed)
                if "?" not in hangString:
                    randomPay = random.randint(6,12)
                    await client.send_message(message.channel, "You won!\nYou received " + str(randomPay) + " 💎")
                    moneyF(message.author.id, randomPay)
                    hangmanOn.remove(message.server.id)
                    return
            await client.send_message(message.channel, "Sorry, you lost. The word was " + str.upper(word) + ".")
            hangmanOn.remove(message.server.id)
        elif message.server.id in hangmanOn:
            await client.send_message(message.channel, "A hangman game is already in progress on this server, sorry!")

    elif message.content.startswith("peri.autorole "):
        userperms = message.author.permissions_in(message.channel)
        if not userperms.administrator:
            await client.send_message(message.channel, "You need to be an administrator to use this command.")
            return
        subLen = len(message.content) - len("peri.autorole ")
        suLen = subLen * -1
        addRole = str.lower(message.content[suLen:])
        roleL = message.server.roles
        roleList = roleL + []
        roleListS = roleList + []
        for i in roleList:
            print(i)
            location = roleList.index(i)
            roleList[location] = str.lower(i.name)
        if addRole not in roleList:
            await client.send_message(message.channel, "That role does not exist.")
            return
        locA = roleList.index(addRole)
        roleTA = roleListS[locA]
        clientMem = message.server.me
        perms = clientMem.server_permissions
        canMan = perms.manage_roles
        if not canMan:
            await client.send_message(message.channel, "I don't have permissions to manage roles, you clod!")
            return
        elif roleTA >= clientMem.top_role:
            await client.send_message(message.channel, "That role is too high in the hierarchy for me too manage. Obviously.")
            return
        embed = discord.Embed(description="Auto-role enabled with role " + roleTA.name + ".", color=0x99e70e)
        embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
        await client.send_message(message.channel, embed=embed)
        if list(ServerAR.objects(server_id=message.server.id)) == []:
            print("one")
            postar = ServerAR(server_id=message.server.id, role_id=roleTA.id)
            postar.save()
        else:
            print("two")
            ServerAR.objects(server_id=message.server.id).update_one(set__role_id=roleTA.id)
            postar = list(ServerAR.objects(server_id=message.server.id))[0]
            postar.save()

    elif message.content.startswith("peri.disautorole"):
        userperms = message.author.permissions_in(message.channel)
        if not userperms.administrator:
            await client.send_message(message.channel, "You need to be an administrator to use this command.")
            return
        if ServerAR.objects(server_id=message.server.id) != []:
            postar = list(ServerAR.objects(server_id=message.server.id))[0]
            embed = discord.Embed(description="Auto-role disabled for this server.", color=0x99e70e)
            embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
            await client.send_message(message.channel, embed=embed)
            postar.delete()

    elif message.content.startswith("peri.suggest "):
        appinfo = await client.application_info()
        owner = appinfo.owner
        subLen = len(message.content) - len("peri.suggest ")
        suLen = subLen * -1
        sendMsg = message.content[suLen:]
        await client.send_message(owner, message.author.name + "#" + message.author.discriminator + ": " + sendMsg)
        embed = discord.Embed(title="Your message was sent to the developers.", description="Your message: " + sendMsg, color=0x99e70e)
        embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
        await client.send_message(message.channel, embed=embed)

    elif message.content.startswith("peri.balance") or message.content.startswith("peri.bal") or message.content.startswith("peri.gems"):
        balanceinit = botUsers.find_one({"id" : message.author.id})
        ifi = "'s"
        if message.author.name[-1:] == "s" or message.author.name[-1:] == "S":
            ifi = "'"
        if balanceinit is None:
            embed = discord.Embed(title=message.author.name + ifi + " balance", description="0 💎", color=0x99e70e)
            embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
            await client.send_message(message.channel, embed=embed)
            return
        embed = discord.Embed(title=message.author.name + ifi + " balance", description=str(botUsers.find_one({"id": message.author.id})['bal']) + " 💎", color=0x99e70e)
        embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
        await client.send_message(message.channel, embed=embed)

    elif message.content.startswith("peri.leaderboard"):
        member_list = message.server.members
        id_list = []
        for mem in member_list:
            id_list.append(mem.id)
        leaderboard = ""
        count = 0
        for doc in botUsers.find({"id": {"$in": id_list}}).sort('bal', pymongo.DESCENDING):
            count += 1
            user_get = discord.utils.get(message.server.members, id=doc['id'])
            leaderboard += str(count) + ". " + user_get.name + "#" + user_get.discriminator + " - " + str(doc['bal']) + " 💎\n"
            if count == 5:
                break
        embed = discord.Embed(title="Gems Leaderboard:", description=leaderboard, color=0x99e70e)
        embed.set_author(name="Peribot", icon_url=client.user.avatar_url)
        embed.set_footer(text="Leaderboard for " + message.server.name, icon_url=message.server.icon_url)
        await client.send_message(message.channel, embed=embed)

client.run(config.token)


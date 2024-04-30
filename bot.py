import CheckForUpdates
import discord
from discord.ext import tasks, commands

#Defines my object
yuri = CheckForUpdates.YuriUpdateChecker()

#intents for the bot
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

#defines client
client = discord.Client(intents=intents)
chapterName = ''
chapterLink = ''

#Other stuff
directory = 'C:/Users/Claire/Desktop/YuriChapters/'

#Function that will check if the yuri has been updated and returns a boolean
#This throws an exception if it can't connect to the site, so I put a try here so the bot doesn't crash from that
def yuriCheck():
    try:
        if not yuri.isYuriUpdated():
            return False

    except:
        print("An error occurred.")
    
    return True

#When the bot opens, initiates the loop
@client.event
async def on_ready():
    activity = discord.CustomActivity("reading yuri")
    status = discord.Status
    
    #await client.get_channel(1217278359600365650).send("Ready spaghetti.")
    await client.change_presence(status=status.idle, activity=activity)
    update.start()
    print("Yuri Bot.")


#text events
@client.event
async def on_message(message):
    channel = client.get_channel(1217278359600365650)
    #Manually updates yuri
    if message.content.startswith(".update"):
        if not yuriCheck():
            await channel.send('<@170152078713290752> New Chapter: **' + yuri.getChapterName() + "**\nhttps://dynasty-scans.com" + yuri.getChapterLink())
        else:
            await channel.send('No new yuri updates.') 

    #Pings bot to see if its still alive
    if message.content.startswith("ping"):
        await message.channel.send("pong")

    if message.content.startswith(".chapter"):
        url = message.content.split(".chapter")[1]
        await channel.send('Downloading ' + chapterName + '...')
        try:
            yuri.downloadChapter(directory, yuri.getYuriName(url), yuri.getChapterNameFromLink(url), url.split("https://dynasty-scans.com")[1])

        except:
            await channel.send('An error occurred.')
            
        else:
            await channel.send('Downloading finished.')

    if message.content.startswith(".full"):
        url = message.content.split(".full")[1]
        await channel.send('Downloading ' + chapterName + '...')
        try:
            yuri.downloadFullYuri(directory, url)

        except:
            await channel.send('An error occurred.')
            
        else:
            await channel.send('Downloading finished.')

        
#Downloads the chpater reacted to to the directory specified above
@client.event
async def on_raw_reaction_add(reaction):
    messageID = reaction.message_id
    channel = client.get_channel(1217278359600365650)
    message = await channel.fetch_message(messageID)
    messageText = message.content
    if messageText.startswith('<@170152078713290752>'):
        chapterLink = messageText.split('https://dynasty-scans.com')[1]
        chapterNameList = messageText.split('https://dynasty-scans.com')[0].split(': ')

        #This messes up if there is a colon in the chapter name, so I'll attempt to fix that.
        i = 1
        chapterName = ""
        while i < len(chapterNameList):
            chapterName = chapterName + chapterNameList[i]
            i = i + 1
        
        chapterName = chapterName.split('**')[1]
        yuriName = yuri.getYuriName('https://dynasty-scans.com' + chapterLink)

        await channel.send('Downloading ' + chapterName + '...')
        try:
            yuri.downloadChapter(directory, yuriName, chapterName, chapterLink)

        except:
            await channel.send('An error occurred.')
            
        else:
            await channel.send('Downloading finished.')

#loop that checks periodically if the list has been updated. compares to predtermined list
#Sends message if the yuri was updated
@tasks.loop(minutes=3)
async def update():
    if not yuriCheck():
        await client.get_channel(1217278359600365650).send('<@170152078713290752> New Chapter: **' + yuri.getChapterName() + "**\nhttps://dynasty-scans.com" + yuri.getChapterLink())
    
    
client.run('MTIxNjUxNTYzNzM2NzY2ODc5Ng.GBQ0vb.ThIMmmIlAtMKHd2YC6ypO-YNeFWZcs0IjX4DRY')

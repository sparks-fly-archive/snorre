import discord
import mysql.connector
import os
import re 
import random

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    # dummy message
    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)
    
    # random inplay quote
    if message.content.startswith('!quote'):
        cnx = mysql.connector.connect(user=os.getenv('USER'), password=os.getenv('PASS'),
                              host=os.getenv('HOST'),
                              database=os.getenv('DATABASE'))
        cursor = cnx.cursor()
        query = ("SELECT quote, username FROM mybb_inplayquotes LEFT JOIN mybb_users ON mybb_users.uid = mybb_inplayquotes.uid WHERE mybb_inplayquotes.uid IN(SELECT uid FROM mybb_users) ORDER BY RAND() LIMIT 1")
        cursor.execute(query)
        for quote, username in cursor:
            if username != None:
                msg = "*{}* - {}".format(quote, username)
                await client.send_message(message.channel, msg)
        cnx.close()
    
    # inplay postings count
    if message.content.startswith('!count'):
        cnx = mysql.connector.connect(user=os.getenv('USER'), password=os.getenv('PASS'),
                              host=os.getenv('HOST'),
                              database=os.getenv('DATABASE'))  
        cursor = cnx.cursor()
        query = ("SELECT COUNT(*) AS ipcount FROM mybb_posts LEFT JOIN mybb_threads ON mybb_posts.tid = mybb_threads.tid WHERE mybb_threads.partners != ''")
        cursor.execute(query)
        ipcount = str(cursor.fetchone()[0])
        ipcount.strip("(")
        ipcount.strip(")")
        ipcount.strip(",")
        msg = "Das Forum zählt aktuell {} Inplayposts!".format(ipcount)
        await client.send_message(message.channel, msg)
        cnx.close()
    
    # let's dice for fun
    if message.content.startswith('!dice'):
        dice = str(message.content.split()[1])
        if dice == None:
            dice = "1d6"
        count = int(dice.split('d')[0])
        eyes = int(dice.split('d')[1])
        i = 0
        while i < count: 
            number = random.randint(1,eyes)
            msg = "Gewürfelte Zahl: {}".format(number)
            await client.send_message(message.channel, msg)
            i += 1
        
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(os.getenv('TOKEN'))

import discord
import mysql.connector
import os
import re 
import random
import datetime

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
        msg = "Das Forum zählt aktuell {} Inplayposts!".format(ipcount)
        await client.send_message(message.channel, msg)
        cnx.close()
    
    # let's dice for fun
    if message.content.startswith('!dice'):
        try:
            dice = str(message.content.split()[1])
        except IndexError:
            pass
            dice = "1d6"
        count = int(dice.split('d')[0])
        eyes = int(dice.split('d')[1])
        i = 0
        while i < count: 
            number = random.randint(1,eyes)
            msg = "Gewürfelte Zahl: {}".format(number)
            await client.send_message(message.channel, msg)
            i += 1
            
    # random character
    if message.content.startswith('!someone'):
        cnx = mysql.connector.connect(user=os.getenv('USER'), password=os.getenv('PASS'),
                              host=os.getenv('HOST'),
                              database=os.getenv('DATABASE'))  
        cursor = cnx.cursor()
        try:
            name = str(message.content.split()[2])
            if name != None:
                name = "%"
        except IndexError:
            pass
            try:
                name = str(message.content.split()[1])
            except IndexError:
                pass
                name = "%" 
        cursor.execute("SELECT username FROM mybb_users LEFT JOIN mybb_userfields ON mybb_userfields.ufid = mybb_users.uid WHERE fid1 LIKE %s AND username != 'Snorre' ORDER BY RAND() LIMIT 1", (name,))
        username = str(cursor.fetchone()[0])
        await client.send_message(message.channel, username)
        cnx.close()
        
    # last inplay post
    if message.content.startswith('!lastpost'):
        cnx = mysql.connector.connect(user=os.getenv('USER'), password=os.getenv('PASS'),
                              host=os.getenv('HOST'),
                              database=os.getenv('DATABASE')) 
        cursor = cnx.cursor(buffered=True)
        usercursor = cnx.cursor(buffered=True)
        name = str(message.content.split()[1])
        msg = "Die letzten Posts von _{}_:".format(name)
        await client.send_message(message.channel, msg)
        cursor.execute("SELECT uid, username FROM mybb_users LEFT JOIN mybb_userfields ON mybb_userfields.ufid = mybb_users.uid WHERE fid1 LIKE %s", (name,))
        for (uid, username) in cursor:
            uid = str(uid)
            username = str(username)
            usercursor.execute("SELECT mybb_posts.dateline FROM mybb_posts LEFT JOIN mybb_threads ON mybb_threads.tid = mybb_posts.tid WHERE mybb_threads.partners != '' AND mybb_posts.uid = %s ORDER BY pid DESC LIMIT 1", (uid,))
            for dateline in usercursor:
                dateline = str(dateline)
                dateline = dateline.strip("(")
                dateline = dateline.strip(")")
                dateline = dateline.strip(",")
                print(dateline)
                lastpost = datetime.datetime.fromtimestamp(int(dateline)).strftime('%d.%m.%Y')
            if usercursor.fetchone() != None:
                msg = "{}: {}".format(username, lastpost)
                await client.send_message(message.channel, msg)
        cnx.close() 
        
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(os.getenv('TOKEN'))

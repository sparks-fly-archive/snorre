import discord
import mysql.connector
from mysql.connector import errorcode
import os

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)
    if message.content.startswith('!quote'):
        cnx = mysql.connector.connect(user=os.getenv('USER'), password=os.getenv('PASS'),
                              host=os.getenv('HOST'),
                              database=os.getenv('DATABASE'))
        cursor = cnx.cursor()
        query = ("SELECT quote, username FROM mybb_inplayquotes LEFT JOIN mybb_users ON mybb_users.uid = mybb_inplayquotes.uid ORDER BY RAND() LIMIT 1")
        cursor.execute(query)
        for quote, username in cursor:
            if username != None:
                msg = "\"{}\" - {}".format(quote, username)
                await client.send_message(message.channel, msg)
        cnx.close()


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(os.getenv('TOKEN'))

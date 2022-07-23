# creates a string formatted for hlorenzi's gameboards table maker
# !scoreboard 4 miarun, usagi, Jeanne, ANIMALSASLEADERS, ta_go, FULLPOWER, kerokke, Takagisan, tracks, dasu_go, Slowbro, megane

# This ^ shouldn't be necessary anymore with the new bot that I want to make







# ^lt - In 150 lounge, this command takes this entire multiline input and parses through to find each team, and instructs the user to enter scores in order (top down, left right) 
# ---
# Poll Ended!

# 1. FFA - 0
# 2. 2v2 - 6 (Ayaka, babycartel, Syndicate, Demani, ShadowMK, Trae)
# 3. 3v3 - 0
# 4. 4v4 - 0
# 6. 6v6 - 0
# Winner: 2v2

# Room MMR: 4818
# Team 1: Euan, babycartel (MMR: 7800)
# Team 2: ShadowMK, Trae (MMR: 6633)
# Team 3: Splinkle, Warp Star (MMR: 4342)
# Team 4: gomigomi, Demani (MMR: 3503)
# Team 5: Zal, Syndicate (MMR: 3361)
# Team 6: Ayaka, Cyan (MMR: 3268)

# Table: !scoreboard 6 Euan, babycartel, ShadowMK, Trae, Splinkle, Warp Star, gomigomi, Demani, Zal, Syndicate, Ayaka, Cyan









# Submits table to specific tier or w/e. this bot sucks cynda
# this is the order that u get from the previous command tutorial above
# ---
# !submit 3 d
# miarun 58
# usagi 89
# Jeanne 107
# ANIMALSASLEADERS 75
# ta_go 65
# FULLPOWER 72
# kerokke 98
# Takagisan 96
# tracks 90
# dasu_go 81
# Slowbro 64
# megane 89

import DBA
import secrets
import discord
from discord.ext import commands
import vlog_msg
import math
import threading
import re
import datetime
import time
import json
import requests
import asyncio
import random
import concurrent.futures
from bs4 import BeautifulSoup as Soup
from waiting import wait

Lounge = [461383953937596416]
lounge_id = 999835318104625252
ml_channel_message_id = 1000138727621918872
ml_lu_channel_message_id = 1000138727697424415
MOGILIST = {}
TIER_ID_LIST = []
intents = discord.Intents(messages=True, guilds=True, message_content=True)
client = discord.Bot(intents=intents, activity=discord.Game(str('200cc Lounge')))

with DBA.DBAccess() as db:
    get_tier_list = db.query('SELECT tier_id FROM tier WHERE tier_id > %s;', (0,))
    for i in range(len(get_tier_list)):
        TIER_ID_LIST.append(get_tier_list[i][0])
    print(TIER_ID_LIST)


def update_mogilist():
    with DBA.DBAccess() as db:
        temp = db.query('SELECT t.tier_name, p.player_name FROM tier t INNER JOIN lineups l ON t.tier_id = l.tier_id INNER JOIN player p ON l.player_id = p.player_id WHERE p.player_id > %s;', (1,))
    for i in range(len(temp)):
        if temp[i][0] in MOGILIST:
            MOGILIST[temp[i][0]].append(temp[i][1])
        else:
            MOGILIST[temp[i][0]]=[temp[i][1]]

    # TODO: actually get the right data, format it, and put it in the ml and mllu channels. good enough for now tho

    ml = client.get_channel(secrets.mogilist_channel)
    # returns a Future object. need to get the .result() of the Future (which is the Discord.message object)
    ml_message = asyncio.run_coroutine_threadsafe(ml.fetch_message(ml_channel_message_id), client.loop)
    asyncio.run_coroutine_threadsafe(ml_message.result().edit(content=f'new temp: {str(len(temp))}'), client.loop)


    mllu = client.get_channel(secrets.mogilist_lu_channel)
    mllu_message = asyncio.run_coroutine_threadsafe(mllu.fetch_message(ml_lu_channel_message_id), client.loop)
    asyncio.run_coroutine_threadsafe(mllu_message.result().edit(content=f'new temp: {temp}'), client.loop)

    
    # Create a dictionary
    # tier_name : [player_names]


def lounge_threads():
    time.sleep(10)
    while(True):
        update_mogilist()
        time.sleep(15)


poll_thread = threading.Thread(target=lounge_threads)
poll_thread.start()








@client.event
async def on_application_command_error(ctx, error):
    if ctx.guild == None:
        channel = client.get_channel(secrets.debug_channel)
        embed = discord.Embed(title='Error', description='ctx.guild = None. This message was sent in a DM...?', color = discord.Color.blurple())
        embed.add_field(name='Name: ', value=ctx.author, inline=False)
        embed.add_field(name='Error: ', value=str(error), inline=False)
        embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
        await channel.send(content=None, embed=embed)
        await ctx.respond('Sorry! My commands do not work in DMs. Please use 200cc Lounge :)')
        return
    else:
        channel = client.get_channel(secrets.debug_channel)
        embed = discord.Embed(title='Error', description=':eyes:', color = discord.Color.blurple())
        embed.add_field(name='Name: ', value=ctx.author, inline=False)
        embed.add_field(name='Error: ', value=str(error), inline=False)
        embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
        await channel.send(content=None, embed=embed)
        await ctx.respond(f'Sorry! An unknown error occurred. Contact {secrets.my_discord} if you think this is a mistake.')
        return

@client.event
async def on_message(ctx):
    if ctx.author.id == lounge_id:
        return
    if ctx.channel.id in TIER_ID_LIST:
        with DBA.DBAccess() as db:
            get_tier = db.query('SELECT voting, tier_id FROM tier WHERE tier_id = %s;', (ctx.channel.id,))
        if get_tier[0][0]:
            if get_tier[0][1] == ctx.channel.id:
                if str(ctx.content) in ['1', '2', '3', '4', '6']:
                    print('its in there lol')
                    try:
                        with DBA.DBAccess() as db:
                            temp = db.query('SELECT player_id FROM lineups WHERE player_id = %s AND tier_id = %s;', (ctx.author.id, ctx.channel.id))
                    except Exception as e:
                        await send_to_debug_channel(ctx, e)
                        return
                    try:
                        with DBA.DBAccess() as db:
                            db.execute('UPDATE lineups SET vote = %s WHERE player_id = %s;', (int(ctx.content), ctx.author.id))
                    except Exception as e:
                        await send_to_debug_channel(ctx, e)
                        return
    # get discord id and channel id
    # if user and channel id in lineups
    message = ctx.content
    print(message)






# Can up - keep track of who is in lineup

# /verify <link>
@client.slash_command(
    name='verify',
    description='Verify your MKC account',
    guild_ids=Lounge
)
async def verify(
    ctx, 
    message: discord.Option(str, 'MKC Link', required=True
    )):
    await ctx.defer(ephemeral=True)
    x = await check_if_player_exists(ctx)
    if x:
        await ctx.respond(f'``Error 1:`` {str(ctx.author.display_name)} is already verified.')
        return
    else:
        pass
    # Regex on https://www.mariokartcentral.com/mkc/registry/players/930
    if 'registry' in message:
        regex_pattern = 'players/\d*'
        if re.search(regex_pattern, str(message)):
            regex_group = re.search(regex_pattern, message)
            x = regex_group.group()
            #print('registry link: regex found: ' + str(x))
            reg_array = re.split('/', x)
            mkc_player_id = reg_array[1]
            #print('mkc player_id :' + str(mkc_player_id))
        else:
            await ctx.respond('``Error 2:`` Oops! Something went wrong. Check your link or try again later')
            return
    # Regex on https://www.mariokartcentral.com/forums/index.php?members/popuko.154/
    elif 'forums' in message:
        regex_pattern = 'members/.*\.\d*'
        if re.search(regex_pattern, str(message)):
            regex_group = re.search(regex_pattern, message)
            x = regex_group.group()
            temp = re.split('\.|/', x)
            mkc_user_id = temp[2]
        else:
            # player doesnt exist on forums
            await ctx.respond('``Error 3:`` Oops! Something went wrong. Check your link or try again later')
            return

        # MKC registry api
        mkc_player_id = await mkc_request_mkc_player_id(mkc_user_id)
        if mkc_player_id != -1:
            pass
        else:
            await ctx.respond('``Error 4:`` Oops! Something went wrong. Check your link or try again later')
            return
    else:
        await ctx.respond('``Error 5:`` Oops! Something went wrong. Check your link or try again later')
        return

    # MKC indiv api on 930 (player_id)
    is_banned = await mkc_request_registry_info(mkc_player_id, 'is_banned')
    if is_banned == -1:
        await ctx.respond('``Error 6:`` Oops! Something went wrong. Check your link or try again later')
        return
    elif is_banned:
        await ctx.respond('``Error 7:`` Oops! Something went wrong. Check your link or try again later')
        return
    else:
        pass

    # Check if user verifying and user in mkc database is the same user
    discord_tag = await mkc_request_registry_info(mkc_player_id, 'discord_tag')
    if str(discord_tag) == str(ctx.author):
        pass
    else:
        await ctx.respond('``Error 8:`` Account is not associated. Check your privacy settings on mariokartcentral.com')
        verify_description = vlog_msg.error2
        verify_color = discord.Color.red()
        await send_to_verification_log(ctx, message, verify_color, verify_description)
        return

    if is_banned:
        verify_description = vlog_msg.error3
        verify_color = discord.Color.red()
        await ctx.respond('``Error 9:`` Oops! Something went wrong. Check your link or try again later')
        await send_to_verification_log(ctx, message, verify_color, verify_description)
        return
    else:
        verify_description = vlog_msg.success
        verify_color = discord.Color.green()
        x = await check_if_mkc_player_id_used(mkc_player_id)
        if x:
            await ctx.respond(f'``Error 10: Duplicate player`` If you think this is a mistake, please contact {secrets.my_discord} immediately. ')
            verify_description = vlog_msg.error4
            verify_color = discord.Color.red()
            await send_to_verification_log(ctx, message, verify_color, verify_description)
            return
        else:
            x = await create_player(ctx)
            await ctx.respond(x)


@client.slash_command(
    name='c',
    description='🙋 Can up for a mogi',
    guild_ids=Lounge
)
@commands.cooldown(1, 15, commands.BucketType.user)
async def c(
    ctx,
    ):
    await ctx.defer(ephemeral=True)
    x = await check_if_uid_in_tier(ctx.author.id)
    if x:
        await ctx.respond('``Error 11:`` You are already in a mogi. Use /d to drop before canning up again.')
        return
    else:
        pass
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT COUNT(player_id) FROM lineups WHERE tier_id = %s;', (ctx.channel.id,))
            count = temp[0][0]
    except Exception as e:
        await ctx.respond(f'``Error 18:`` Something went VERY wrong! Please contact {secrets.my_discord}. {e}')
        await send_to_debug_channel(ctx, e)
        return
    if count == 12:
        await ctx.respond('Mogi is full')
        return
    try:
        with DBA.DBAccess() as db:
            db.execute('INSERT INTO lineups (player_id, tier_id) values (%s, %s);', (ctx.author.id, ctx.channel.id))
            await ctx.respond('You have joined the mogi! You can /d in `15 seconds`')
            channel = client.get_channel(ctx.channel.id)
            await channel.send(f'<@{ctx.author.id}> has joined the mogi!')
            count+=1
    except Exception as e:
        await ctx.respond(f'``Error 16:`` Something went wrong! Contact {secrets.my_discord}. {e}')
        await send_to_debug_channel(ctx, e)
        return
    if count >= 2:
        print('count >=2')
        mogi_format = await start_format_vote(ctx)
        await start_mogi(ctx)



        # start the mogi, vote on format, create teams
    return

@client.slash_command(
    name='d',
    description='Drop from the mogi',
    guild_ids=Lounge
)
async def d(
    ctx,
    ):
    await ctx.defer(ephemeral=True)
    x = await check_if_uid_in_tier(ctx.author.id)
    if x:
        # No try block - check is above...
        with DBA.DBAccess() as db:
            tier_temp = db.query('SELECT t.tier_id, t.tier_name FROM tier as t JOIN lineups as l ON t.tier_id = l.tier_id WHERE player_id = %s;', (ctx.author.id,))
        try:
            with DBA.DBAccess() as db:
                db.execute('DELETE FROM lineups WHERE player_id = %s;', (ctx.author.id,))
                await ctx.respond(f'You have dropped from tier {tier_temp[0][1]}')
        except Exception as e:
            await send_to_debug_channel(ctx, e)
            await ctx.respond(f'``Error 17:`` Oops! Something went wrong. Contact {secrets.my_discord}')
            return
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT player_name FROM player WHERE player_id = %s;', (ctx.author.id,))
                channel = client.get_channel(tier_temp[0][0])
                await channel.send(f'{temp[0][0]} has dropped from the lineup')
        except Exception as e:
            await send_to_debug_channel(ctx, f'WHAT! 1 {e}')
            # i should never ever see this...
        return
    else:
        await ctx.respond('You are not in a mogi')
        return

@client.slash_command(
    name='l',
    description='Show the mogi lineup',
    guild_ids=Lounge
)
# @commands.command(aliases=['list'])
@commands.cooldown(1, 30, commands.BucketType.user)
async def l(
    ctx
    ):
    await ctx.defer()
    try:
        with DBA.DBAccess() as db:
            temp = db.query("SELECT p.player_name FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s ORDER BY l.create_date ASC;", (ctx.channel.id,))
    except Exception as e:
        await ctx.respond(f'``Error 20:`` Oops! Something went wrong. Please contact {secrets.my_discord}')
        return
    response = '`Mogi List`:'
    for i in range(len(temp)):
        response = f'{response}\n`{i+1}.` {temp[i][0]}'
    response = f'{response}\n\n\nYou can type `/l` again in 30 seconds'
    await ctx.respond(response, delete_after=30)
    return


@client.slash_command(
    name='sub',
    description='Sub out a player',
    guild_ids=Lounge
)
async def sub(
    ctx,
    leaving_player: discord.Option(discord.Member, 'Leaving player', required=True),
    subbing_player: discord.Option(discord.Member, 'Subbing player', required=True)
    ):
    await ctx.defer()
    x = await check_if_mogi_is_ongoing(ctx)
    if x:
        pass
    else:
        await ctx.respond('Mogi has not started')
        return
    # Only players in the mogi can sub out others
    y = await check_if_uid_in_tier(ctx.author.id)
    if y:
        pass
    else:
        await ctx.respond('You are not in the mogi. You cannot sub out another player')
        return
    z = await check_if_uid_in_tier(leaving_player.id)
    if z:
        pass
    else:
        await ctx.respond(f'<@{leaving_player.id}> is not in this mogi.')
        return
    try:
        with DBA.DBAccess() as db:
            db.execute('UPDATE lineups SET player_id = %s WHERE player_id = %s;', (subbing_player.id, leaving_player.id))
    except Exception as e:
        await ctx.respond(f'``Error 19:`` Oops! Something went wrong. Please contact {secrets.my_discord}')
        await send_to_debug_channel(ctx, e)
        return
    await ctx.respond(f'<@{leaving_player.id}> has been subbed out for <@{subbing_player.id}>')
    await send_to_sub_log(ctx, f'<@{leaving_player.id}> has been subbed out for <@{subbing_player.id}>')
    return



# /setfc
@client.slash_command(
    name='fc',
    description='Display or set your friend code',
    guild_ids=Lounge
)
async def fc(
    ctx,
    fc: discord.Option(str, 'XXXX-XXXX-XXXX', required=False)):
    if fc == None:
        await ctx.defer(ephemeral=True)
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT fc FROM player WHERE player_id = %s;', (ctx.author.id, ))
                await ctx.respond(temp[0][0])
        except Exception as e:
            await ctx.respond('``Error 12:`` No friend code found. Use ``/fc XXXX-XXXX-XXXX`` to set.')
            await send_to_debug_channel(ctx, e)
    else:
        await ctx.defer(ephemeral=True)
        y = await check_if_banned_characters(fc)
        if y:
            await send_to_verification_log(ctx, fc, discord.Color.blurple(), vlog_msg.error1)
            return '``Error 13:`` Invalid fc. Use ``/fc XXXX-XXXX-XXXX``'
        x = await check_if_player_exists(ctx)
        if x:
            pass
        else:
            await create_player(ctx)
        confirmation_msg = await update_friend_code(ctx, fc)
        await ctx.respond(confirmation_msg)

























async def create_player(ctx):
    x = await check_if_player_exists(ctx)
    if x:
        return 'Player already registered'
    else:
        mkc_player_id = int(await mkc_request_mkc_player_id(int(await lounge_request_mkc_user_id(ctx))))
        if mkc_player_id != -1:
            with DBA.DBAccess() as db:
                # TODO: 
                # REWRITE TO GATHER MORE DATA AND MATCH NEW DATABASE
                db.execute('INSERT INTO player (player_id, player_name, mkc_id) VALUES (%s, %s, %s);', (ctx.author.id, ctx.author.display_name, mkc_player_id))
                return 'Verified & registered successfully'
        else:
            return f'``Error 14:`` Contact {secrets.my_discord} if you think this is a mistake.'
            # 1. a player trying to use someone elses link (could be banned player)
            # 2. a genuine player locked from usage by another player (banned player might have locked them out)
            # 3. someone is verifying multiple times

async def update_friend_code(ctx, message):
    fc_pattern = '\d\d\d\d-?\d\d\d\d-?\d\d\d\d'
    if re.search(fc_pattern, message):
        try:
            with DBA.DBAccess() as db:
                db.execute('UPDATE player SET friend_code = %s WHERE player_id = %s;', (message, ctx.author.id))
                return 'Friend Code updated'
        except Exception as e:
            await send_to_debug_channel(ctx, e)
            return '``Error 15:`` Player not found'
    else:
        return 'Invalid fc. Use ``/fc XXXX-XXXX-XXXX``'

async def start_format_vote(ctx):
    try:
        with DBA.DBAccess() as db:
            db.execute('UPDATE tier SET voting = 1 WHERE tier_id = %s;', (ctx.channel.id,))
    except Exception as e:
        await send_to_debug_channel(ctx, e)
        await channel.send(f'`Error 23:` Could not start the format vote. Contact the admins or {secrets.my_discord} immediately')
        return 0

    # TIER VOTING BOOLEAN LOL ------------------------------------------------------------


    channel = client.get_channel(ctx.channel.id)
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT p.player_name FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s ORDER BY l.create_date ASC;', (ctx.channel.id,))
    except Exception as e:
        await send_to_debug_channel(ctx, e)
        await channel.send(f'`Error 22:` Could not start the format vote. Contact the admins or {secrets.my_discord} immediately')
        return 0
    response = ''
    for i in range(len(temp)):
        response = f'{response} <@{temp[i][0]}> '
    response = f'''{response} mogi has 12 players
`Poll Started!`

`1.` FFA
`2.` 2v2
`3.` 3v3
`4.` 4v4
`6.` 6v6

Type a number to vote!
Poll ends in 2 minutes or when a format reaches 6 votes.'''
    await channel.send(response)
    with DBA.DBAccess() as db:
        unix_temp = db.query('SELECT UNIX_TIMESTAMP(create_date) FROM lineups WHERE tier_id = %s ORDER BY create_date DESC LIMIT 1;', (ctx.channel.id,))
    # returns the index of the voted on format, and the list [ffa, 2v2, 3v3, 4v4, 6v6]
    poll_results = await check_for_poll_results(ctx, unix_temp[0][0])
    await channel.send(poll_results[1])
    poll_results_response = '''


'''
    teams_response = await create_teams(ctx, poll_results[0])
    await channel.send(teams_response)

    


async def create_teams(ctx, poll_results):
    with DBA.DBAccess() as db:
        players_db = db.query('SELECT p.player_name FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s ORDER BY l.create_date ASC LIMIT 12;', (ctx.channel.id,))
    players_list = []
    for i in range(len(player_db)):
        players_list.append(player_db[i][0])
    random.shuffle(players_list)


    
# Poll Ended!

# 1. FFA - 3 (Splinkle, Tatsuya, IhavePants)
# 2. 2v2 - 6 (Ai Xiang, Deshawn Co. III, ObesoYoshiraMK, Helfire Club, naive, iiRxl)
# 3. 3v3 - 0
# 4. 4v4 - 0
# 6. 6v6 - 0
# Winner: 2v2

# Room MMR: 7213
# Team 1: Deshawn Co. III, iiRxl (MMR: 9846)
# Team 2: naive, Ty (MMR: 7728)
# Team 3: Tatsuya, ObesoYoshiraMK (MMR: 7033)
# Team 4: Splinkle, Maxarx (MMR: 6378)
# Team 5: IhavePants, Ai Xiang (MMR: 6318)
# Team 6: Helfire Club, Nino (MMR: 4734)

# Table: !scoreboard 6 Deshawn Co. III, iiRxl, naive, Ty, Tatsuya, ObesoYoshiraMK, Splinkle, Maxarx, IhavePants, Ai Xiang, Helfire Club, Nino



# Somebody did a bad
# ctx | message | discord.Color.red() | my custom message
async def send_to_verification_log(ctx, message, verify_color, verify_description):
    channel = client.get_channel(secrets.verification_channel)
    embed = discord.Embed(title='Verification', description=verify_description, color = verify_color)
    embed.add_field(name='Name: ', value=ctx.author, inline=False)
    embed.add_field(name='Message: ', value=message, inline=False)
    embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
    await channel.send(content=None, embed=embed)

async def send_to_debug_channel(ctx, error):
    channel = client.get_channel(secrets.debug_channel)
    embed = discord.Embed(title='Error', description='>.<', color = discord.Color.blurple())
    embed.add_field(name='Name: ', value=ctx.author, inline=False)
    embed.add_field(name='Error: ', value=str(error), inline=False)
    embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
    await channel.send(content=None, embed=embed)

async def send_to_sub_log(ctx, message):
    channel = client.get_channel(secrets.sub_channel)
    embed = discord.Embed(title='Sub', description=':3', color = discord.Color.blurple())
    embed.add_field(name='Name: ', value=ctx.author, inline=False)
    embed.add_field(name='Message: ', value=str(message), inline=False)
    embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
    await channel.send(content=None, embed=embed)










async def check_for_poll_results(ctx, last_joiner_unix_timestamp):
    dtobject_now = datetime.datetime.now()
    unix_now = time.mktime(dtobject_now.timetuple())
    format_list = [0,0,0,0,0]
    while (unix_now - last_joiner_unix_timestamp) < 20:
        await asyncio.sleep(1)
        with DBA.DBAccess() as db:
            ffa_temp = db.query('SELECT COUNT(vote) FROM lineups WHERE tier_id = %s AND vote = %s;', (ctx.channel.id,1))
            format_list[0] = ffa_temp[0][0]
        with DBA.DBAccess() as db:
            v2_temp = db.query('SELECT COUNT(vote) FROM lineups WHERE tier_id = %s AND vote = %s;', (ctx.channel.id,2))
            format_list[1] = v2_temp[0][0]
        with DBA.DBAccess() as db:
            v3_temp = db.query('SELECT COUNT(vote) FROM lineups WHERE tier_id = %s AND vote = %s;', (ctx.channel.id,3))
            format_list[2] = v3_temp[0][0]
        with DBA.DBAccess() as db:
            v4_temp = db.query('SELECT COUNT(vote) FROM lineups WHERE tier_id = %s AND vote = %s;', (ctx.channel.id,4))
            format_list[3] = v4_temp[0][0]
        with DBA.DBAccess() as db:
            v6_temp = db.query('SELECT COUNT(vote) FROM lineups WHERE tier_id = %s AND vote = %s;', (ctx.channel.id,6))
            format_list[4] = v6_temp[0][0]
        if 6 in format_list:
            break
        print(f'{unix_now} - {last_joiner_unix_timestamp}')
        dtobject_now = datetime.datetime.now()
        unix_now = time.mktime(dtobject_now.timetuple())
    with DBA.DBAccess() as db:
        db.execute('UPDATE tier SET voting = 0 WHERE tier_id = %s;', (ctx.channel.id,))
    with DBA.DBAccess() as db:
        db.execute('UPDATE lineups SET vote = NULL WHERE tier_id = %s;', (ctx.channel.id,))
    if format_list[0] == 6:
        return 1
    elif format_list[1] == 6:
        return 2
    elif format_list[2] == 6:
        return 3
    elif format_list[3] == 6:
        return 4
    elif format_list[4] == 6:
        return 6
    else:
        # Get the index of the voted on format
        max_val = max(format_list)
        ind = [i for i, v in enumerate(format_list) if v == max_val]

        # Create a dictionary where key=format, value=list of players who voted
        poll_dictionary = {}
        with DBA.DBAccess() as db:
            votes_temp = db.query('SELECT l.vote, p.player_name FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s ORDER BY l.create_date ASC LIMIT 12;', (ctx.channel.id,))
        for i in range(len(votes_temp)):
            if temp[i][0] in poll_dictionary:
                poll_dictionary[votes_temp[i][0]].append(votes_temp[i][1])
            else:
                if votes_temp[i][0] == 1:
                    poll_dictionary['FFA']=[votes_temp[i][1]]
                elif votes_temp[i][0] == 2:
                    poll_dictionary['2v2']=[votes_temp[i][1]]
                elif votes_temp[i][0] == 3:
                    poll_dictionary['3v3']=[votes_temp[i][1]]
                elif votes_temp[i][0] == 4:
                    poll_dictionary['4v4']=[votes_temp[i][1]]
                elif votes_temp[i][0] == 6:
                    poll_dictionary['6v6']=[votes_temp[i][1]]
                else:
                    pass
        return [random.choice(ind), poll_dictionary]

async def check_if_mogi_is_ongoing(ctx):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT COUNT(player_id) FROM lineups WHERE tier_id = %s;', (ctx.channel.id,))
    except Exception:
        return False
    if temp[0][0] == 12:
        return True
    else:
        return False

async def check_if_uid_in_tier(uid):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_id FROM lineups WHERE player_id = %s;', (uid,))
            if temp[0][0] == uid:
                return True
            else:
                return False
    except Exception:
        return False

async def check_if_mkc_player_id_used(mkc_player_id):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT mkc_player_id from player WHERE mkc_player_id = %s;', (mkc_player_id,))
            if int(temp[0][0]) == int(mkc_player_id):
                return True
            else:
                return False
    except Exception as e:
        await send_to_debug_channel(ctx, e)
        return False

async def check_if_player_exists(ctx):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_id FROM player WHERE player_id = %s;', (ctx.author.id, ))
            if temp[0][0] == ctx.author.id:
                return True
            else:
                return False
    except Exception as e:
        await send_to_debug_channel(ctx, e)
        return False

async def check_if_banned_characters(message):
    for value in secrets.BANNED_CHARACTERS:
        if value in message:
            return True
    return False





async def mkc_request_mkc_player_id(mkc_user_id):
    # MKC Registry API
    #print('mkc user id: aaaaaaaa')
    #print(mkc_user_id)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(mt_mkc_request_mkc_player_id, mkc_user_id)
        return_value = future.result()
    return return_value

async def mkc_request_registry_info(mkc_player_id, field_name):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(mt_mkc_request_registry_info, mkc_player_id, field_name)
        return_value = future.result()
    return return_value

# Takes ctx and Discord ID, returns mkc_user_id
async def lounge_request_mkc_user_id(ctx):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(mt_lounge_request_mkc_user_id, ctx)
        return_value = future.result()
    return return_value




client.run(secrets.token)
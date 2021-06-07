import sqlite3
import vacefron
import discord
from discord.ext import commands

vac_api = vacefron.Client()



class Levelling(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def set(self, ctx):
        # Set commands
        await ctx.send("USE `set xp` or `set level`")

    # Set xp for a user
    @set.command()
    @commands.is_owner()
    async def xp(self, ctx, member: discord.Member=None, *, amount=None):
        if member is None:
            await ctx.send("You need to mention them")
        if amount is None:
            await ctx.send("You need to put a amount")
        db = sqlite3.connect("./db/leveling.db")
        cursor = db.cursor()
        cursor.execute(f"SELECT userid FROM users WHERE guildid = '{ctx.guild.id}'")
        result = cursor.fetchone()
        if result is None:
            sql = ("INSERT INTO users(guildid, userid, level, xp, level_up_xp, rank_image_url) VALUES(?, ?, ?, ?, ?, ?)")
            val = (str(ctx.guild.id), str(ctx.author.id), 1, amount, 100, "https://media.discordapp.net/attachments/818899477372600434/848947456334495794/Leveling_System_Background_3.jpg")
            cursor.execute(sql, val)
            db.commit()
        sql = ("UPDATE users SET xp = ? WHERE guildid = ? and userid = ?")
        val = (amount, str(ctx.guild.id), str(member.id))
        cursor.execute(sql, val)
        db.commit()
        await ctx.send("Done")

    # Set level for a user
    @set.command()
    @commands.is_owner()
    async def level(self, ctx, member: discord.Member=None, *, amount=None):
        if member is None:
            await ctx.send("You need to mention them")
        if amount is None:
            await ctx.send("You need to put a amount")
        db = sqlite3.connect("./db/leveling.db")
        cursor = db.cursor()
        cursor.execute(f"SELECT userid FROM users WHERE guildid = '{ctx.guild.id}'")
        result = cursor.fetchone()
        if result is None:
            sql = ("INSERT INTO users(guildid, userid, level, xp, level_up_xp, rank_image_url) VALUES(?, ?, ?, ?, ?, ?)")
            val = (str(ctx.guild.id), str(ctx.author.id), amount, 10, 100, "https://media.discordapp.net/attachments/818899477372600434/848947456334495794/Leveling_System_Background_3.jpg")
            cursor.execute(sql, val)
            db.commit()
            return
        sql = ("UPDATE users SET level = ? WHERE guildid = ? and userid = ?")
        val = (amount, str(ctx.guild.id), str(member.id))
        cursor.execute(sql, val)
        db.commit()
        await ctx.send("Done")
    

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = sqlite3.connect("./db/leveling.db")
        cursor = db.cursor()
        sql = ("INSERT INTO users(guildid, userid, level, xp, level_up_xp, rank_image_url) VALUES(?, ?, ?, ?, ?, ?)")
        val = (str(member.guild.id), str(member.id), 1, 0, 100, "https://media.discordapp.net/attachments/818899477372600434/848947456334495794/Leveling_System_Background_3.jpg")
        cursor.execute(sql, val)
        db.commit()


    @commands.Cog.listener()
    async def on_member_leave(self, member):
        db = sqlite3.connect("./db/leveling.db")
        cursor = db.cursor()
        cursor.execute(f"DELETE FROM users WHERE userid = {member.id}")
        db.commit()



    @commands.Cog.listener()
    async def on_message(self, message):
        # If bot is sending the message
        if message.author.bot:
            return
        
        # DB info
        db = sqlite3.connect("./db/leveling.db")
        cursor = db.cursor()

        # Getting info from the user
        cursor.execute(f"SELECT userid FROM users WHERE guildid = '{message.guild.id}'")

        # Fetch one result
        result = cursor.fetchone()

        # If the db can't find anything
        if result is None:
            # Insert the user
            sql = ("INSERT INTO users(guildid, userid, level, xp, level_up_xp, rank_image_url) VALUES(?, ?, ?, ?, ?, ?)")
            val = (str(message.guild.id), str(message.author.id), 1, 10, 100, "https://media.discordapp.net/attachments/818899477372600434/848947456334495794/Leveling_System_Background_3.jpg")
            cursor.execute(sql, val)

            # Commit to the db
            db.commit()

        # If the db found something
        else:
            # Getting the user info again
            cursor.execute(f"SELECT userid, xp, level, level_up_xp FROM users WHERE guildid = '{message.guild.id}' and userid = '{message.author.id}'")

            # Fetch the user info once
            result1 = cursor.fetchone()
            # xp variable
            exp = result1[1]

            # Updating db
            sql = ("UPDATE users SET xp = ? WHERE guildid = ? and userid = ?")
            val = (int(exp + 10), str(message.guild.id), str(message.author.id))
            cursor.execute(sql, val)

            # Commit to db
            db.commit()

            # More info
            xp = int(result1[1])
            exp_until_lvl_up = int(result1[3])
            lvl = int(result1[2])
            lvl_up = lvl + int(1)
            next_exp_until_lvl_up = exp_until_lvl_up + int(100)

            # If the user reaches the amount to level up
            if xp == exp_until_lvl_up or xp > exp_until_lvl_up:
                # Send the message to notify the user
                await message.channel.send(f"GG {message.author.mention} level up to {lvl_up}")

                # Updating db
                sql = ("UPDATE users SET xp = ?, level = ?, level_up_xp = ? WHERE guildid = ? and userid = ?")
                val = (0, int(lvl_up), int(next_exp_until_lvl_up),str(message.guild.id), str(message.author.id))
                cursor.execute(sql, val)
                db.commit()


    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rank(self, ctx, member: discord.Member=None):
        if member is None:
            member = ctx.author

        # DB info
        db = sqlite3.connect("./db/leveling.db")
        cursor = db.cursor()

        # Get everything except guildid
        cursor.execute(f"SELECT userid, level, xp, level_up_xp, rank_image_url FROM users WHERE guildid = '{ctx.guild.id}' AND userid = '{member.id}'")

        # Get a/one result
        result = cursor.fetchone()

        # If then user is not in db
        if result is None:
            sql = ("INSERT INTO users(guildid, userid, level, xp, level_up_xp, rank_image_url) VALUES(?, ?, ?, ?, ?, ?)")
            val = (str(ctx.guild.id), str(member.id), 1, 10, 100, "https://media.discordapp.net/attachments/818899477372600434/848947456334495794/Leveling_System_Background_3.jpg")
            cursor.execute(sql, val)
            db.commit()
            return

        # If they are in db
        # Info
        xp = str(result[2])
        level_up_xp = result[3]

        # Rank in leaderboard
        rank = 1

        # Find what rank the user is at
        for value in cursor:
            if xp < value[0]:
                rank += 1

        # More info
        exp = int(result[2])
        level = int(result[1])
        lvl_up_xp = int(result[3])

        # Boxes for progress bar
        boxes = int((exp/(200*((1/2) * level)))*20)

        # The percentage progress
        percentage_progress = (100/lvl_up_xp * exp)
        try:
            level_up_xp = int(result[3])
            gen_card = await vac_api.rank_card(
            username = f"{member.name}#{member.discriminator}",
            avatar = member.avatar_url_as(format = "png"), 
            level = int(level), 
            rank = rank, 
            current_xp = exp,
            next_level_xp = level_up_xp,
            previous_level_xp = 0,
            custom_background = f"{result[4]}", 
            xp_color = "3399CC",
            is_boosting = bool(member.premium_since), 
            circle_avatar = True  
            )
            rank_image = discord.File(fp = await gen_card.read(), filename = f"{member.name}_rank.png")
            await ctx.send(file = rank_image)
        except:
            # The embed
            embed = discord.Embed(title=f"{member.name}'s Rank", color=discord.Color.blue()) # The user's name
            embed.add_field(name="Level:", value=level) # The users's level
            embed.add_field(name="XP:", value=f"{exp}/{level_up_xp}") # The user's xp
            embed.add_field(name="Rank:", value=f"{rank}/{ctx.guild.member_count}") # The user's rank
            embed.add_field(name=f"Progress Bar {percentage_progress}%:", value=boxes * "🟦" + (20-boxes) * "⬜", inline=False) # The user's percentage progress&progress bar
            embed.set_thumbnail(url=member.avatar_url) # Show the user's image
            await ctx.send(embed=embed) # Send the embed




        



    @commands.command(aliases=['xplb'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def xpleaderboard(self, ctx, *, all_time=None):
        if all_time is None:
            # DB info
            db = sqlite3.connect('db/leveling.db')
            cursor = db.cursor()

            # Ordering - Limit is 10
            cursor.execute(f"SELECT userid, level, xp from users WHERE guildid = '{ctx.guild.id}' ORDER BY level + 0 DESC, xp + 0 DESC LIMIT 10")

            # Fectch all result
            end = cursor.fetchall()

            # Embed
            embed = discord.Embed(title=f"{ctx.guild.name}'s Leaderboard: Top 10", description=f"All time in this guild: {ctx.guild.name}", color=discord.Color.green())
            for i, x in enumerate(end, 1): # End is the ending number and 1 is the start number. This is a loop
                embed.add_field(name=f"#{i}", value=f"Name: <@{x[0]}>\n Level: {x[1]}\n XP: {x[2]}", inline=False) # I is number so like #1 and the others are labled

            # Sending the embed
            await ctx.send(embed=embed)
            return
        if all_time == "True" or 'true':
            # DB info
            db = sqlite3.connect('db/leveling.db')
            cursor = db.cursor()

            # Ordering - Limit is 10
            cursor.execute(f"SELECT userid, level, xp from users ORDER BY level + 0 DESC, xp + 0 DESC LIMIT 10")

            # Fectch all result
            end = cursor.fetchall()

            # Embed
            embed = discord.Embed(title=f"All Time Leaderboard: Top 10", description="All time in every guild", color=discord.Color.green())
            for i, x in enumerate(end, 1): # End is the ending number and 1 is the start number. This is a loop
                embed.add_field(name=f"#{i}", value=f"Name: <@{x[0]}>\n Level: {x[1]}\n XP: {x[2]}", inline=False) # I is number so like #1 and the others are labled

            # Sending the embed
            await ctx.send(embed=embed)
            return

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def image(self, ctx, url):
        # DB info
        db = sqlite3.connect('db/leveling.db')
        cursor = db.cursor()

        cursor.execute(f"SELECT rank_image_url FROM users WHERE guildid = '{ctx.guild.id}' AND userid = '{ctx.author.id}'")
        result = cursor.fetchone()
        if result is None:
            sql = ("INSERT INTO users(guildid, userid, level, xp, level_up_xp, rank_image_url) VALUES(?, ?, ?, ?, ?, ?)")
            val = (str(ctx.guild.id), str(ctx.author.id), 1, 10, 100, "https://media.discordapp.net/attachments/818899477372600434/848947456334495794/Leveling_System_Background_3.jpg")
            cursor.execute(sql, val)
            db.commit()
        sql = ("UPDATE users SET rank_image_url = ? WHERE guildid = ? and userid = ?")
        val = (str(url), str(ctx.guild.id), str(ctx.author.id))
        cursor.execute(sql, val)
        db.commit()
        await ctx.send(f"Image has been set to {url}")
    

def setup(client):
    client.add_cog(Levelling(client))
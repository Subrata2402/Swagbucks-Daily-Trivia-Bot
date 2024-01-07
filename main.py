import asyncio, os
import config, db, discord
from discord.ext import commands
from swagbucks import Swagbucks
from sb_daily_trivia import DailyTrivia

class MainClass(commands.Cog, Swagbucks):

	def __init__(self, client: commands.Bot):
		self.client = client

	@commands.command(name = "add", description = "Add a Swagbucks account to the database.")
	@commands.is_owner()
	async def add(self, ctx: commands.Context, access_token: str = None, token: str = None, sig: str = None):
		"""
		Add a Swagbucks account to the database.
		:param ctx: The context of the command.
		:param access_token: The access token to authenticate.
		:param token: The token to authenticate.
		:return: None.
		"""
		if ctx.guild:
			return await ctx.send(content = "This command can only be used in DMs.")
		if not access_token:
			msg = await ctx.send(content = "Enter the access token of the account (within 60 seconds) :")
			try:
				message = await self.client.wait_for("message", check = lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout = 60)
				access_token = message.content.strip()
				success = await self.is_expired(access_token)
				if not success:
					return await ctx.send(content = "The access token you entered is invalid or expired.")
			except asyncio.TimeoutError:
				return await msg.edit(content = "You failed to enter the access token in time.")
		if not token:
			msg = await ctx.send(content = "Enter the token of the account (within 60 seconds) :")
			try:
				message = await self.client.wait_for("message", check = lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout = 60)
				token = message.content.strip()
			except asyncio.TimeoutError:
				return await msg.edit(content = "You failed to enter the token in time.")
		if not sig:
			msg = await ctx.send(content = "Enter the signature of the account (within 60 seconds) :")
			try:
				message = await self.client.wait_for("message", check = lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout = 60)
				sig = message.content.strip()
			except asyncio.TimeoutError:
				return await msg.edit(content = "You failed to enter the signature in time.")
		await self.add_account(ctx, access_token, token, sig)

	@commands.command(name = "update", description = "Update a Swagbucks account.")
	@commands.is_owner()
	async def update(self, ctx: commands.Context, username: str):
		"""
		Update a Swagbucks account.
		:param ctx: The context of the command.
		:param username: The username to find details of a user.
		:return: None.
		"""
		try:
			await ctx.message.delete()
		except:
			pass
		await self.update_account(ctx, username)

	# @commands.command(name = "delete", description = "Delete a Swagbucks account from the database.")
	async def delete(self, ctx: commands.Context, username: str):
		"""
		Delete a Swagbucks account from the database.
		:param ctx: The context of the command.
		:param username: The username to find details of a user.
		:return: None.
		"""
		try:
			await ctx.message.delete()
		except:
			pass
		details = db.sb_details.find_one({"username": username})
		if not details:
			return await ctx.send(content = f"Account with username `{username}` does not exist.")
		db.sb_details.delete_one({"username": username})
		await self.delete_account(ctx, username)

	@commands.command(name = "details", description = "Get the details of a Swagbucks account.")
	@commands.is_owner()
	async def details(self, ctx: commands.Context, username: str):
		"""
		Get the details of a Swagbucks account.
		:param ctx: The context of the command.
		:param username: The username to find details of a user.
		:return: None.
		"""
		try:
			await ctx.message.delete()
		except:
			pass
		await self.account_details(ctx, username)

	@commands.command(name = "show", description = "Get the details of the current game show.")
	@commands.is_owner()
	async def show(self, ctx: commands.Context):
		"""
		Get the details of the current game show.
		:param ctx: The context of the command.
		:return: None.
		"""
		if ctx.guild:
			return await ctx.send(content = "This command can only be used in DMs.")
		await self.show_details(ctx)

	@commands.command(name = "accounts", aliases = ["account"], description = "Get the list of all Swagbucks accounts.")
	@commands.is_owner()
	async def accounts(self, ctx: commands.Context):
		"""
		Get the list of all Swagbucks accounts.
		:param ctx: The context of the command.
		:return: None.
		"""
		if ctx.guild:
			return await ctx.send(content = "This command can only be used in DMs.")
		accounts = list(db.sb_details.find({"id": ctx.author.id}))
		if not accounts:
			return await ctx.send("No accounts found.")
		description = ""
		for index, data in enumerate(accounts):
			description += "{}{} - {}\n".format(0 if index+1 < 10 else "", index+1, data["username"])
		await ctx.send("```\n{}\n```".format(description))

	@commands.command(name = "play", description = "Play the daily trivia game.")
	@commands.is_owner()
	async def play(self, ctx: commands.Context, username: str = None):
		"""
		Play the daily trivia game.
		:param ctx: The context of the command.
		:param username: The username to find details of a user. If not provided, the account of the user will be used.
		:return: None.
		"""
		try:
			await ctx.message.delete()
		except:
			pass
		if not username:
			details = list(db.sb_details.find({"id": ctx.author.id}))
			if not details:
				return await ctx.send("No account found. Please add an account.")
			for data in details:
				access_token = data["access_token"]
				check_token = await self.is_expired(access_token)
				if not check_token:
					return await ctx.send("Your access token has expired. Please update your account. `{}update {}`".format(ctx.prefix, data["username"]))
				await DailyTrivia(access_token).play_daily_trivia(ctx)
		else:
			details = db.sb_details.find_one({"id": ctx.author.id, "username": username})
			if not details:
				return await ctx.send(f"No account found with that username ` {username} `.")
			access_token = details["access_token"]
			check_token = await self.is_expired(access_token)
			if not check_token:
				return await ctx.send("Your access token has expired. Please update your account.")
			await DailyTrivia(access_token).play_daily_trivia(ctx)


	# @commands.command(name = "help", description = "Get help on the commands.")
	async def help(self, ctx: commands.Context):
		"""
		Get help on the commands.
		:param ctx: The context of the command.
		:return: None.
		"""
		embed = discord.Embed(title = "Help", description = "List of commands.", color = discord.Color.blue())
		for command in self.client.commands:
			if command.name == "help":
				continue
			embed.add_field(name = f"{command.name}", value = f"{command.description}", inline = False)
		await ctx.send(embed = embed)

prefix = ".", "-"
intents = discord.Intents.all()
client = commands.Bot(command_prefix = prefix, owner_ids = os.environ['OWNER_IDS'], intents = intents, strip_after_prefix = True, case_insensitive = True)
# client.remove_command("help")
client.add_cog(MainClass(client))

@client.event
async def on_ready():
	print("Logged in as {0.user}".format(client))
	print("Bot is ready.")
	await client.change_presence(activity = discord.Game(name = "Discord!"), status = discord.Status.online)

@client.event
async def on_message(message: discord.Message):
    """
	Send a message to a channel when a message is sent in a guild.
	:param message: The message sent.
	:return: None.
	"""
    if not message.author.bot:
        channel = client.get_channel(os.environ['CHANNEL_ID'])
        embed=discord.Embed(description=message.content, color=discord.Colour.random())
        embed.set_thumbnail(url=message.author.avatar_url)
        embed.set_author(name=message.author, icon_url=message.author.avatar_url)
        embed.set_footer(text=f"Name: {message.author} | ID: {message.author.id}", icon_url=message.author.avatar_url)
        if message.attachments: embed.set_image(url = message.attachments[0].url)
        # await channel.send(embed=embed)
        #embed = discord.Embed(description = f"**You cannot be used me in private messages. For invite me [Click Here](https://discord.com/api/oauth2/authorize?client_id={client.user.id}&permissions=523376&scope=bot).**")
        #return await message.channel.send(embed = embed)
    await client.process_commands(message)

@client.event
async def on_command(ctx: commands.Context):
	channel = client.get_channel(os.environ['CHANNEL_ID'])
	embed = discord.Embed(description = f"Command : `{ctx.command.name}`\nGuild : `{ctx.guild.name if ctx.guild else None}`\nChannel : `{ctx.channel.name if ctx.guild else ctx.channel}`\nCommand Failed : `{ctx.command_failed}`\nMessage :\n```\n{ctx.message.content}\n```",
			color = discord.Color.random(),
			timestamp = ctx.author.created_at)
	embed.set_footer(text = f"ID : {ctx.author.id} | Created at")
	embed.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)
	if ctx.guild: embed.set_thumbnail(url = ctx.guild.icon_url)
	await channel.send(embed = embed)

client.run(os.environ['BOT_TOKEN'])

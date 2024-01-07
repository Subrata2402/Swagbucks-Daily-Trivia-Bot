import discord, config, db
from discord.ext import commands
from sb_daily_trivia import DailyTrivia
from datetime import datetime

class Swagbucks(object):

	# def __init__(self):
	# 	super.__init__()

	async def is_expired(self, bearer_token: str) -> bool:
		"""
		Check if an account is expired and delete it from the database.
		And login again to update the account.
		:param bearer_token: The bearer token to authenticate.
		:return: Either the token is expired or not.
		"""
		daily_trivia = DailyTrivia(bearer_token)
		data = await daily_trivia.fetch("POST", config.trivia_home)
		return data["success"]
	
	async def get_token(self, username: str) -> str or None:
		"""
		Get token from database by username.
		:param username: The username to find details of a user.
		:return: The token of the user. If not found, return None.
		"""
		details = db.sb_details.find_one({"username": username})
		if details:
			return details["access_token"]

	async def update_account(self, ctx: commands.Context, username: str, send: bool = True) -> None or str:
		"""
		If the bearer token is expired then refresh the token and update account.
		:param ctx: The context of the command.
		:param username: The username to find details of a user.
		:param send: If the command is called from a command, send the message.
		:return: None or the access token.
		"""
		details = db.sb_details.find_one({"id": ctx.author.id, "username": username})
		if not details and send:
			return await ctx.send(content = "No account found with that username ` {} `.".format(username))
		user_id = details["user_id"]
		sig = details["sig"]
		headers = {
			"content-type": "application/x-www-form-urlencoded",
			"Host": "app.swagbucks.com",
			"user-agent": "SwagIQ-Android/34 (okhttp/3.10.0);Realme RMX1911",
			"accept-encoding": "gzip",
		}

		data = f"_device=f6acc085-c395-4688-913f-ea2b36d4205f&partnerMemberId={user_id}&partnerUserName={username}&verify=false&partnerApim=1&partnerHash={sig}"
		data = await DailyTrivia().fetch("POST", config.auth_token, headers = headers, data = data)
		access_token = data["accessToken"]
		refresh_token = data["refreshToken"]
		update = {"access_token": access_token, "refresh_token": refresh_token}
		db.sb_details.update_one({"user_id": user_id}, {"$set": update})
		if send: await ctx.send(content = "Account updated successfully.")
		else: return access_token

	async def account_details(self, ctx: commands.Context, username: str) -> None:
		"""
		Get the details of the swagbucks account.
		:param ctx: The context of the command.
		:param username: The username to find details of a user.
		:return: None
		"""
		user_details = db.sb_details.find_one({"id": ctx.author.id, "username": username})
		if not user_details:
			return await ctx.send(content = "No account found with that username ` {} `.".format(username))
		token = user_details["token"]
		params = {
			"token": token, "checkreferral": "false",
			"appid": "37", "appversion": "34"
		}
		headers = {
			"content-type": "application/x-www-form-urlencoded",
			"Host": "app.swagbucks.com",
			"user-agent": "SwagIQ-Android/34 (okhttp/3.10.0);Realme RMX1911",
			"accept-encoding": "gzip",
		}
		data = await DailyTrivia().fetch("POST", config.apm_3, headers = headers, params = params)
		description = f"```\n" \
				f"• User Id             ::  {data['member_id']}\n" \
				f"• Email Verified      ::  {data['email_verified']}\n" \
				f"• Rejoins (Lives)     ::  {data['lives']}\n" \
				f"• Username            ::  {data['user_name']}\n" \
				f"• Swagbucks (SB)      ::  {data.get('swagbucks')}\n" \
				f"• Re-Verification     ::  {data['require_reverification']}\n" \
				f"• Profile Complete    ::  {data['profile_complete']}\n" \
				f"• OTP Verified        ::  {data['otp_verified']}\n" \
				f"• Member Status       ::  {data['member_status']}\n" \
				f"• Pending Earnings    ::  {data['pending_earnings']}\n" \
				f"• Registered Date     ::  {data['registered_date']}\n" \
				f"• Lifetime Earnings   ::  {data['lifetime_earnings']}\n```"
		await ctx.send(content = description)

	async def show_details(self, ctx: commands.Context) -> None:
		"""
		Get the details of the current game show.
		:param ctx: The context of the command.
		:return: None
		"""
		details = list(db.sb_details.find())[0] # Get the first account details from the database.
		access_token = details["access_token"]
		is_valid = await self.is_expired(access_token) # Check if the token is expired.
		if not is_valid:
			access_token = await self.update_account(ctx, details["username"], False) # If token is expired, update the account.
		daily_trivia = DailyTrivia(access_token) 
		data = await daily_trivia.fetch("POST", config.trivia_home) # Get the details of the current show.
		prize = data["episode"]["grandPrizeDollars"] # Get the prize money.
		time = data["episode"]["start"] # Get the start time of the show.
		embed=discord.Embed(title = "__SwagIQ Next Show Details !__", description=f"**• Show Name : Swagbucks Live\n• Show Time : <t:{time}>\n• Prize Money : ${prize}**", color = discord.Colour.random())
		embed.set_thumbnail(url = daily_trivia.icon_url)
		embed.set_footer(text = "Swagbucks Live")
		embed.timestamp = datetime.utcnow()
		await ctx.send(embed = embed)

	async def add_account(self, ctx: commands.Context, access_token: str, token: str, sig: str) -> None:
		"""
		Add a swagbucks account to the database.
		:param ctx: The context of the command.
		:param access_token: The access token of the account.
		:param token: The token of the account.
		:param sig: The signature of the account.
		:return: None
		"""
		is_valid_token = await self.is_expired(access_token)
		if not is_valid_token:
			return await ctx.send(content = "The access token is invalid or expired. Please check the access token and try again.")
		params = {
			"token": token, "checkreferral": "false",
			"appid": "37", "appversion": "34"
		}
		headers = {
			"content-type": "application/x-www-form-urlencoded",
			"Host": "app.swagbucks.com",
			"user-agent": "SwagIQ-Android/34 (okhttp/3.10.0);Realme RMX1911",
			"accept-encoding": "gzip",
		}
		data = await DailyTrivia().fetch("POST", config.apm_3, headers = headers, params = params)
		if data["status"] != 200:
			return await ctx.send(content = "The token is invalid or expired. Please check the token and try again.")
		user_id = data["member_id"]
		username = data["user_name"]
		if db.sb_details.find_one({"id": ctx.author.id, "user_id": user_id}): # Check if the account is already added.
			return await ctx.send(content = "The account is already added.")
		db.sb_details.insert_one({
			"id": ctx.author.id,
			"user_id": user_id,
			"username": username,
			"access_token": access_token,
			"token": token,
			"sig": sig
			})
		await ctx.send(content = "Account added successfully with username ` {} `.".format(username))
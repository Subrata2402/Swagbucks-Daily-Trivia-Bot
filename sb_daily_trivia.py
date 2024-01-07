import aiohttp, json, config
import requests, asyncio, db
from discord.ext import commands
import discord

class DailyTrivia(object):

	def __init__(self, bearer_token: str = None):
		self.bearer_token = bearer_token
		self.entry_id = "1062468$162960984$ccf48ba1481e3bf0954e494010b7a219a3534d7f" # The entry ID.
		self.answers = [] # The answers.
		self.question = "What is the question?" # The question.
		self.icon_url = "https://cdn.discordapp.com/attachments/799861610654728212/991317134930092042/swagbucks_logo.png" # Logo icon url of Swagbucks.
		self.gif_icon_url = "https://cdn.discordapp.com/emojis/773955381063974972.gif" # The icon URL for the playing game.
		self.headers = {
					"Host": "api.playswagiq.com",
					"user-agent": "SwagIQ-Android/37 (okhttp/3.14.9);Realme RMX1911",
					"authorization": "Bearer " + str(self.bearer_token),
					"content-type": "application/x-www-form-urlencoded",
					"accept-encoding": "gzip"
				}

	async def check_daily_trivia(self, ctx: commands.Context) -> bool:
		"""
		Check either daily trivia available or not.
		:param ctx: The context of the command.
		:return: Either daily trivia available or not.
		"""
		response_data = await self.fetch(method = "POST", url = config.trivia_home, headers = self.headers)
		if response_data.get("success"):
			playable = response_data["dailygame"]["playable"]
			if playable:
				return playable
			else:
				next_playable = response_data["dailygame"]["nextAvailableSeconds"]
				hours, remainder = divmod(next_playable, 3600)
				minutes, seconds = divmod(remainder, 60)
				hours, minutes, seconds = int(hours), int(minutes), int(seconds)
				if hours + minutes == 0:
					description = f"You have played all games as of now, so you must wait **{seconds}** second{'' if seconds == 1 else 's'} to play Daily Trivia Challenge once again."
				elif hours == 0:
					description = f"You have played all games as of now, so you must wait **{minutes}** minute{'' if minutes == 1 else 's'} **{seconds}** second{'' if seconds == 1 else 's'} to play Daily Trivia Challenge once again."
				elif minutes == 0:
					description = f"You have played all games as of now, so you must wait **{hours}** hour{'' if hours == 1 else 's'} and **{seconds}** second{'' if seconds == 1 else 's'} to play Daily Trivia Challenge once again."
				else:
					description = f"You have played all games as of now, so you must wait **{hours}** hour{'' if hours == 1 else 's'} **{minutes}** minute{'' if minutes == 1 else 's'} and **{seconds}** second{'' if seconds == 1 else 's'} to play Daily Trivia Challenge once again."
				await ctx.send(embed = discord.Embed(description = description, color = discord.Color.random()))

	async def get_db_answer(self, question: str, options: list) -> str:
		"""
		Get the answer to a question.
		:param question: The question.
		:param options: The list of options.
		:return: The answer.
		"""
		data = db.questions.find_one({"question": question.lower()})
		if not data: return None
		answer = data.get("answer")
		for index, option in enumerate(options):
			if answer == option.lower():
				return index

	async def add_question(self, question: str, answer: str) -> None:
		"""
		Add a question to the database.
		:param question: The question.
		:param answer: The answer.
		:return: None
		"""
		check_question = db.questions.find_one({"question": question.lower()})
		if not check_question:
			db.questions.insert_one({"question": question.lower(), "answer": answer.lower()})
		else:
			print("Already added this question in the database.")

	async def get_google_answer(self, question: str, options: list) -> int:
		"""
		Get the answer to a question.
		:param question: The question.
		:param options: The options.
		:return: The answer.
		"""
		r = requests.get(f"https://www.google.com/search?q={question.replace(' ', '+')}") # Get the Google Search Results
		res = str(r.text).lower()
		count_options = {}
		for choice in options:
			option = choice.strip()
			count_option = res.count(option.lower())
			count_options[option] = count_option
		max_count = max(list(count_options.values()))
		for index, option in enumerate(count_options):
			if count_options[option] == max_count:
				return index

	async def fetch(self, method: str = "POST", url: str = None, headers = None, params = None, data = None) -> dict or str:
		"""
		Fetch data from an API.
		:param method: The HTTP method to use.
		:param function: The function to use.
		:param headers: The headers to use.
		:param params: The parameters to use.
		:param data: The data to use.
		:param host: The host to use.
		:return: The response.
		"""
		async with aiohttp.ClientSession() as client_session:
			response = await client_session.request(method = method, url = url, params = params, headers = headers or self.headers, data = data)
			status = response.status
			content = await response.text()
			# print(content)
			# if status != 200:
			# 	return content # TODO: Raise an exception.
			return json.loads(content)
		
	async def play_daily_trivia(self, ctx: commands.Context) -> None:
		"""
		Play the daily trivia.
		:param ctx: The context.
		:return: None
		"""
		response_data = await self.enter_daily_trivia(ctx)
		if not response_data: return
		# print(response_data)
		# if not response_data["success"]:
		# 	return await ctx.send(content = f"```\n{response_data['errorMsg']}\n```")
		embed = discord.Embed(title = "Starting Daily Trivia...", color = discord.Color.random())
		message = await ctx.send(embed = embed)
		answers = response_data["firstQuestion"]["answers"]
		total_questions = response_data["numberOfQuestions"]
		options = [answer['text'] for answer in response_data["firstQuestion"]["answers"]]
		question = response_data["firstQuestion"]["text"]
		answer = await self.get_db_answer(question, options) # Get the answer from the database.
		if not answer: answer = await self.get_google_answer(question, options) # Get the answer from Google.
		answer_id = response_data["firstQuestion"]["answers"][answer]["idSigned"]
		entry_id = response_data["entryIdSigned"]
		embed.title = "Playing Daily Trivia..."
		embed.description = f"**1. {question}**\n"
		for index, option in enumerate(options):
			embed.description += f"{index + 1}. {option}\n"
		embed.set_thumbnail(url = self.gif_icon_url)
		embed.set_footer(text = "Swagbucks Trivia", icon_url = self.icon_url)
		await message.edit(embed = embed)
		await asyncio.sleep(3)
		while True:
			response_data = await self.send_answer(entry_id, answer_id)
			# print(response_data)
			summary = response_data.get("summary") # Get the summary if the game is over.
			# correct = response_data["correct"] # Get the correct answer.
			for answer in answers:
				if answer["id"] == response_data["correctAnswerId"]:
					await self.add_question(question, answer["text"]) # Add the question to the database.
			if summary:
				# print("Game over!\n")
				# print(f"Correct : {summary['correct']}\nIncorrect : {summary['incorrect']}\nUnclaimed Regions : {summary['unclaimedRejoins']}\nUnclaimed SB : {summary['unclaimedSB']}\n")
				embed.title = "Played Daily Trivia ✅"
				embed.description = f"**▫️ Total Question : {total_questions}\n" \
					f"▫️ Correct Answer : {0 if summary['correct'] < 10 else ''}{summary['correct']}\n" \
						f"▫️ Incorrect Answer : {0 if summary['incorrect'] < 10 else ''}{summary['incorrect']}\n" \
							f"▫️ Unclaimed Regions : {0 if summary['unclaimedRejoins'] < 10 else ''}{summary['unclaimedRejoins']}\n" \
								f"▫️ Unclaimed SB : {0 if summary['unclaimedSB'] < 10 else ''}{summary['unclaimedSB']}**\n"
				embed.set_thumbnail(url = self.icon_url)
				await message.edit(embed = embed)
				if summary["unclaimedSB"] > 0:
					embed = discord.Embed(title = "SB Daily Trivia", color = discord.Color.random())
					embed.description = f"**{summary['unclaimedSB']}** SB is available to claim. Claiming SB..."
					# embed.set_thumbnail(url = self.icon_url)
					message = await ctx.send(embed = embed)
					await asyncio.sleep(2)
					response_data = await self.claim_sb(entry_id) # Claim SB.
					if response_data["success"]:
						embed.description = f"**{summary['unclaimedSB']}** SB has been claimed."
					else:
						embed.description = f"**{summary['unclaimedSB']}** SB could not be claimed. Error : {response_data.get('errorMsg')}"
					await message.edit(embed = embed)
					break; return
			else:
				answers = response_data["nextQuestion"]["answers"]
				question = response_data["nextQuestion"]["text"]
				options = [answer['text'] for answer in response_data["nextQuestion"]["answers"]]
				answer = await self.get_db_answer(question, options) # Get the answer index to use from the database.
				if not answer: answer = await self.get_google_answer(question, options) # Get the answer index to use from the Google.
				answer_id = response_data["nextQuestion"]["answers"][answer]["idSigned"]
				question_number = response_data["nextQuestionNumber"]
				embed.description = f"**{question_number}. {question}**\n"
				for index, option in enumerate(options):
					embed.description += f"{index + 1}. {option}\n"
				await message.edit(embed = embed)
				await asyncio.sleep(3)


	async def enter_daily_trivia(self, ctx: commands.Context) -> dict:
		"""
		Enter to the daily trivia.
		:return: The response.
		"""
		trivia_available = await self.check_daily_trivia(ctx)
		if not trivia_available: return
		response_data = await self.fetch(method = "POST", url = config.daily_trivia, headers = self.headers)
		return response_data
	
	async def send_answer(self, entry_id: str, answer_id: str) -> dict:
		"""
		Send answer to the daily trivia.
		:param entry_id: The entry id to use.
		:param answer_id: The answer id to use.
		:return: The response.
		"""
		params = {"entryid": entry_id, "aid": answer_id}
		response_data = await self.fetch(method = "POST", url = config.send_answer, headers = self.headers, params = params, data = None)
		return response_data

	async def claim_sb(self, entry_id: str) -> dict:
		"""
		Claim SB.
		:param entry_id: The entry id to use.
		:return: The response.
		"""
		params = {"entryid": entry_id}
		response_data = await self.fetch(method = "POST", url = config.claim_sb, headers=self.headers, params = params, data = None)
		return response_data
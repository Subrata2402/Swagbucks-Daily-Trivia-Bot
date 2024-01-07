import aiohttp, json, config
import requests, asyncio, db

class DailyTrivia(object):

	def __init__(self, bearer_token: str):
		self.bearer_token = bearer_token
		self.entry_id = "1062468$162960984$ccf48ba1481e3bf0954e494010b7a219a3534d7f" # The entry ID.
		self.answers = [] # The answers.
		self.question = "What is the question?" # The question.
		self.headers = {
					"Host": "api.playswagiq.com",
					"user-agent": "SwagIQ-Android/37 (okhttp/3.14.9);Realme RMX1911",
					"authorization": "Bearer " + self.bearer_token,
					"content-type": "application/x-www-form-urlencoded",
					"accept-encoding": "gzip"
				}

	async def check_daily_trivia(self) -> bool:
		"""
		Check either daily trivia available or not.
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
					print(f"You have played all games as of now, so you must wait **{seconds}** second{'' if seconds == 1 else 's'} to play Daily Challenge once again.")
				elif hours == 0:
					print(f"You have played all games as of now, so you must wait **{minutes}** minute{'' if minutes == 1 else 's'} **{seconds}** second{'' if seconds == 1 else 's'} to play Daily Challenge once again.")
				elif minutes == 0:
					print(f"You have played all games as of now, so you must wait **{hours}** hour{'' if hours == 1 else 's'} and **{seconds}** second{'' if seconds == 1 else 's'} to play Daily Challenge once again.")
				else:
					print(f"You have played all games as of now, so you must wait **{hours}** hour{'' if hours == 1 else 's'} **{minutes}** minute{'' if minutes == 1 else 's'} and **{seconds}** second{'' if seconds == 1 else 's'} to play Daily Challenge once again.")


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

	async def get_not_question(self, question: str) -> bool:
		"""
		Check either a question negative or not.
		:param question: The question.
		:return: Either a question negative or not.
		"""
		for negative_word in config.negative_words:
			if negative_word in question:
				not_question = True
				break
			else:
				not_question = False
		return not_question

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
		min_count = min(list(count_options.values()))
		not_question = await self.get_not_question(question)
		min_max_count = min_count if not_question else max_count
		for index, option in enumerate(count_options):
			if count_options[option] == min_max_count:
				return index

	async def fetch(self, method: str = "GET", url: str = None, headers = None, params = None, data = None) -> dict:
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
			response = await client_session.request(method = method, url = url, params = params, headers = headers, data = data)
			status = response.status
			content = await response.text()
			print(content)
			if status != 200:
				return content # TODO: Raise an exception.
			return json.loads(content)
		
	async def enter_daily_trivia(self) -> str:
		"""
		Enter to the daily trivia.
		:return: The answer id.
		"""
		trivia_available = await self.check_daily_trivia()
		if not trivia_available: return
		response_data = await self.fetch(method = "POST", url = config.daily_trivia, headers = self.headers)
		if response_data["success"] == False:
			print(response_data["errorMsg"])
			return
		self.answers = response_data["firstQuestion"]["answers"]
		options = [answer['text'] for answer in response_data["firstQuestion"]["answers"]]
		self.question = response_data["firstQuestion"]["text"]
		answer = await self.get_db_answer(self.question, options) # Get the answer from the database.
		if not answer: answer = await self.get_google_answer(self.question, options) # Get the answer from Google.
		answer_id = response_data["firstQuestion"]["answers"][answer]["idSigned"]
		self.entry_id = response_data["entryIdSigned"]
		print(f"1. {self.question}")
		print(f"Options : {options}")
		await self.send_answer(answer_id)
	
	async def send_answer(self, answer_id: str) -> None:
		"""
		Send answer to the daily trivia.
		:param answer_id: The answer id to use.
		:return: The summary.
		"""
		params = {"entryid": self.entry_id, "aid": answer_id}
		response_data = await self.fetch(method = "POST", url = config.send_answer, headers = self.headers, params = params, data = None)
		summary = response_data.get("summary") # Get the summary if the game is over.
		correct = response_data["correct"] # Get the correct answer.
		print(f"Correct answer : {correct}")
		for answer in self.answers:
			if answer["id"] == response_data["correctAnswerId"]:
				print(f"Correct answer : {answer['text']}\n")
				await self.add_question(self.question, answer["text"]) # Add the question to the database.
		if summary:
			print("Game over!\n")
			print(f"Correct : {summary['correct']}\nIncorrect : {summary['incorrect']}\nUnclaimed Regions : {summary['unclaimedRejoins']}\nUnclaimed SB : {summary['unclaimedSB']}\n")
			if summary["unclaimedSB"] > 0:
				print("Claiming SB...")
				return await self.claim_sb() # Claim SB.
		else:
			self.answers = response_data["nextQuestion"]["answers"]
			self.question = response_data["nextQuestion"]["text"]
			options = [answer['text'] for answer in response_data["nextQuestion"]["answers"]]
			answer = await self.get_db_answer(self.question, options) # Get the answer index to use from the database.
			if not answer: answer = await self.get_google_answer(self.question, options) # Get the answer index to use from the Google.
			answer_id = response_data["nextQuestion"]["answers"][answer]["idSigned"]
			question_number = response_data["nextQuestionNumber"]
			print(f"{question_number}. {self.question}")
			print(f"Options : {options}")
			await asyncio.sleep(3)
			await self.send_answer(answer_id)

	async def claim_sb(self) -> None:
		"""
		Claim SB.
		:return: None.
		"""
		params = {"entryid": self.entry_id}
		response_data = await self.fetch(method = "POST", url = config.claim_sb, headers=self.headers, params = params, data = None)
		if response_data["success"]:
			print("Successfully claimed SB!")
		else:
			print("Failed to claim SB!")

for token in config.BEARER_TOKEN:
	p = input("Enter to start the daily trivia...")
	if p == "exit":
		break
	daily_trivia = DailyTrivia(token)
	asyncio.run(daily_trivia.enter_daily_trivia())
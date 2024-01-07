apm_15 = "https://app.swagbucks.com/?cmd=apm-15"
response_data = {
	"code": 0,
	"message": {
		"SWAGCODE_TIMER": "60"
		}
	}
apm_3 = "https://app.swagbucks.com/?cmd=apm-3"
response_data = {
		"user_name": "sakhman2001s1",
		"swagbucks": 417,
		"require_reverification": False,
		"verification_earning_threshold": 2147483647,
		"home_page": 1,
		"sig": "0d46dd156a6c6846f539ce0d89e313a9667016b601a2e05a67d6d61edd23d71d",
		"otp_verified": True,
		"new_user": True,
		"member_status": "ACTIVE",
		"needs_data_privacy_response": False,
		"verify": False,
		"pending_earnings": 0,
		"lifetime_earnings": 417,
		"member_id": 127137912,
		"email_verified": True,
		"lives": 29,
		"logged_in": True,
		"user_name_temp": True,
		"profile_complete": False,
		"expgrids": "68|591|613",
		"rate_app": False,
		"is_gdpr_member": False,
		"needs_gdpr_consent": False,
		"registered_date": "08/16/2022",
		"status": 200
	}

negative_words = {
    " not ", "least", "except", "never", "incorrect", "incorrectly", "none", "cannot", "can't", "didn't", "doesn't", "don't",
    "won't", "hasn't", "haven't", "shouldn't", "wouldn't", "wasn't", "aren't", "isn't", "couldn't", "weren't", "can't", "didn't",
    "doesn't", "don't", "won't", "hasn't", "haven't", "shouldn't", "wouldn't", "wasn't", "aren't", "isn't", "couldn't", "weren't",
    "hadn't", "hadn't", "mustn't", "mustn't"
}

daily_trivia = "https://api.playswagiq.com/dailygame/enter"
response_data = {'entryIdSigned': '1036564$162876338$4b3fde38943071b7e8b2be49adad598e05b455dc',
				'firstQuestion': {'answers': [{'id': 3769,
											'idSigned': '3769$162876338$9ab35cfe8eff852ccaa74f86a829020ec5b96260',
											'text': 'Rock the Casbah'},
											{'id': 3770,
											'idSigned': '3770$162876338$d82430cb21b52cccd511e502c132d7c72a326bfd',
											'text': 'Train in Vain'},
											{'id': 3771,
											'idSigned': '3771$162876338$f1737311c988bf99ca6772f8ba71eb7294c7fe49',
											'text': 'London Calling'}],
								'idSigned': '1255$162876338$500982397d892fdc358e1c76088b43445acc9f1b',
								'text': 'In which song by the Clash do we learn that "phony '
										'Beatlemania has bitten the dust?"'},
				'numberOfQuestions': 10,
				'secondsBetweenQuestions': 3,
				'secondsToAnswer': 10,
				'success': True}

{'success': False, 'errorCode': 50101, 'errorMsg': 'Daily game not available'}

send_answer = "https://api.playswagiq.com/dailygame/answer"
response_data = {'correct': False,
				'correctAnswerId': 3771,
				'nextQuestion': {'answers': [{'id': 38002,
											'idSigned': '38002$162877021$c94906b9650075d92359a63348756b39bdd55a5f',
											'text': 'Wooden Blocks'},
											{'id': 38003,
											'idSigned': '38003$162877021$6a7e56ab9e4eb0b9ed1f249b127cded126f07db0',
											'text': 'Ventriloquist Dummy'},
											{'id': 38004,
											'idSigned': '38004$162877021$984915abbb2459831453fb21a6207a54724b66f6',
											'text': 'Model Train'}],
								'idSigned': '12666$162877021$795bd230b642b4e906fe7dd96e15e3615edabfef',
								'text': 'Woody from "Toy Story" was originally supposed to '
										'be what kind of toy?'},
				'nextQuestionNumber': 2,
				'success': True,
				'timedout': True}

response_data = {'correct': True,
				'correctAnswerId': 29393,
				'finished': True,
				'success': True,
				'summary': {'correct': 4,
							'incorrect': 6,
							'unclaimedRejoins': 0,
							'unclaimedSB': 1},
				'timedout': False}

claim_sb = "https://api.playswagiq.com/dailygame/claim"
response_data = {'success': True, 'claimed': True}

trivia_home = "https://api.playswagiq.com/trivia/home"
response_data = {'dailygame': {'enabled': True, 'nextAvailableSeconds': 0, 'playable': True},
				'episode': {'commentSubjectId': 1421,
							'grandPrizeDollars': 1000,
							'id': 1421,
							'start': 1677873600,
							'startDisplay': '12pm PT',
							'title': '2023-03-03 12:00pm PT',
							'uuid': '21dfd1a2-24e3-4b08-b65a-12884bb96a3f'},
				'pendingSBDiff': 0,
				'success': True,
				'weeklyRank': 0}

auth_token = "https://api.playswagiq.com/auth/token"
response_data = {'accessToken': 'Cb2zsJHdN-HK3Twr-SPfSryA_phUhUuWL8ewjO7Emty_ghrzsdHBxNJV_CcnJ3sa57jTFv3l-SGrMdnOPB8cgVRm1W5pkw',
				'profile': {'id': 1555237,
							'partnerMemberId': 127137912,
							'username': 'sakhman2001s1'},
				'refreshToken': 'Cb2zsF5hASag8t_C6WgyREaBjm1AgshaLIUUGfe01CIphWJ3DVFjXkLslTUXyi11rlwF-so8HrzdR6Q-jDkVSu4',
				'success': True}

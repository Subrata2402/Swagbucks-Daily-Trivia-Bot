from pymongo import MongoClient
import os

data = MongoClient(os.environ['MONGO_URL'])
db = data.get_database("SBDailyTrivia")
questions = db.questions
sb_details = db.sb_details

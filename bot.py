import socket
import re
import time
import sqlite3
import json
import urllib.request
import _thread
import random
import math
import config
                      
LAST_API_REQUEST = None
CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

#making connections to the twitch irc
twitch = socket.socket()
twitch.connect((config.HOST, config.PORT))
twitch.send("PASS {}\r\n".format(config.PASS).encode("utf-8"))
twitch.send("NICK {}\r\n".format(config.NICK).encode("utf-8"))
twitch.send("JOIN {}\r\n".format(config.CHAN).encode("utf-8"))
print("Connected!")

#connect to database
conn = sqlite3.connect("botData.db")
db = conn.cursor()
db.execute("CREATE TABLE IF NOT EXISTS users (name text PRIMARY KEY, rank text, points real, viewtime real)") 
conn.commit()

#fetch summoner id
url = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}?api_key={}".format(config.SUMM,config.API_KEY)
jsonurl = urllib.request.urlopen(url)
jsonstr = jsonurl.read().decode("utf-8")
summ_info = json.loads(jsonstr)
SUMM_ID = summ_info["id"]

#define and start function to monitor user time and points
def monitorUsers():
	userurl = "https://tmi.twitch.tv/group/user/{}/chatters".format(config.CHAN.replace("#",""))
	conn = sqlite3.connect("botData.db")
	db = conn.cursor()
	previous = []
	current = []
	while True:
		jsonurl = urllib.request.urlopen(userurl)
		jsonstr = jsonurl.read().decode("utf-8")
		viewer_info = json.loads(jsonstr)
		viewer_list = viewer_info["chatters"]
		for types in viewer_list:
			for user in viewer_list[types]:
				db.execute("INSERT INTO users(name,points,viewtime) SELECT ?,?,? WHERE NOT EXISTS(SELECT * FROM users WHERE name=?)",(user,0,0,user))
				conn.commit()
				current.append(user)
		for user in current:
			if user in previous:
				viewtime = db.execute("SELECT viewtime FROM users WHERE name=?",(user,)).fetchone()[0]
				if viewtime % 5 == 0:
					db.execute("UPDATE users SET points=points+5, viewtime=viewtime+1 WHERE name=?",(user,))
				else:
					db.execute("UPDATE users SET viewtime=viewtime+1 WHERE name=?",(user,))
				conn.commit()      
		previous = current
		current = []
		time.sleep(60)
try:
	_thread.start_new_thread(monitorUsers,())
	print("Monitoring Users!")
except:
	print("Error: unable to start thread")

def chat(msg):
	message = "PRIVMSG {} :{}\r\n".format(config.CHAN, msg)
	twitch.send(message.encode("utf-8"))

def ban(user):
	chat(".ban {}".format(user))

def timeout(user, secs=600):
	chat(".timeout {}".format(user, secs))

def addRank(user):
	rank = db.execute("SELECT rank FROM users WHERE name=?",(username,)).fetchone()[0]
	if rank is None:
		return
	if rank == "Bronze 5":
		rank = "Bronze 4"
	elif rank == "Bronze 4":
		rank = "Bronze 3"
	elif rank == "Bronze 3":
		rank = "Bronze 2"
	elif rank == "Bronze 2":
		rank = "Bronze 1"
	elif rank == "Bronze 1":
		rank = "Silver 5"
	elif rank == "Silver 5":
		rank = "Silver 4"
	elif rank == "Silver 4":
		rank = "Silver 3"
	elif rank == "Silver 3":
		rank = "Silver 2"
	elif rank == "Silver 2":
		rank = "Silver 1"
	elif rank == "Silver 1":
		rank = "Gold 5"
	elif rank == "Gold 5":
		rank = "Gold 4"
	elif rank == "Gold 4":
		rank = "Gold 3"
	elif rank == "Gold 3":
		rank = "Gold 2"
	elif rank == "Gold 2":
		rank = "Gold 1"
	elif rank == "Gold 1":
		rank = "Platinum 5"
	elif rank == "Platinum 4":
		rank = "Platinum 3"
	elif rank == "Platinum 3":
		rank = "Platinum 2"
	elif rank == "Platinum 2":
		rank = "Platinum 1"
	elif rank == "Platinum 1":
		rank = "Diamond 5"
	elif rank == "Diamond 5":
		rank = "Diamond 4"
	elif rank == "Diamond 4":
		rank = "Diamond 3"
	elif rank == "Diamond 3":
		rank = "Diamond 2"
	elif rank == "Diamond 2":
		rank = "Diamond 1"
	elif rank == "Diamond 1":
		rank = "Masters"
	elif rank == "Masters":
		rank = "Challenger"
	db.execute("UPDATE users SET rank=? WHERE name=?",(rank,username))
	conn.commit()

def subRank(user):
	rank = db.execute("SELECT rank FROM users WHERE name=?",(username,)).fetchone()[0]
	if rank is None:
		return
	if rank == "Bronze 4":
		rank = "Bronze 5"
	elif rank == "Bronze 3":
		rank = "Bronze 4"
	elif rank == "Bronze 2":
		rank = "Bronze 3"
	elif rank == "Bronze 1":
		rank = "Bronze 2"
	elif rank == "Silver 5":
		rank = "Bronze 1"
	elif rank == "Silver 4":
		rank = "Silver 5"
	elif rank == "Silver 3":
		rank = "Silver 4"
	elif rank == "Silver 2":
		rank = "Silver 3"
	elif rank == "Silver 1":
		rank = "Silver 2"
	elif rank == "Gold 5":
		rank = "Silver 1"
	elif rank == "Gold 4":
		rank = "Gold 5"
	elif rank == "Gold 3":
		rank = "Gold 4"
	elif rank == "Gold 2":
		rank = "Gold 3"
	elif rank == "Gold 1":
		rank = "Gold 2"
	elif rank == "Platinum 5":
		rank = "Gold 1"
	elif rank == "Platinum 4":
		rank = "Platinum 5"
	elif rank == "Platinum 3":
		rank = "Platinum 4"
	elif rank == "Platinum 2":
		rank = "Platinum 3"
	elif rank == "Platinum 1":
		rank = "Platinum 2"
	elif rank == "Diamond 5":
		rank = "Platinum 1"
	elif rank == "Diamond 4":
		rank = "Diamond 5"
	elif rank == "Diamdond 3":
		rank = "Diamond 4"
	elif rank == "Diamond 2":
		rank = "Diamond 3"
	elif rank == "Diamond 1":
		rank = "Diamond 2"
	elif rank == "Masters":
		rank = "Diamond 1"
	elif rank == "Challenger":
		rank = "Masters"   
	db.execute("UPDATE users SET rank=? WHERE name=?",(rank,username))
	conn.commit()

betting_open = None
def handleCommand(msg,username):
	r = re.search(r"(\S+)\s*([0,1,2,3,4,5,6,7,8,9]*)",msg)
	msg = r.group(1)
	points = r.group(2)
	print(msg + " " + points)
	if msg == "!hello":
			print("I hear you")
			chat("Hello {}!".format(username))
	elif msg == "!commands":
		chat("Command List: !hello, !rank, !placements, !boost, !time, !points\r\n")
	elif msg == "!rank":
		rank = db.execute("SELECT rank FROM users WHERE name=?",(username,)).fetchone()[0]
		if rank is None:
			chat("@{}, You are not currently ranked. Please do your placements with the command !placements".format(username))
		else:
			chat("@{}, Your current rank is {}".format(username,rank))
	elif msg == "!placements":
		rank = db.execute("SELECT rank FROM users WHERE name=?",(username,)).fetchone()[0]
		if rank is not None:
			chat("@{}, you have already done your placements. You may only do them once.".format(username))
			return
		chat("@{} attemts to do their placements.".format(username))
		time.sleep(5)
		rank = math.ceil(random.randrange(0,100))
		if rank < 10:
			rank = "Bronze 5"
		elif rank < 20:
			rank = "Bronze 4"
		elif rank < 30:
			rank = "Bronze 3"
		elif rank < 40:
			rank = "Bronze 2"
		elif rank < 50:
			rank = "Bronze 1"
		elif rank < 60:
			rank = "Silver 5"
		elif rank < 65:
			rank = "Silver 4"
		elif rank < 70:
			rank = "Silver 3"
		elif rank < 75:
			rank = "Silver 2"
		elif rank < 80:
			rank = "Silver 1"
		elif rank < 85:
			rank = "Gold 5"
		elif rank < 90:
			rank = "Gold 4"
		elif rank < 95:
			rank = "Gold 3"
		elif rank < 97:
			rank = "Gold 2"
		elif rank < 98:
			rank = "Gold 1"
		elif rank <= 100:
			rank = "Platinum 5"
		db.execute("UPDATE users SET rank=? WHERE name=?",(rank,username))
		conn.commit()
		chat("@{}, finished their placement and was placed in {}!".format(username,rank))
	elif msg == "!boost":
		rank = db.execute("SELECT rank FROM users WHERE name=?",(username,)).fetchone()[0]
		if rank is None:
			chat("@{}, you cannot get boosted during your placements. Please do your placements first with the command !placements".format(username))
			return
		curPoints = db.execute("SELECT points FROM users WHERE name=?",(username,)).fetchone()[0]
		try:
			if curPoints < float(points):
				chat("@{}, you don't have that many points. You currently have {} points.".format(username,int(curPoints)))
				return
		except:
			chat("@{}, you must pay for your boost! Use !boost <points to pay>".format(username))
			return
		chat("{} attempts to boost their account for {} points.".format(username,points))
		db.execute("UPDATE users SET points=points-? WHERE name=?",(points,username))
		conn.commit()
		diff = abs(random.random()*100 - random.random()*100)
		time.sleep(5)
		if diff <= float(points):
			addRank(username)
			rank = db.execute("SELECT rank FROM users WHERE name=?",(username,)).fetchone()[0]
			chat("@{} was boosted a rank to {}!".format(username,rank))
		else:
			rank = db.execute("SELECT rank FROM users WHERE name=?",(username,)).fetchone()[0]
			subRank(username)
			chat("{} purchased a cheap boost. He lost and was demoted to {}".format(username,rank))
			
	elif msg == "!time":
		viewtime = db.execute("SELECT viewtime FROM users WHERE name=?",(username,)).fetchone()[0]
		chat("@{}, You have watched for {} hours and {} min".format(username,int(viewtime/60),int(60*(viewtime/60 - int(viewtime/60)))))
	elif msg == "!points":
		points = db.execute("SELECT points FROM users WHERE name=?",(username,)).fetchone()[0]
		chat("@{}, You have {} points".format(username,int(points)))
	elif msg == "!bet":
		if betting_open is None:
			chat("@{}, betting has closed. Please wait until betting opens again".format(username))
			return
	elif msg == "!doinks":
		chat("Big doinks")
	elif msg == "!mixer":
		chat("LUL")

def getGameId():
	url = "https://na1.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{}?api_key={}".format(SUMM_ID,config.API_KEY)
	global LAST_API_REQUEST
	if LAST_API_REQUEST is not None:
		if time.time() - LAST_API_REQUEST <= 2:
			return None
	LAST_API_REQUEST = time.time()
	try:
		jsonurl = urllib.request.urlopen(url)
	except:
		return None
	jsonstr = jsonurl.read().decode("utf-8")
	game_info = json.loads(jsonstr)
	gameId = game_info["gameId"]
	return gameId

def getGameStatus(gameId):
	url = "https://na1.api.riotgames.com/lol/match/v4/matches/{}?api_key={}".format(gameId,config.API_KEY)
	global LAST_API_REQUEST
	if LAST_API_REQUEST is not None:
		if time.time() - LAST_API_REQUEST <= 2:
			return None
	LAST_API_REQUEST = time.time()
	try:
		jsonurl = urllib.request.urlopen(url)
	except:
		return None
	jsonstr = jsonurl.read().decode("utf-8")
	game_info = json.loads(jsonstr)
	part_id = None
	team_id = 0
	win = False
	for id in game_info["participantIdentities"]:
		if id["player"]["summonerId"] == SUMM_ID:
			part_id = id["participantId"]
	for part in game_info["participants"]:
		if part["participantId"] == part_id:
			team_id = part["teamId"]
	for team in game_info["teams"]:
		if team["teamId"] == team_id:
			if team["win"] == "Win":
				win = True
				print("win")
			elif team["win"] == "Fail":
				win = False
				print("loss")
	return win

random.seed()
cur_game_id = None
while True:
	response = twitch.recv(1024).decode("utf-8")
	if response == "PING :tmi.twitch.tv\r\n":
		twitch.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
	else:
		username = re.search(r"\w+", response).group(0)
		message = CHAT_MSG.sub("", response)
		print(username + ": " + message)
		handleCommand(message,username)
	if cur_game_id is not None:
		status = getGameStatus(cur_game_id)
		if status is not None:
			if status:
				chat("The game has been won!")
			else:
				chat("The game was lost!")
			cur_game_id = None
	else:
		temp = getGameId()
		if temp is not None:
			time.time
			chat("A game has begun. Place your bets!")
			cur_game_id = temp
			print(cur_game_id)
	time.sleep(1 / config.RATE)

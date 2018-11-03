#!/usr/bin/python3
import sys
import socket
import random
import time
import urllib.parse
from urllib.request import urlopen
from bs4 import BeautifulSoup
from threading import Thread

try:
    f = open("config.txt", "r")
    channel = f.read().split('\'')[1]
    f.close()
except SyntaxError:
    print("Read File Error")
    channel = "#CN_DEMO"

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
botnick = "bot_b03703012" # Bot nickname
server = "chat.freenode.net"

ircsock.connect((server, 6667))
# Once the connection is established we need to send some information to the server to let it know who we are.
# We do this by sending our user information and setting the nickname we’d like to go by.
ircsock.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick + " " + botnick + "\n", "UTF-8")) # User information
ircsock.send(bytes("NICK "+ botnick +"\n", "UTF-8")) # Assign the nick to the bot

def joinchan(chan): # join channel(s).
    ircsock.send(bytes("JOIN "+ chan +"\n", "UTF-8")) 
    ircmsg = ""
    while ircmsg.find("End of /NAMES list.") == -1: 
        ircmsg = ircsock.recv(2048).decode("UTF-8")
        ircmsg = ircmsg.strip('\n\r')
        print(ircmsg)

def ping(): # Responds to server Pings.
    ircsock.send(bytes("PONG\n", "UTF-8"))

def sendmsg(msg, person): # Sends message to the channel.
    ircsock.send(bytes("PRIVMSG "+ person +" :"+ msg +"\n", "UTF-8"))

def recvmsg(): # Receives and print message from the channel.
    ircmsg = (ircsock.recv(4096).decode("UTF-8")).strip('\n\r')
    return ircmsg

def isHoroscope(msg):
    horoscopes = ["Capricorn", "Aquarius", "Pisces", "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius"]
    for horoscope in horoscopes:
        if horoscope == msg:
            return True
    return False
    
def guessNum(person):
    sendmsg("Guess a number between 1 and 10!", person)
    ans = random.randint(1, 10)
    guessed = [False]*11
    while guessed[ans] == False:
        ircmsg = recvmsg()
        fromWho = (ircmsg.split('PRIVMSG', 1)[0].split('!', 1)[0])[1:]
        if ircmsg.find("PRIVMSG") != -1 and fromWho == person:
            print(ircmsg)
            value = ircmsg.split('PRIVMSG', 1)[1].split(':', 1)[1]
            isInt = True
            try:
                num = int(value)
            except ValueError:
                isInt = False
            if isInt == True:
                print(num)
                if(num > 10 or num < 1):
                    sendmsg("Please enter a number BETWEEN 1 and 10.", person)
                else:
                    strnum = str(num)
                    if num < ans:
                        if guessed[num]:
                            sendmsg("You have already guessed " + strnum + "... Larger than " + strnum + "!", person)
                        else: 
                            sendmsg("Larger than " + strnum + "!", person)
                            guessed[num] = True
                    elif num > ans:
                        if guessed[num]:
                            sendmsg("You have already guessed " + strnum + "... Smaller than " + strnum + "!", person)
                        else: 
                            sendmsg("Smaller than " + strnum + "!", person)
                            guessed[num] = True
                    else: 
                        sendmsg("Congrats! You've guessed the correct answer: " + strnum + "!", person)
                        guessed[num] = True
        else:
            if ircmsg.find("PING :") != -1:
                ping()
                print("PONG!")

def musicBot(song, person):
    query = urllib.parse.quote(song)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, features = "html.parser")
    vids = soup.findAll(attrs={'class':'yt-uix-tile-link'})
    vidList = []
    for vid in vids:
        vidList.append("https://www.youtube.com" + vid['href'])
    sendmsg(vidList[0], person)

class ChatThreads:
    def __init__(self, person):
        self.leave = False
        self.person = person
        self.haveMail = True
    def getInput(self, msg):
        msg = input()
        self.haveMail = False
    def chatSend(self):
        while self.leave == False:
            msg = input()
            if self.leave == False:
                ircsock.send(bytes("PRIVMSG "+ channel +" :"+ msg +"\n", "UTF-8"))
    def chatRecv(self):
        while self.leave == False:
            ircmsg = (ircsock.recv(4096).decode("UTF-8")).strip('\n\r')
            fromWho = (ircmsg.split('PRIVMSG', 1)[0].split('!', 1)[0])[1:]
            if ircmsg.find("PRIVMSG") != -1 and fromWho == person:
                msg = ircmsg.split('PRIVMSG', 1)[1].split(':', 1)[1]
                print(self.person + ": " + msg)
                if msg == "!bye":
                    self.leave = True
                else:
                    self.haveMail = True
            else:
                if ircmsg.find("PING :") != -1:
                    ping()
    def run(self):
        sendThread = Thread(target = self.chatSend)
        recvThread = Thread(target = self.chatRecv)
        sendThread.start()
        recvThread.start()
        sendThread.join()
        recvThread.join()

def chat(person):
    print("========", person, "wants to connect with you ========")
    chat = ChatThreads(person)
    chat.run()
    print("==========", person, "has left the chatroom ==========")

if __name__ == '__main__':
    joinchan(channel)
    sendmsg("I'm " + botnick, channel)
    ircmsg = ""
    while 1:
        ircmsg = recvmsg()
        if ircmsg.find("PRIVMSG") != -1:
            print(ircmsg)
            command = ircmsg.split('PRIVMSG', 1)[1].split(':', 1)[1]
            person = (ircmsg.split('PRIVMSG', 1)[0].split('!', 1)[0])[1:]
            if command.find("!") != -1:
                command = ircmsg.split('!', 1)[1]
                if command.find("guess") != -1:
                    guessNum(person)
                elif command.find("song") != -1:
                    song = command.split(' ', 1)[1]
                    musicBot(song, person)
                elif command.find("chat") != -1:
                    print("person = " + person)
                    chat(person)
            elif isHoroscope(command):
                sendmsg("The positions of stars and planets when you were born will not affect your life in any way.", person)
        else:
            if ircmsg.find("PING :") != -1:
                ping()

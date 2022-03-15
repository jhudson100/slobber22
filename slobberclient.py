import tornado 
import tornado.websocket
import tornado.ioloop 
import subprocess
import asyncio 
import json
import sys 
import random
from Card import Card

#this is just a testbed for the server
#In the real slobberhannes program,
#this would be implemented in Javascript (in the browser)
#and would not use Tornado.



class Player:
    def __init__(self,name):
        self.name=name
        self.myHand=[]
    def setHand(self,cardlist):
        self.myHand=[]
        for c in cardlist:
            rank = c["rank"]
            suit = c["suit"]
            self.myHand.append( Card(rank,suit))
            

class HumanPlayer(Player):
    def __init__(self,name):
        super().__init__(name)
    def getCardToPlay(self,leadSuit,playedCards):
        while True:
            print("Played cards:",playedCards)
            print("My hand:")
            for i in range(len(self.myHand)):
                print(i," = ",self.myHand[i])
            ci = input("Which card to play?")
            try:
                ci = int(ci)
                if ci >= 0 and ci < len(self.myHand):
                    c = self.myHand.pop(ci)
                    return c
            except ValueError:
                pass
            print("Bad index, try again!")

class AIPlayer(Player):
    def __init__(self,name):
        super().__init__(name)
        
    def getCardToPlay(self,leadSuit,playedCards):
        #really dumb AI:
        #try to match the lead suit.
        #If not possible, play anything
        for i in range(len(self.myHand)):
            c = self.myHand[i]
            if c.suit == leadSuit:
                self.myHand.pop(i)
                return c
        return self.myHand.pop(0)
        



async def main():
    #ai or human?
    mode = sys.argv[1]
    
    #player's name (humanly readable)
    name = sys.argv[2]
    
    print("Client",mode,name,"is starting...")
    
    if mode == "ai":
        player = AIPlayer(name)
    elif mode == "human":
        player = HumanPlayer(name)
    else:
        assert 0
    
    #get server url from the command line
    url=sys.argv[3]

    print(name,": Connecting...")
    global conn
    conn = await tornado.websocket.websocket_connect(
        url=url,
        on_message_callback=lambda msg: messageCallback(conn, player, msg)
    )
    conn.write_message(json.dumps({"type":"sitDown","name":name}))
    
    #run forever
    await(asyncio.gather(*asyncio.all_tasks()))
    
    print("Client exiting")
    
playedCards=[]

def messageCallback(sock,player,msg):
    #called in response to a server message
    
    if msg == None:
        print(player.name,": The server vanished!")
        sys.exit(1)
    mj = json.loads(msg)
    typ = mj["type"]
    if typ == "newPlayer":
        print(player.name,": A new player joined:",mj["name"])
    elif typ == "playMade":
        c = Card(mj["rank"],mj["suit"])
        print(player.name,": Player",mj["who"],"played a card:",c)
        playedCards.append(c)
    elif typ == "deal":
        myHand = mj["cards"]
        player.setHand(myHand)
    elif typ == "play":
        print(player.name,": Need to get a card to play.")
        ls = mj["leadSuit"]
        c = player.getCardToPlay(ls,playedCards)
        print(player.name,": I will play:",c)
        sock.write_message( 
            json.dumps({"type":"played","rank":c.rank,"suit":c.suit})
        )
    elif typ == "turned":
        print(player.name,": Trick turned; winner=",mj["winner"])
        del playedCards[0:len(playedCards)]
            
asyncio.run(main())

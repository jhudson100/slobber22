import tornado 
import tornado.websocket
import tornado.ioloop 
import subprocess
import asyncio 
import json
import sys 
import random
from Card import Card,Deck

PORT=2022


JACK=11
QUEEN=12
KING=13
ACE=14


#JSON encoder utility class...
class JE(json.JSONEncoder):
    def default(self,obj):
        return obj.toJson()
    
#JSON dump utility function
def jdump(obj):
    return json.dumps(obj,cls=JE)


class Table:
    def __init__(self):
        #list of Client objects: Players at the table.
        #these are Tornado Client objects
        self.people = [None,None,None,None]
        
        #name of each client (strings)
        self.names = ["","","",""]
        
        #how many people are in people
        self.numPeople=0
        
        #cards played by each player
        self.played=[None,None,None,None]
        
        #number of non-None values in played
        self.numPlayed=0

        #who has the lead. Should be player to the left of dealer
        self.lead = 0
        
        #index of the next player to play
        self.nextToPlay=self.lead
        
        #cards left in hand
        self.cardsLeft=0
    
    def broadcast(self,msg,exceptFor=None):
        """ Broadcast a message to all players.
            Do not send message to player in exceptFor"""
        for p in self.people:
            if p and p != exceptFor:
                p.write_message(msg)
                
    def sitDown(self,client,D):
        """ Called when a client wants a seat at the table."""
        if self.numPeople == 4:
            print("Go away")
            return
        else:
            name = D["name"] 
            msg=jdump({"type":"newPlayer","name":name})
            self.broadcast(msg) 
            self.people[self.numPeople] = client 
            self.names[self.numPeople] = name
            print("Player",self.numPeople,"is",name)
            self.numPeople+=1
            if self.numPeople == 4:
                self.startHand()

    def playerSentMessage(self,player,msg):
        """ Called when a player sends a message to the server."""
        D = json.loads(msg)
        
        typ = D["type"]
        
        if typ == "sitDown":
            #player is sitting down at the table
            name = D["name"]
            self.sitDown(player,D)
            return
            
        playerIndex = self.people.index(player)
        
        if typ == "played":
            #player has played a card
            rank = D["rank"]
            suit = D["suit"]
            msg = jdump( {"type":"playMade","who":playerIndex,"rank":rank,"suit":suit})
            self.broadcast(msg,player)
            self.played[playerIndex] = Card(rank,suit)
            self.nextToPlay = (self.nextToPlay+1)%4
            self.numPlayed += 1
            if self.numPlayed == 4:
                self.turnTrick()
            else:
                self.getNextCardToPlay()
        else:
            print("Unexpected message:",D)
            
    def playerLeft(self,player):
        #player exited unexpectedly
        print("Player left. We cannot continue.")
        sys.exit(1)
        
    def startHand(self):
        #start a new hand: Deal the cards and tell the first player to go
        d = Deck()
        
        for i in range(4):
            #8 cards per player
            lst=[]
            for j in range(8):
                lst.append(d.deal())
                
            print("Deal cards to player",i,":",lst)
            
            self.people[i].write_message( jdump({ "type": "deal", "cards": lst }) )
            
        self.cardsLeft=8
        self.getNextCardToPlay()
        
    def getNextCardToPlay(self):
        #get the next card to play
        
        if self.numPlayed == 0:
            leadSuit=None
        else:
            leadSuit = self.played[self.lead].suit
            
        self.people[self.nextToPlay].write_message( 
            jdump({"type":"play","leadSuit":leadSuit}))
    
    def turnTrick(self):
        #determine who won the trick,
        #tell everyone,
        #set the new leader,
        #and ask for the next card.
        
        
        leadSuit = self.played[self.lead].suit
        winnerIndex = self.lead
        for i in range(4):
            
            i1 = (i+1)%4
            i2 = (i+2)%4
            i3 = (i+3)%4
            
            o1 = self.played[i].outranks(self.played[i1], leadSuit )
            o2 = self.played[i].outranks(self.played[i2], leadSuit )
            o3 = self.played[i].outranks(self.played[i3], leadSuit )
            if o1 and o2 and o3:
                winnerIndex=i
        
        
        self.broadcast( jdump({"type":"turned", "winner":winnerIndex}) )
        
        self.played=[None,None,None,None]
        self.numPlayed=0
        self.lead = winnerIndex
        self.nextToPlay=self.lead
        self.cardsLeft-=1
        if self.cardsLeft == 0:
            print("THE HAND IS OVER!")
        else:
            self.getNextCardToPlay()
            
theTable=Table()
        

class Client(tornado.websocket.WebSocketHandler):
    def __init__(self,*args):
        super().__init__(*args)
        self.myTable=None
        self.myName="anonymous"
    def open(self):
        print("OPEN")
    def on_message(self,msg):
        self.myTable = theTable
        self.myTable.playerSentMessage(self,msg)
    def on_close(self):
        print("CLOSE")
        self.myTable.playerLeft(self)
    def check_origin(self,o):
        return True 

if __name__ != "__main__":
    print("Spawning Tornado...")
    P = subprocess.Popen(
        [sys.executable, __file__]
    )
else:
    print("Starting tornado")
    eventloop = asyncio.new_event_loop()
    asyncio.set_event_loop(eventloop)
    app=tornado.web.Application(
        [
            ("/",Client)
        ]
    )
    app.listen(PORT)
    tornado.ioloop.IOLoop.instance().start()

    print("Server exiting")

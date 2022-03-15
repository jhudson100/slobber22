import random

JACK=11
QUEEN=12
KING=13
ACE=14


#ensure we always get the same sequence of cards for debugging.
#in production, we should seed the generator randomly
R = random.Random(42)

class Card:
    def __init__(self,rank,suit):
        self.rank=rank
        self.suit=suit
        assert suit in "CSHD"
        
    def toJson(self):
        return {"rank":self.rank,"suit":self.suit}
        
    def __repr__(self):
        sd = { 
            "C": "♣", "S": "♠", "H": "♥" , "D": "♦" 
        }
        r=["","","2","3","4","5","6","7","8","9","10","J","Q","K","A"]
        return f"{r[self.rank]}{sd[self.suit]}"
        
    def outranks(self,c2,ls):
        """ self = card 1
            c2 = card 2
            ls = lead suit
            Returns true if self outranks c2. """

        c1 = self

        assert ls in "CSHD"
        
        #if c1 does not match the lead suit,
        #it cannot outrank anything
        if c1.suit != ls:
            return False

        #if we get here, c1 matches the lead suit.

        #if c2 does not match the lead suit, c1 outranks it
        if c2.suit != ls:
            return True
            
        #if we get here, both c1 and c2 match the lead suit.

        #look at the rank.
        return c1.rank > c2.rank
     
class Deck:
    def __init__(self):
        self.lst=[]
        for r in range(7,ACE+1):
            for s in "CSHD":
                c = Card(r,s)
                self.lst.append(c)
        R.shuffle(self.lst)
    def deal(self):
        return self.lst.pop()
                

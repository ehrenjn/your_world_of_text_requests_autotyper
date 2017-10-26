import socket as s
import time
import random

#YOU CAN'T SEND ANY CHARS THAT HAVE AN ord() HIGER THEN 127 FOR SOME REASON
#YOU ALSO CAN'T SEEM TO SEND ANY DOUBLE QUOTES (") BUT SINGLE QUOTES WORK (')

#basically just follows this http://puu.sh/ww9Nj/80d799e914.png and makes sure you have a mask
    #https://tools.ietf.org/html/rfc6455 <-check for info on everything websockets (including the masking algor)
##THIS IS ALL SORT OF POINTLESS BECAUSE THE FOLLWOING JS:
    #Permissions.can_paste = function() {return true;};
#ENABLES PASTING SO YOU CAN JUST PASTE WHATEVER YOU WANT
#BUT THIS IS WAY FASTER THEN PASTING


class websocket():
    def __init__(self, world = ''):
        if world != '':
            world += '/'
        self.world = world
        self.sock = s.socket()
        self.sock.settimeout(4)
        self.charsSent = 0 #keeps track of how many chars has been sent by the socket, need this to make ywotData()
        self.handshake()
    def handshake(self):
        headers = "GET ws://www.yourworldoftext.com/" + self.world + """ws/ HTTP/1.1
Host: www.yourworldoftext.com
Connection: Upgrade
Pragma: no-cache
Cache-Control: no-cache
Upgrade: websocket
Origin: http://www.yourworldoftext.com
Sec-WebSocket-Version: 13
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36
Accept-Encoding: gzip, deflate, sdch
Accept-Language: en-GB,en-US;q=0.8,en;q=0.6
Cookie: __cfduid=d5a558db0c400424789f651c42a912d691498517424; __uvt=; uvts=6C5FtrkWPdEl7Jnl; __utma=23997618.903236636.1498517427.1498585998.1498589791.7; __utmc=23997618; __utmz=23997618.1498517427.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); csrftoken=OeskqVvh30KBDLuFG0d8IhCdszRWkIUUb4MH8Ms4vLZXYob4mgeUDKIXRhVM5M2n
Sec-WebSocket-Key: MhGzNuGQsB8i48P9vqEnTQ==
Sec-WebSocket-Extensions: permessage-deflate; client_max_window_bits\n\n""".replace('\n','\r\n') #dumping all my headers here just incase it matters
        self.sock.connect(('www.yourworldoftext.com', 80)) #Did you know that port 80 is for http and port 443 is for https?
        self.sock.send(headers)
        print self.recv() #gets http response
        print self.recv() #gets a websocket response
    def recv(self):
        try:
            return self.sock.recv(999999)
        except:
            return "No Response"
    def send(self, data):
        message = websocketFrame(data).message
        self.sock.send(message)
    def post(self, majorXY, minorXY, chars): #an example of a message to post is: '{"kind":"write","edits":[[0,3,0,0,1498587168398,"a",1]]}'
        data = ywotData(self, majorXY, minorXY, chars).data
        print 'sending ' + str(len(data)) + ' bytes'
        self.send(data)
    def close(self):
        self.sock.close()


class websocketFrame(): #ALL INFO ON HOW TO DO THIS IS IN SECTION 5 OF https://tools.ietf.org/html/rfc6455
    def __init__(self, data):
        messageType = '\x81' #\x81 is 10000001 which means that the following message is ascii
        dataLength = self.lengthBytes(data)
        mask = self.genMask() #mask basically encrypts data
        maskedData = self.masked(data, mask)
        self.message = messageType + dataLength + mask + maskedData
    def lengthBytes(self, data):
        length = len(data)
        lenBytes = ''
        firstByte = 128 #+128 BECUASE THE MASK BIT MUST BE SET TO 1 (mask bit is first bit of first length byte)
        if length < 126: #if the length is less then 126 then the length is data is stored in the same byte as the mask bit
            firstByte += length
        elif length >= 126 and length < 65536: #if the length is more then 126 then there are 3 length bytes, the first has the masked bit AND IS SET TO 126 TO SAY THAT ITS THE NEXT 2 BYTES THAT CONTAIN THE LENGTH and the next 2 represent the length as a 16 bit unsigned int
            firstByte += 126
            lenBytes += self.encodeAsNBitInt(length, 16)
        elif length >= 65536: #if the len is really fucking big then theres 9 length bytes, agian the first has the masked bit PLUS 127 TO INDICATE THAT THE LENGTH IS SAVED IN THE NEXT 8 BYTES and the next 8 are an unsigned 64 bit int
            firstByte += 127
            lenBytes += self.encodeAsNBitInt(length, 64)
        return chr(firstByte) + lenBytes
    def encodeAsNBitInt(self, num, n):
        binary = bin(num).replace('b','')
        binary = '0' * (n - len(binary)) + binary
        return ''.join(map(lambda b: chr(int(b, 2)), [binary[i:i+8] for i in range(0, n, 8)]))
    def genMask(self):
        mask = ''
        for i in range(4):
            mask += chr(int(random.random()*250))
        print [mask]
        return mask
    def masked(self, data, mask): #MASKING ALGORYTHM IS DESCRIBED IN SECTION 5.3 OF https://tools.ietf.org/html/rfc6455
        output = ''
        for i in range(len(data)):
            dataByte = ord(data[i]) #char to byte
            maskByte = ord(mask[i%4])
            newByte = dataByte ^ maskByte
            output += chr(newByte)
        return output


class ywotData(): #an example of a message to post is: '{"kind":"write","edits":[[-1,0,6,5,1498719388413,"a",1],[-1,0,6,6,1498719388430,"b",2]]}'
    def __init__(self, websock, initialMajorXY, initialMinorXY, text):
        assert len(text.replace('\n','')) <= 200 #YWOT DOESN'T LET YOU SEND MORE THEN 200 CHARACTERS PER FRAME
        timestamp = int(time.time()*1000) - len(text)
        data = ''
        self.majorXY = list(initialMajorXY)
        self.minorXY = list(initialMinorXY)
        for c in range(len(text)):
            if text[c] == '\n': #move down a line
                self.increaseCoord(1)
                self.majorXY[0] = initialMajorXY[0] #have to reset x coords
                self.minorXY[0] = initialMinorXY[0]
            else: #write a char
                websock.charsSent += 1
                info = [self.majorXY[1], self.majorXY[0], self.minorXY[1], self.minorXY[0], 'TIMESTAMP_GOES_HERE', 'CHAR_GO_HERE', websock.charsSent]
                info = str(info).replace("'CHAR_GO_HERE'", '"' + text[c] + '"')
                info = info.replace("'TIMESTAMP_GOES_HERE'", str(timestamp+c))
                data += info + ','
                self.increaseCoord(0)
        data = data[:-1] #removes the last comma
        self.data = '{"kind":"write","edits":[' + data + ']}'
    def increaseCoord(self, dimension): #minor grid is 16x8 I guess
        if self.minorXY[dimension] == 15 and dimension == 0:
            self.minorXY[0] = 0
            self.majorXY[0] += 1
        elif self.minorXY[dimension] == 7 and dimension == 1:
            self.minorXY[1] = 0
            self.majorXY[1] += 1
        else:
            self.minorXY[dimension] += 1



if __name__ == '__main__': #example, spams "@winningpodcast" on the main world a bunch
    import time
    le = websocket()
    for i in range(30):
        time.sleep(1)
        le.post((1,-1), (0,0), '\n'*(i+1) + '@winningpodcast '*10)
        print le.recv()
    le.close()
    

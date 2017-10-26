# your_world_of_text_requests_autotyper
Posts to http://www.yourworldoftext.com/ extremely quickly using requests


Unfortunately "extremely quickly" only means ~200 bytes/second, however this is still much faster than pasting. 
You may only send up to 200 bytes per message and if you post messages too quickly from one IP you will be banned for about 5 minutes. I've found that a one second sleep between messages prevents the site detecting it as spam. I also found that it was possible to temporarily get away with times between messages as low as 0.5 seconds, but after posting a few times at that rate I was banned.

**Warning: THIS LIBRARY IS INCOMPLETE BUT STILL USABLE. yourworldoftext will often try to switch websockets which will result in your websocket becoming useless and having to start a new one. This happens more frequently if you post slowly (slower then once a second) but will happen to every websocket eventually. At 1 post/second I can usually post at least a hundred times before I get disconnected.
Creating a websocket will also fail sometimes. If the first line that websocket() prints is "HTTP/1.1 403 Access denied" then the websocket has failed to make a connection.**

#### Usage

    sock = websocket(world)

Creates a new websocket that sends data to the yourworldoftext world specified by _world_ (a string). If there is no world specified the world variable defaults to "", which posts to the main world.

    sock.post(majorXY, minorXY, chars)

Posts the string _chars_ starting in the location specified by _majorXY_ and _minorXY_. 
Can only post a maximum of 200 characters (not including newline characters ('\n')).

The yourworldoftext grid is actually a grid of smaller grids. Each smaller grid is 16x16 characters wide. The larger grid is a grid of these smaller grids and is (theoretically) infinitely wide. 

minorXY and majorXY are both tuples. _minorXY_ is the xy position of the beginning of chars in the small grid. _majorXY_ is the xy position of the small grid in the large grid.

    sock.recv()
    
Retrieves the latest response to your post. If there is no response to retrieve then "No response" is returned. If yourworldoftext has closed the websocket on their end then you will receive either a 0 byte response, an http response that says "400 Bad Request" somewhere, or just no response at all.

    sock.close()

Closes the connection to yourworldoftext. 


#### Example

    from ywot import websocket
	import time

	#creates a new websocket on the world "bottesting"
	s = websocket("bottesting")
	#posts 2 lines of text
	s.post((1,-1), (0,0), "test post line 1\ntest post line 2")
	#you should wait a second before posting agian
	time.sleep(1)
	#post another line of text underneath the first two
	s.post((1,-1), (0,2), "test number 2")
	#prints the data gotten back from yourworldoftext
	print s.recv()
	#closes connection
	s.close()

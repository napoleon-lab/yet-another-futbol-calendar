from @/sources/futbol.py 

Store the data files in the data/footbal directory with the format <day>-promedios.json

Run every 30 minutes a function that will update the games data for the 30 days from today. Also, it should check that the old files (> 3 months) are deleted.

The update functionality should ensure that we do not get blocked from the API. For that only a single call is allowed every 1 + random (0, 30) minutes. The update strategy should ensure that close events (<= 2 days) are updated every 6 hours and far away events (> 1 week) can be updated every 24 hours. If you decide to use the files as way to store the events, then a way of checking if you need to update a event day is checking the last modification time of the file.

Create a HTTP server with endpoints of build information, health check, also add access logs (time + endpoint + resopnse status + response time) with rotation with max keep of 1 week

Serve the games for each league as a iCalendar thourgh the http server, each event is the teams of the game Team 1 vs Team 2, start is start_time and description include the tv network
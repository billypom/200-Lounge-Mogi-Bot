# 200 Lounge Bot

Automated mogi bot for MK8DX 200cc Lounge. Enter mogis, submit tables, update mmr, see stats, and more.


# Commands

# `/verify` +1 REQUIRED `http://mariokartcentral.com/`

The MK8DX competitive scene is tied to Mario Kart Central. Verify your MKC identity (registry or forum link) with this command to participate in mogis.

# `/c`

"Can up" for a mogi. (Join the queue)

# `/d`

Drop from a mogi (Leave the queue)

# `/l`

List players in the mogi (See the queue)

# `/esn`

Ends the current mogi, Starts a New mogi

# `/fc` +1 (optional) `XXXX-XXXX-XXXX`

Upload your Friend Code. | Submitting your FC means you are willing and able to host. If FCs are available - the bot will choose a player at random to host a mogi, once the room reaches 12 players.


# `/table` +2 REQUIRED `format` & `scores`

Submit a table. Provide a format (1, 2, 3, 4, 6) and a list of 12 players & 12 scores (brandon 180 popuko 12 jpgiviner 42 etc...). The best way to ensure that the table is submitted properly is to copy the example from the MOGI STARTED message. All players on a team MUST be grouped together in the submission.

# `/teams`

See the teams in the ongoing mogi (must be sent from a tier channel)

# `/mmr`

Displays your MMR and rank. Useful for returning players.

# `/stats` +3 (optional) `#tier-channel` `@player` `last`

Displays player statistics. 

Filter by tier (#tier-a, #tier-b, ...)

Filter by player (@popuko, @brandon, ...)

Filter by last `x` mogis played (last 10, last 100, last 5, ...)

# `/name` +1 REQUIRED `new name`

Submit a name-change request to staff.

# `/strikes`

Displayers your strikes

# `/twitch` +1 REQUIRED `username`

Upload your twitch username to be added to the automated #mogi-media channel. If you are in an ongoing mogi, and streaming, the bot will recognize that and post your stream in #mogi-media
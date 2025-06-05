import flask_server
import discord_bot


flask_options = {'host': '0.0.0.0'}
discord_bot.main()
flask_server.main(**flask_options)
this project was born out of my annoyance with groupme and a couple friends' stubborn refusal to switch the group chat to a channel in our discord server. this project ended because groupme broke certain functionality that i used, and then the group decided to move to a platform other than discord anyway.

this project is very unfinished. i don't have any intention at the moment to continue to work on the  fixes or additional features i had planned because i dont use groupme for anything anymore and gm is honestly too trash for me to care enough, but my notes on those features are below if someday i (or you!) want to flesh this out.

this is a quick, custom-for-my-use-case modification of code from [this](https://github.com/jerbob/groupme-discord) archived repo that i slapped together in 2022 then didn't touch again til fall 2024 which is when it fell apart entirely.  
credit and thank you to [jerbob](https://github.com/jerbob) for the initial repo and starting point

urls and tokens and whatnot have been redacted for obvious reasons

# discord groupme sync

uses a small webserver, a groupme bot, and a discord bot + webhook to sync messages between a discord channel and a groupme chat

## what it needs

a discord bot and a webhook for the channel (https://discord.com/developers/docs/quick-start/overview-of-apps), (https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)

a groupme bot linked to the chat (https://dev.groupme.com/tutorials/bots) i recommend the web form over the API

a URL for the webserver that the groupme bot can post to

## what it does

when a message is posted in the groupme chat, the groupme bot sends that message object to the webserver which then reformats and sends it to the discord webhook. the discord webhook then posts the message to the discord channel, using the groupme user's username & profile picture from the message object

when a message is posted in the discord channel, the discord bot reformats and sends the message object to the groupme bot, which posts the message into the groupme chat. 

## how it works

the groupme bot is configured with a callback URL that it sends message objects to whenever something is sent in the chat - this needs to be the URL that the flask webserver is exposed to (i used ngrok, this turned out to be a huge issue, more on that below). any groupme message received by the webserver that *wasnt* sent by the bot itself is then reformatted for the discord webhook such that the discord webhook will assume the username and pfp of the groupme user who sent the message and will attach an image or video to the message if one was sent (only one image/video gets attached even if multiple were sent, another issue). this webserver exists and does the message reformatting because the groupme bot itself can't, it simply sends messages in the chat that are posted to it, and posts messages sent in the chat to its callback URL

in the other direction, the discord bot itself reformats messages sent in the discord channel. it supports up to 3 image attachments in one message (not really an issue, mainly laziness) and posts the message body directly to the groupme bot. there's no way to edit the groupme bot's name or profile picture on a per-message basis, this can only be done through the groupme dev web interface.

# fixable issues

## ngrok callback URLs

in fall 2024, groupme banned the use of ngrok urls in a groupme bot's callback URL. because this code runs flask locally and i was using ngrok to tunnel into it, this entirely broke the groupme-to-discord direction. this can obviously be fixed by using any number of different ways to get traffic to flask

## image/video attachments

image and video attachments are very much hardcoded in this. these issues (let's be honests, the "issue" is laziness) can be fixed with proper loops and filtering in the groupme-to-discord direction and proper loops, filtering, and object building in the discord-to-groupme direction. 

for the groupme-to-discord direction: there is an `attachments` array for every message object, each attachment has a `type`. currently the code just checks for the first object's `type` and in the case that it's an image, it appends its `url` to the message body. this can lead to lots of issues obviously, some of which though stem from the fact that in groupme messages, many things are considered attachments, including user mentions, stickers, or an object indicating that the message is a reply to another message. in these cases, any attached image is most likely not the first element. obvious solution here is to loop through `attachments` and filter for images & videos, tack on their `url`s to a string, then add that string to the message body.

in the discord-to-groupme direction: discord messages also have an `attachments` array. the current code is limited to 3 image attachments per message - it loops through `attachments` and checks to see if something is an image by means of checking its file extension. groupme messages only accept images hosted on groupme's image hosting platform, so the code uploads each image it finds to that and adds each resulting `finalurl` to a list. depending on the length of the list, these are then grabbed in a seriously awful manner during the actual message formatting process. solution here is to do a better job of passing and formatting these `finalurl`s in the post to the groupme bot

# abandoned features

## cross-platform mentions & cross-platform replies

both of these are *technically* possible but potentially annoying to implement. a centralized store of group chat user data needs to exist mapping each discord user ID to a groupme user ID with those mapped to their discord display name and groupme user name. the IDs never change but the user names can, so those would likely need to be updated by hand every time as I don't think there's a way to make the discord bot listen for that and there's certainly no way to make the groupme bot listen for that.

in the event of mentions or replies, the parts of the code that reformat messages for other platforms would need to do some quick lookups against that object and build the proper mention/reply objects based on the mapping of that discord user ID is the groupme user name, or vice versa. i think this would have been a very cool feature, since as it stands now you won't get a proper mention notification if someone mentions you or replies to your groupme message in discord (or the other way around).

# limitations

obviously these are two different platforms with two different sets of features that are incompatible with each other. groupme bots can do very little - most other discord features wouldn't be translatable

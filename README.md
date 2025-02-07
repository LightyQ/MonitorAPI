# Getting Started

Requirements needed

```
pip install aiohttp
pip install beautifulsoup4
pip install aiofiles
```
# API-MONITOR

**Disclaimer** : This is a re-made version of [Devorkk's](https://github.com/devorkk) original Monitor-API old project, so all credits belongs to Devork respectively.

**About** : A simple monitor API written in python, able to monitor all existing posts in game using [KoGaMa's Feed API](https://www.kogama.com/api/feed/0/) and sending the data to a discord webhook, The content varies depending on the latest post ID existing in the website and so it goes on.

# Showcase

[Check out the showcase](https://www.youtube.com/watch?v=v-nv_ZVDSb0&ab_)

# Capability 
The script is only capable of tracking the following data :
* Wall posts
* Purchases
* Games published
* Badges earned
* Usernames Changed

# Safety And How To Use

**LAST_ID Issues** : Sometimes the the LAST_ID.txt file cannot keep going on it own due to specific problems and this can a bit complex if using a host since it can end up doing a loop starting from the last ID you printed

**How to get the Post ID ?** : The post ID can be easily obtained through the [Feed API](https://www.kogama.com/api/feed/0/)
![How to](https://cdn.discordapp.com/attachments/1264627993477906584/1327998417703665746/Test.jpg?ex=67a76167&is=67a60fe7&hm=e05852bf9ca40c6fc06d1d0fc42c8b65b5305adbd5a0c63771a3bdaa9e6dab42&)

**Mandatory Note** : You must make a post and then copy its ID using the feed API and then paste it to the LAST_ID.txt, if done correct, you'll be on track with the latest feeds being posted

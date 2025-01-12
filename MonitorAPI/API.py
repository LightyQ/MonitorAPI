import asyncio
import json
import re
from datetime import datetime
from urllib.parse import quote, unquote
import aiohttp
from aiohttp import web
from bs4 import BeautifulSoup
import aiofiles

def remove_markdown(string):
    return re.sub(r'[\*_~`>\\]', r'\\\g<0>', string).replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')

def format_entities(string):
    is_visible = 'Unnamed' if string.strip() == '' else string
    soup = BeautifulSoup(f"<html><body>{is_visible}</body></html>", "html.parser")
    return soup.body.get_text()

def format_image(url):
    default_links = [
        'd12755047758464d8115cdfcf3c2a1f6', '0e4459cad3d74a21b1db0ab5654c8e58', 'd12755047758464d8115cdfcf3c2a1f6',
        '98ebac5ea0e042ca8521363a2756b2fb', '8b28b5efb0b24dedab68092914ed056b', '560098edf9d946f7a365e1ff7ebd62d9',
        '31de51b2344b4f599bdd1b4fe2752647', '42238de716a446938dc7e9f732db71a2', '7eee4cab3fed4b86b70f1400055d3276',
        '8ba6e8c66fe64f07ac8c7fd92571bbc9', 'f681cb4afc9344e9ad18578501792b8e', '65cd3a3fb6274ddeb322e3dce5336502',
        '9dbd95fccf3349a6a4d4c6999a99a358', 'fc2aeb396744467abb0daa722b24d768', '7619a517cdb8433fb54dedecc3efc09b',
        '538168d7a8eb4a86b65a573b8a0ee511', '71cb75544bae4f218210c640ac349108', '9ae82e1ec96043b2bb65837a84f0637a',
        '4ad3748a3c8d4464856cb29b91b0c14d', '14848111-8879-4b85-b294-d3480deb5165', '9995d208-9996-4230-80ee-46cac638bfda'
    ]

    last_part = url.split('_')[-1].split('.')[0]
    first_part = url.replace(f"_{last_part}", '').replace('.jpg', '.png')
    result = 'https:' + url

    if 'avatar_images' in url:
        result = 'https:' + first_part
    elif any(str in url for str in default_links):
        return result
    else:
        if 'placeholder' not in url:
            result = 'https:' + first_part
        if 'cache' in url:
            result = result.replace('cache', 'images')
    return result

def get_date(date):
    return datetime.fromisoformat(date).strftime('%a, %d %b %Y %H:%M:%S %Z')

async def send_fetch(url, content):
    async with aiohttp.ClientSession() as session:
        await session.post(url, json=content)

CONFIG = {
    'NAME': 'API Monitor',
    'SERVER': 'https://www.kogama.com', 
    'COLOR': 16219718, #Hex demical color
    'AVATAR': 'https://play-lh.googleusercontent.com/Oq0WGvSCr_I2c0TWNPSjYv_VjMOjhbEQoH6gwRXnR1Pn6jz2VRn6TpzrTuLIJ5pnkPBR',
    'POST': 'Your_Discord_Webhook_URL',
    'WALL_POST': 'Your_Discord_Webhook_URL',
    'MARKETPLACE': 'Your_Discord_Webhook_URL',
    'BADGES': 'Your_Discord_Webhook_URL',
    'GAMES': 'Your_Discord_Webhook_URL',
    'USERNAME_URL': 'Your_Discord_Webhook_URL',
}

LAST_ID = None

async def get_last_id():
    global LAST_ID
    async with aiofiles.open('last_id.txt', mode='r') as f:
        LAST_ID = int(await f.read())

    while True:
        api = f"{CONFIG['SERVER']}/api/feed/0/{LAST_ID}/"

        async with aiohttp.ClientSession() as session:
            async with session.get(api) as response:
                if response.status == 200:
                    json_data = await response.json()
                    if json_data:
                        handle_data(json_data['data'])
                        LAST_ID += 1
                        async with aiofiles.open('last_id.txt', mode='w') as f:
                            await f.write(str(LAST_ID))
                else:
                    await asyncio.sleep(1)

async def send_post(data):
    name = data['profile_username']
    id = data['profile_id']
    created = data['created']
    message = json.loads(data['_data'])['status_message']
    profile_image = data['profile_images']['large']

    embed = {
        'title': remove_markdown(name),
        'description': LAST_ID,
        'url': f"{CONFIG['SERVER']}/profile/{id}/",
        'color': CONFIG['COLOR'],
        'author': {'name': '#' + f"{abs(29760166 - LAST_ID):,}"},
        'fields': [{'name': 'Has posted:', 'value': format_entities(message)}],
        'footer': {'text': get_date(created)},
        'thumbnail': {'url': format_image(profile_image)},
    }

    payload = {
        'avatar_url': CONFIG['AVATAR'],
        'content': None,
        'embeds': [embed],
        'username': CONFIG['NAME'],
        'allowedMentions': {'parse': []}
    }

    await send_fetch(CONFIG['POST'], payload)

async def send_wall_post(data):
    name = data['profile_username']
    id = data['profile_id']
    created = data['created']
    other_id = data['other_profile_id']
    other_name = data['other_username']
    message = json.loads(data['_data'])['status_message']
    profile_image = data['profile_images']['large']

    embed = {
        'title': remove_markdown(name),
        'description': LAST_ID,
        'url': f"{CONFIG['SERVER']}/profile/{id}/",
        'color': CONFIG['COLOR'],
        'author': {'name': '#' + f"{abs(29760166 - LAST_ID):,}"},
        'fields': [
            {'name': 'Has wall-posted:', 'value': '\n'},
            {'name': 'From:', 'value': f"[{remove_markdown(name)}]({CONFIG['SERVER']}/profile/{id}/)"},
            {'name': 'To:', 'value': f"[{remove_markdown(other_name)}]({CONFIG['SERVER']}/profile/{other_id}/)"},
            {'name': 'Message:', 'value': format_entities(message)}
        ],
        'footer': {'text': get_date(created)},
        'thumbnail': {'url': format_image(profile_image)}
    }

    payload = {
        'avatar_url': CONFIG['AVATAR'],
        'content': None,
        'embeds': [embed],
        'username': CONFIG['NAME'],
        'allowedMentions': {'parse': []}
    }

    await send_fetch(CONFIG['WALL_POST'], payload)

async def send_badge(data):
    name = data['profile_username']
    id = data['profile_id']
    created = data['created']
    badge_image = data['badge_images']['large']
    badge_name = data['badge_name']

    embed = {
        'title': remove_markdown(name),
        'description': LAST_ID,
        'url': f"{CONFIG['SERVER']}/profile/{id}/",
        'color': CONFIG['COLOR'],
        'author': {'name': '#' + f"{abs(29760166 - LAST_ID):,}"},
        'fields': [{'name': 'Earned a badge:', 'value': badge_name}],
        'footer': {'text': get_date(created)},
        'thumbnail': {'url': format_image(badge_image)}
    }

    payload = {
        'avatar_url': CONFIG['AVATAR'],
        'content': None,
        'embeds': [embed],
        'username': CONFIG['NAME'],
        'allowedMentions': {'parse': []}
    }

    await send_fetch(CONFIG['BADGES'], payload)

async def send_shop(data):
    name = data['profile_username']
    id = data['profile_id']
    created = data['created']
    creator_id = json.loads(data['_data'])['creditor_profile_id']
    creator_name = json.loads(data['_data'])['creditor_username']
    product_name = json.loads(data['_data'])['product_name']
    product_id = json.loads(data['_data'])['product_id']
    avatar_image = data['avatar_images']['large']

    embed = {
        'title': remove_markdown(name),
        'description': LAST_ID,
        'url': f"{CONFIG['SERVER']}/profile/{id}/",
        'color': CONFIG['COLOR'],
        'author': {'name': '#' + f"{abs(29760166 - LAST_ID):,}"},
        'fields': [
            {'name': 'Has purchased an avatar:', 'value': '\n'},
            {'name': 'Creator:', 'value': f"[{remove_markdown(creator_name)}]({CONFIG['SERVER']}/profile/{creator_id}/)"},
            {'name': 'Product:', 'value': f"[{format_entities(product_name)}]({CONFIG['SERVER']}/marketplace/avatar/{product_id}/)"}
        ],
        'footer': {'text': get_date(created)},
        'image': {'url': format_image(avatar_image)}
    }

    payload = {
        'avatar_url': CONFIG['AVATAR'],
        'content': None,
        'embeds': [embed],
        'username': CONFIG['NAME'],
        'allowedMentions': {'parse': []}
    }

    await send_fetch(CONFIG['MARKETPLACE'], payload)

async def send_game(data):
    id = data['profile_id']
    name = data['profile_username']
    planet_name = data['planet_name']
    planet_id = data['planet_id']
    created = data['created']
    planet_image = data['planet_images']['large']
    profile_image = data['profile_images']['large']

    embed = {
        'title': remove_markdown(name),
        'description': LAST_ID,
        'url': f"{CONFIG['SERVER']}/profile/{id}/",
        'color': CONFIG['COLOR'],
        'author': {'name': '#' + f"{abs(29760166 - LAST_ID):,}"},
        'fields': [{'name': 'Has published a game:', 'value': f"[{format_entities(planet_name)}]({CONFIG['SERVER']}/games/play/{planet_id}/)"}],
        'footer': {'text': get_date(created)},
        'image': {'url': format_image(planet_image)},
        'thumbnail': {'url': format_image(profile_image)}
    }

    payload = {
        'avatar_url': CONFIG['AVATAR'],
        'content': None,
        'embeds': [embed],
        'username': CONFIG['NAME'],
        'allowedMentions': {'parse': []}
    }

    await send_fetch(CONFIG['GAMES'], payload)

# Function to send a username change notification
async def send_username(data):
    name = data['profile_username']
    id = data['profile_id']
    created = data['created']
    new_name = json.loads(data['_data'])['username_new']
    old_name = json.loads(data['_data'])['username_old']
    profile_image = data['profile_images']['large']

    payload = {
        'avatar_url': CONFIG['AVATAR'],
        'content': None,
        'embeds': [
            {
                'title': remove_markdown(name),
                'description': LAST_ID,
                'url': f"{CONFIG['SERVER']}/profile/{id}/",
                'color': CONFIG['COLOR'],
                'author': {'name': '#' + f"{abs(29760166 - LAST_ID):,}"},
                'fields': [
                    {'name': 'Name has been changed:', 'value': '\n'},
                    {'name': 'Old:', 'value': format_entities(old_name)},
                    {'name': 'New:', 'value': format_entities(new_name)}
                ],
                'footer': {'text': get_date(created)},
                'thumbnail': {'url': format_image(profile_image)}
            }
        ],
        'username': CONFIG['NAME'],
        'allowedMentions': {'parse': []}
    }

    await send_fetch(CONFIG['USERNAME_URL'], payload)

def handle_data(data):
    feed_type = data['feed_type']
    if feed_type == 'status_updated':
        asyncio.create_task(send_post(data))
    elif feed_type == 'wall_post':
        asyncio.create_task(send_wall_post(data))
    elif feed_type == 'game_published':
        asyncio.create_task(send_game(data))
    elif feed_type == 'marketplace_buy':
        asyncio.create_task(send_shop(data))
    elif feed_type == 'badge_earned':
        asyncio.create_task(send_badge(data))
    elif feed_type == 'username_updated':
        asyncio.create_task(send_username(data))

async def start_server():
    app = web.Application()
    app.router.add_get('/', lambda request: web.Response(text='Alive'))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()

async def main():
    await asyncio.gather(get_last_id(), start_server())

# Run the main function
asyncio.run(main())
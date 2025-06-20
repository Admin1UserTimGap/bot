import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import asyncio
import threading
import os

DATA = {
    "prefix": "!",
    "token file": "role_token.txt",
    "ROLES": {
    }
}

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

BOT = commands.Bot(command_prefix=DATA["prefix"], intents=intents, help_command=None)

@BOT.event
async def on_ready():
    print("Ролебот вже тут і готовий! \n")
    print(f"Він під'єднався як {BOT.user}")

async def _managerole(rolename, uid, action):
    try:
        user = await BOT.fetch_user(uid)
        if user is None:
            return "error"
            
        guild = None
        for g in BOT.guilds:
            member = g.get_member(uid)
            if member:
                guild = g
                user = member
                break
        
        if guild is None:
            return "error"

        ident = DATA["ROLES"].get(rolename)
        if ident is None:
            return "error"

        rl = guild.get_role(ident)
        if rl is None:
            return "error"

        if action == "add":
            if rl not in user.roles:
                await user.add_roles(rl)
            return "success"
        elif action == "remove":
            if rl in user.roles:
                await user.remove_roles(rl)
            return "success"
        else:
            return "error"

    except Exception as e:
        return "error"

def encodemessageback(msg):
    return msg[0].upper()

def decodemessage(msg):
    action=""
    role=""
    uid = int(msg[4:])

    if msg[0]=="R":
        action="remove"
    elif msg[0]=="A":
        action="add"
    else:
        return None, None, None
    
    roles=DATA["ROLES"]
    key=""
    for x in range(1, 4):
        key+=msg[x]
    
    key=key.lower()
    
    for element in roles.keys():
        if element.lower()[0:3]==key:
            fr = element
            break
        
    return fr, action, uid

app = Flask(__name__)

@app.route("/", methods=["POST"])
async def recreq():
    if not request.is_json:
        return jsonify(status=encodemessageback("error")), 400

    data = request.get_json()
    enc = data.get("message")

    if not enc:
        return jsonify(status=encodemessageback("error")), 400

    r, a, u = decodemessage(enc)

    if r is None or a is None or u is None:
        return jsonify(status=encodemessageback("error")), 400

    loop = BOT.loop if BOT.loop else asyncio.get_event_loop()
    s = await asyncio.run_coroutine_threadsafe(
        _managerole(r, u, a), loop
    ).result()

    return jsonify(status=encodemessageback(s))

def _activate():
    with open(DATA["token file"],"r") as file:
        token=file.read().strip()
    if not token:
        print("ПОМИЛКА ТОКЕНА: Токен не існує")
        return
    try:
        BOT.run(token)
    except discord.errors.LoginFailure as e:
        print(f"ПОМИЛКА ТОКЕНА: Токен неправильний: {e}")
    except Exception as e:
        pass

def _flactivate():
    port = os.environ.get("PORT", 5000)
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    flaskt = threading.Thread(target=_flactivate())
    flaskt.start()

    _activate()

import discord
import re
import time
import os
from flask import Flask, jsonify
from threading import Thread

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")  # Must be set in Railway env vars
CHANNEL_ID = 1400497545532276746  # Your Discord channel ID

app = Flask(__name__)
pet_servers = []

def parse_pet_embed(embed):
    name = mutation = dps = tier = jobId = placeId = None

    for field in embed.fields:
        if "Name" in field.name:
            name = field.value.strip()
        elif "Mutation" in field.name:
            mutation = field.value.strip()
        elif "Money" in field.name or "Per Sec" in field.name:
            dps = field.value.strip()
        elif "JOBID" in field.name:
            jobId = field.value.strip()
        elif "Join Script" in field.name:
            m = re.search(r'TeleportToPlaceInstance\((\d+),\s*"([\w-]+)', field.value)
            if m:
                placeId = m.group(1)
            else:
                placeId = None

    if name and jobId and placeId:
        return {
            "name": name,
            "mutation": mutation or "",
            "dps": dps or "",
            "jobId": jobId,
            "placeId": placeId,
            "timestamp": discord.utils.utcnow().timestamp(),
        }
    return None

class PetClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self, message):
        if message.channel.id != CHANNEL_ID:
            return

        for embed in message.embeds:
            pet = parse_pet_embed(embed)
            if pet:
                if not any(p["jobId"] == pet["jobId"] and p["name"] == pet["name"] for p in pet_servers):
                    pet_servers.append(pet)
                    print(f"Added pet: {pet['name']} {pet['jobId']}")
                if len(pet_servers) > 20:
                    pet_servers.pop(0)
                break

@app.route('/recent-pets')
def recent_pets():
    now = time.time()
    filtered = [p for p in pet_servers if now - p["timestamp"] < 900]
    return jsonify(filtered)

def run_flask():
    port = int(os.environ.get("PORT", 8080))  # Railway provides PORT dynamically
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    intents = discord.Intents.default()
    intents.message_content = True
    client = PetClient(intents=intents)
    client.run(DISCORD_TOKEN)

const { Client, Intents } = require('discord.js');

const CHANNEL_ID = '1400497545532276746'; // Your Discord channel ID as a string
const DISCORD_TOKEN = process.env.DISCORD_TOKEN; // Set on Railway environment variables

const client = new Client({
  intents: [
    Intents.FLAGS.GUILDS,
    Intents.FLAGS.GUILD_MESSAGES,
  ],
});

client.once('ready', () => {
  console.log(`Logged in as ${client.user.tag}!`);
});

client.on('messageCreate', (message) => {
  if (!message.channel || !message.channel.id) return;

  if (message.channel.id !== CHANNEL_ID) return;

  // Your bot logic here
  console.log(`Message from monitored channel: ${message.content}`);
});

client.login(DISCORD_TOKEN);

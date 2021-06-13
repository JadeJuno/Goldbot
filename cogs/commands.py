import asyncio
from collections import deque
import random
import string
import sys
import traceback
from datetime import datetime, timedelta

import discord
import wikipedia
from discord.ext import commands, tasks
from googletrans import Translator, LANGUAGES
from iso639 import languages

import googlesearch
from bot import config, embed_template, is_bot_owner
from morsecode import MorseCode

status_list = ['My default prefix is g!.', "If I break, contact Gølder06#7041.", 'To see my commands, type g!help.']

command_list = ['8ball', 'ban', 'binary', 'choose', 'clear', 'coinflip', 'detect', 'diceroll', 'flip', 'flipcoin', 'google',
				'googleit', 'googlesearch', 'help', 'kick', 'langlist', 'language', 'languagelist', 'morse',
				'morsecode', 'pin', 'ping', 'prefix', 'roll', 'rolldice', 'say', 'translate', 'unban', 'wikipedia']

change_loop_interval = random.randint(1, 90)


def get_dict_key(dictionary, value):
	key_list = list(dictionary.keys())
	value_list = list(dictionary.values())
	for listed_value in value_list:
		if listed_value == value:
			return key_list[value_list.index(value)]
	return value


def get_emoji_list(emojis):
	return_list = list(emojis)
	for i in range(len(return_list)):
		for j in range(i + 1, len(return_list)):
			if return_list[i].name > return_list[j].name:
				return_list[i], return_list[j] = return_list[j], return_list[i]
	return return_list


class Commands(commands.Cog):
	def __init__(self, client):
		self.activity = None
		self.client = client
		self.log = None
		self.loop_interval = None
		self.morse = MorseCode()
		self.my_guild = None
		self.owner = None
		self.translator = Translator()
		self.lang_dict = LANGUAGES
		self.emoji_list = None

	@tasks.loop(minutes=change_loop_interval)
	async def change_status_task(self):
		global change_loop_interval
		self.activity = random.choice(status_list)
		await self.client.change_presence(status=discord.Status.online, activity=discord.Game(self.activity))
		time_now = datetime.now()
		print(f'Status changed to "{self.activity}" ({time_now.strftime("%H:%M")}).')
		change_loop_interval = random.randint(1, 90)
		print(
			f"Next status change in {change_loop_interval} minutes ({(time_now + timedelta(minutes=change_loop_interval)).strftime('%H:%M')}).")

	@commands.Cog.listener()
	async def on_ready(self):
		self.log = self.client.get_channel(config["log_channel"])
		self.owner = await self.client.fetch_user(config["owners_id"][0])
		self.my_guild = self.client.get_guild(config["guild_id"])
		self.emoji_list = get_emoji_list(self.my_guild.emojis)
		print(f'Bot is ready.')
		print(f"bot created by {self.owner.name}.")
		await self.log.send("Bot Started.")
		self.change_status_task.start()

	@commands.Cog.listener()
	async def on_command(self, ctx):
		# Function only used for testing purposes. DO NOT USE!
		# (I'd delete it, but I feel like I'll need it one day...)
		"""
		if ctx.message.channel.guild != self.my_guild:
			await self.log.send(f"{ctx.message.channel.guild.name}:\n{ctx.message.author}: {ctx.message.content}")
			print(f"{ctx.message.channel.guild.name}:\n{ctx.message.author}: {ctx.message.content}")
		"""

	@commands.command(name='8ball')
	async def _8ball(self, ctx, *, question):
		ball_predicts = ["It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.",
						 "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.",
						 "Signs point to yes.", "Reply hazy, try again.", "Ask again later.",
						 "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
						 "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.",
						 "Very doubtful."]
		if "?" in question:
			if "love" in question.lower():
				prediction = random.choice(ball_predicts[-5:])
			else:
				prediction = random.choice(ball_predicts)
		else:
			prediction = "That's not a question..."
		await ctx.send(f'Question: {question}\nThe ***:8ball:BALL*** says: {prediction}.')

	@commands.command()
	async def choose(self, ctx, *, options):
		divided_options = options.split(",")
		if len(divided_options) >= 2:
			for option in divided_options:
				if not option:
					divided_options.pop(option)
			await ctx.send(f'Gøldbot chooses: `{random.choice(divided_options).strip()}`.')
		else:
			await ctx.send(
				f'I can\'t just choose between {len(divided_options)} choice. *(to divide the choices you should put a comma between them)*.')

	@commands.command(aliases=["coinflip", "flipcoin"])
	async def flip(self, ctx):
		await ctx.send(f"-Flip!-\nIt landed on {random.choice(['heads', 'tails'])}!")

	@commands.command(aliases=["rolldice", "diceroll", "dice"])
	async def roll(self, ctx, faces=6.0):
		if random.choices([True, False], [100, 1])[0]:
			if type(faces) is float and faces != int(faces):
				await ctx.send(
					f"Error: You can't roll a die with a non-whole amout of faces, you {faces} dimensional being!")
				return
			if faces > 2:
				try:
					faces = int(faces)
				except ValueError:
					await ctx.send("Error: You can't roll a die with a non-numeric amount of faces...")
				result = random.randint(1, faces)
				if faces <= 6:
					emoji = self.emoji_list[result - 1]
				else:
					emoji = result
				await ctx.send(f"Rolled a d{faces}.\nIt landed on **{emoji}**!")
			elif faces == 2:
				await ctx.send(f"... A 2 sided die is a coin... Use the `{ctx.prefix}`flip command.")
			elif faces <= 1:
				await ctx.send("... You serious?")
		else:
			# This right here is why you don't allow me to code while sick =)
			with open('=).gif', 'rb') as f:
				img = discord.File(f)
			await ctx.send("Rick. \n~~haha get it it's a rickroll lmfaooooooo-~~", file=img)

	@roll.error
	async def roll_error(self, ctx, error):
		if isinstance(error, commands.BadArgument):
			await ctx.send("Error: You can't roll a die with a non-numeric amount of faces...")

	@commands.command()
	async def say(self, ctx, message, channel=None):
		if channel is None:
			channel = ctx.channel
		else:
			if channel.startswith("<#"):
				channel = self.client.get_channel(int(channel.strip("<>")[1:]))
			else:
				channel = discord.utils.get(ctx.guild.text_channels, name=channel)
		if channel is None:
			await ctx.send("Error: Channel doesn't exist")
			return
		if message.lower().startswith("i am") or message.lower().startswith("i'm"):
			if "stupid" in message.lower():
				message = f"{ctx.author.mention} is stupid."
			elif "dumb" in message.lower():
				message = f"{ctx.author.mention} is dumb."
		await discord.Message.delete(ctx.message, delay=0)
		await channel.send(message)

	@commands.command(aliases=["googleit", "googlesearch"])
	async def google(self, ctx, *, search_request):
		message = await ctx.send(f"Searching for `{search_request}`...")
		i = 1
		output_str = ""
		for url in googlesearch.search(search_request, stop=10):
			if i < 10:
				output_str += f"`{i}.`   **[{url.title}](<{url.link}>)**\n"
			else:
				output_str += f"`{i}.` **[{url.title}](<{url.link}>)**\n"
			i += 1
		if i == 1:
			output_str = "**No results found.**"
		embed = embed_template(ctx, "Google", output_str[0:-1],
							   icon="https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/1200px-Google_%22G%22_Logo.svg.png")
		await message.edit(content=None, embed=embed)

	@commands.command(aliases=["detect", "language"])
	async def lang_detect(self, ctx, *, user_message):
		detected_lang = self.translator.detect(user_message).lang
		if isinstance(detected_lang, list):
			detected_lang = detected_lang[self.translator.detect(user_message).confidence.index(max(self.translator.detect(user_message).confidence))]
		await ctx.send(
			f'"{user_message}" is in {languages.get(alpha2=detected_lang).name} (Certainty: `{int(max(self.translator.detect(user_message).confidence) * 100)}%`).')

	@commands.command(aliases=["morsecode", "morse"])
	async def morse_code(self, ctx, encrypt_decrypt, *, sentence):
		disc = encrypt_decrypt
		var = self.morse.check_letter(sentence.upper())
		if not var:
			await ctx.send("Error: Invalid character detected.")
			return
		code = f"{sentence} "
		error_message = f"Error: You tried to {disc} an already {disc}ed message or you entered an invalid character."
		if disc == "encrypt":
			try:
				code = code[0:-1]
				output = self.morse.encrypt(code.upper())
			except KeyError:
				output = error_message
			except Exception as e:
				print(e)
				return
		elif disc == "decrypt":
			code = code.replace('_', '-')
			try:
				output = self.morse.decrypt(code).lower()
			except ValueError:
				output = error_message
		else:
			output = "Error: Invalid discriminator."
		await ctx.send(output.capitalize())

	@commands.command()
	async def ping(self, ctx):
		await ctx.send(f':ping_pong: Pong! {round(self.client.latency * 1000)}ms.')

	@commands.command()
	async def translate(self, ctx, translate_message, destination_language='en', source_language=None):
		destination_language = destination_language.lower()
		destination_language = get_dict_key(self.lang_dict, destination_language)
		if source_language is not None:
			source_language = source_language.lower()
			source_language = get_dict_key(self.lang_dict, source_language)
		else:
			source_language = self.translator.detect(translate_message).lang
			if isinstance(source_language, list):
				source_language = source_language[0]
		translated_text = self.translator.translate(translate_message, src=source_language,
													dest=destination_language).text.replace("`", "\`")
		try:
			await ctx.send(
				f'Translated from {self.lang_dict[source_language].capitalize()} to {self.lang_dict[destination_language].capitalize()}\n`{translated_text.capitalize()}`.')
		except ValueError:
			await ctx.send(f"Error: Invalid language.")

	@commands.command()
	async def wikipedia(self, ctx, *, search_request):
		title = "Wikipedia"
		description = ""
		image = "https://i.imgur.com/7kT1Ydo.png"
		try:
			result = wikipedia.page(search_request)
			description = f"[{result.title}]({result.url})\n{result.summary}"
			image = result.images[0]
		except wikipedia.exceptions.DisambiguationError as e:
			i = 1
			for option in e.options[:9]:
				i += 1
				disamb_result = wikipedia.page(option, auto_suggest=False)
				if disamb_result.url != "":
					result_2 = f"[{disamb_result.title}]({disamb_result.url})"
				else:
					result_2 = f"{disamb_result} **URL Not Found**"
				description += f"`{i}`: {result_2}\n"
		except wikipedia.exceptions.PageError:
			description = "Page not found."
		embed = embed_template(ctx, title, description, image=image, icon="https://i.imgur.com/FD1pauH.png")
		await ctx.send(embed=embed)

	@commands.has_permissions(manage_messages=True)
	@commands.command()
	async def clear(self, ctx, amount: int):
		await ctx.message.delete()
		await ctx.channel.purge(limit=amount)
		clear_message = await ctx.send(f'Cleared {amount} messages.')
		await asyncio.sleep(2)
		await clear_message.delete()

	@commands.has_permissions(ban_members=True)
	@commands.command()
	async def ban(self, ctx, member: discord.Member, *, reason=None):
		await member.ban(reason=reason)
		await ctx.send(f'{member} banned via {ctx.prefix}ban command. Reason: {reason}.')

	@commands.has_permissions(kick_members=True)
	@commands.command()
	async def kick(self, ctx, member: discord.Member, *, reason=None):
		await member.kick(reason=reason)
		await ctx.send(f'{member} kicked via {ctx.prefix}kick command. Reason: {reason}.')

	@commands.has_permissions(manage_messages=True)
	@commands.command()
	async def pin(self, ctx):
		messages = await ctx.history(limit=2).flatten()
		messages.remove(ctx.message)
		await messages[0].pin()

	@commands.command()
	async def caesar(self, ctx, shift, encrypt_decrypt: str, *, sentence):
		try:
			int(shift)
		except ValueError:
			await ctx.send('Error: Shift no good (PH)')
		for char in sentence:
			if char in string.digits:
				await ctx.send('Error: no, frick you (PH)')
				return
		alphabet_upper = deque(list(string.ascii_uppercase))
		alphabet_lower = deque(list(string.ascii_lowercase))
		shift_upper = alphabet_upper
		shift_upper.rotate(shift)
		shift_lower = alphabet_lower
		shift_lower.rotate(shift)
		if encrypt_decrypt.lower() == 'encrypt':
			pass
		await ctx.send()

	@commands.command()
	async def binary(self, ctx, encode_decode: str, *, sentence):
		if encode_decode.lower() == "encode":
			s = ''.join(format(ord(i), '08b') for x, i in enumerate(sentence))
			bin_list = [s[i:i + 8] for i in range(0, len(s), 8)]
			output = ''
			for _bin in bin_list:
				output += f'{_bin} '
			output = output[:-1]
			await ctx.send(f"Here\'s your encoded string: \n`{output}`")
		elif encode_decode.lower() == 'decode':
			for char in sentence:
				if char not in ['0', '1', ' ']:
					await ctx.send("Please only use 1s and 0s.")
					return
			try:
				int(sentence)
			except ValueError:
				bin_list = sentence.split()
			else:
				bin_list = [sentence[i:i + 8] for i in range(0, len(sentence), 8)]

			output = ''
			for _bin in bin_list:
				output += chr(int(_bin, 2))
			await ctx.send(f"Here\'s your decoded binary code: \n`{output}`")
			return
		else:
			await ctx.send('ERROR: Invalid discriminator.')
			return

	@commands.has_permissions(ban_members=True)
	@commands.command()
	async def unban(self, ctx, *, member):
		banned_users = await ctx.guild.bans()
		member_name, member_discriminator = member.split('#')
		for ban_entry in banned_users:
			user = ban_entry.user
			if (user.name, user.discriminator) == (member_name, member_discriminator):
				await ctx.guild.unban(user)
				await ctx.send(f'Unbanned {user.mention}.')
				return
			await ctx.send(f'{user.mention} is not banned.')

	@commands.check(is_bot_owner)
	@commands.command()
	async def error_handling(self, ctx):
		await ctx.send(0 / 0)

	@commands.check(is_bot_owner)
	@commands.command()
	async def test(self, ctx):
		gold_emoji = self.emoji_list[0]
		print("TEST")
		embed = discord.Embed(title="Title", description=f"{gold_emoji}[Test Link](https://www.youtube.com)",
							  color=random.randint(0, 0xffffff), url="https://www.google.com/")
		embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
		embed.set_footer(text=f"*Requested by {ctx.author.name}.*", icon_url=ctx.author.avatar_url)
		embed.set_image(url="https://discordpy.readthedocs.io/en/latest/_images/snake.png")
		embed.set_thumbnail(url="https://i.imgur.com/8bOl5gU.png")
		embed.add_field(name="Field 1", value="value 1")
		embed.add_field(name="Field 2", value="value 2")
		embed.add_field(name="Field 3", value="value 3")
		await ctx.send(embed=embed)
		try:
			int(1)
		except Exception as e:
			exc_info = sys.exc_info()
			track = traceback.format_exception(*exc_info)
			print(track)
			await ctx.send(f"An exception has ocurred: {e}.")

	@commands.check(is_bot_owner)
	@commands.command()
	async def auto_error(self, ctx):
		await ctx.send(f"{int('A')}")


def setup(client):
	client.add_cog(Commands(client))

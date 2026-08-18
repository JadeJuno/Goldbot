import random
import re
import typing
from urllib import parse as urlparse

import aiohttp
import discord
from discord.ext import commands

from libs import botutils


class Fun(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		botutils.log("Fun Cog ready!")

	@commands.command(
		name='8ball',
		description="You can ask a yes or no question to the Magic :8ball: Ball, and it will answer it.",
		extras={'example': 'Am I loved?'}
	)
	async def _8ball(self, ctx: commands.Context, *, question: str):
		ball_predicts = ("It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.",
						 "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.",
						 "Signs point to yes.", "Reply hazy, try again.", "Ask again later.",
						 "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
						 "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.",
						 "Very doubtful.")
		if "love" in question.lower():  # lol
			ball_predicts = ball_predicts[-5:]
		if question.endswith("?"):
			if question == "?":
				prediction = "That's not a question, that's a question sign..."
			else:
				prediction = random.choice(ball_predicts)
		else:
			prediction = "That's not a question..."
		await ctx.send(f'Question: {question}\nThe ***:8ball:BALL*** says: {prediction}')

	@commands.command(
		aliases=('colour',),
		description="Sends an image with a solid color specified in Hexadecimal Code.",
		extras={"example": "#32A852"}
	)
	async def color(self, ctx: commands.Context, hex_color: str):
		hex_color = hex_color.upper().replace('#', '')
		pattern = re.compile(r"^[A-Fa-f\d]{6}$", re.IGNORECASE)
		if not re.search(pattern, hex_color):
			await botutils.error_template(ctx, f"`#{hex_color}` is not a valid Hex Color code.")
			return
		img = f"https://dummyimage.com/300/{hex_color}/&text=+"
		embed = botutils.embed_template(footer=f'#{hex_color}', color=int(hex_color, 16), image=img)
		await ctx.send(embed=embed)

	@commands.command(
		alias=("choice",),
		description="Give me some options **(More than 1)** and I will randomly choose between them.",
		extras={
			"signature": "<Option1 Option2 Option3 (...)>",
			"example":   "Yes No Perhaps"
		}
	)
	async def choose(self, ctx: commands.Context, *options: str):
		if len(options) < 2:
			await ctx.send("I can't just choose between 1 choice.")
			return
		await ctx.send(f"{self.bot.user.name} chooses: `{random.choice(options).strip()}`.")

	@commands.command(
		aliases=("coinflip", "flipcoin", "coin"),
		description="Flip a coin and see if it lands on heads or tails."
	)
	async def flip(self, ctx: commands.Context):
		await ctx.send(f"-Flip!-\nIt landed on {random.choice(('heads', 'tails'))}!")

	@commands.command(
		aliases=("rolldice", "diceroll", "dice"),
		description="Roll a die with X number of faces *(6 by default)*.",
		extras={
			'example':   "20",
			"signature": "[Sides=6]"
		}
	)
	async def roll(self, ctx: commands.Context, faces: float = 6.0):
		try:
			if faces != int(faces):
				await botutils.error_template(ctx,
											  f"You can't roll a die with a non-whole amout of faces, you {faces}-dimensional being!")
				return
		except OverflowError:
			await botutils.error_template(ctx, "You can't roll an infinite dice!")
			return

		emojis = self.bot.get_guild(botutils.config["guild_id"]).emojis
		if faces > 2:
			faces = int(faces)

			result = random.randint(1, faces)
			if faces <= 6:
				result = discord.utils.get(emojis, name=f"Dice{result}")
			await ctx.send(f"Rolled a d{faces}.\nIt landed on **{result}**!")
		elif faces == 2:
			await ctx.send(f"... A 2 sided die is a coin... Use the `{ctx.prefix}flip` command.")
		else:
			await ctx.send("... You serious?")

	@roll.error
	async def roll_error(self, ctx: commands.Context, error: Exception):
		if isinstance(error, commands.BadArgument):
			await botutils.error_template(ctx, "You can't roll a die with a non-numeric amount of faces...")

	@commands.command(
		description="Send a message with the text you wrote and deletes your message. If the channel is set, it'll send the message to said channel.",
		extras={
			"example": "#general Hi, my name is Junøbot and I'm sentient."
		}
	)
	async def say(self, ctx: commands.Context, files: botutils.GreedyAttachments,
				  channel: typing.Optional[discord.TextChannel], *, message: str):
		if channel is None:
			channel = ctx.channel
			author = ctx.author
		else:
			author = channel.guild.get_member(ctx.author.id)

		files = [await file.to_file(spoiler=file.is_spoiler()) for file in files]

		if not channel.permissions_for(author).send_messages:
			await botutils.error_template(ctx, f"You don't have permissions to talk in {channel.mention}")
			return

		await ctx.message.delete()
		await channel.send(message, files=files)

	@commands.command(
		aliases=('skin',),
		description="Sends the Minecraft skin of a user you give.",
		extras={
			"example": "Dinnerbone"
		}
	)
	async def namemc(self, ctx: commands.Context, username: str):
		try:
			name, uuid = await self.get_mc_user(username)
		except ValueError:
			await botutils.error_template(ctx, f'There\'s no Minecraft user called "{username}"')
			return

		embed = botutils.embed_template(title=name, url=f"https://namemc.com/profile/{name}",
										image=f"https://minotar.net/armor/body/{uuid}.png",
										icon=f"https://minotar.net/avatar/{uuid}.png",
										footer="Powered by https://minotar.net")

		await ctx.send(embed=embed)

	@staticmethod
	async def get_mc_user(name: str) -> tuple[str, str]:
		name = urlparse.quote(name)
		async with aiohttp.ClientSession() as session:
			async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{name}") as mc_request:
				if mc_request.status == 200:
					d = await mc_request.json()
					return d['name'], d['id']
				else:
					raise ValueError


async def setup(bot: commands.Bot):
	await bot.add_cog(Fun(bot), override=True)

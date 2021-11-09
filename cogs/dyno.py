import googletrans
from discord.ext import commands
from googletrans import Translator

import bot
from config import parse_config

config = parse_config("./config.toml")


def is_in_command(ctx):
	return ctx.channel.id == 843834879736283156 or ctx.author.id in config["origins_mods"]


class Commands(commands.Cog):
	def __init__(self, client):
		self.activity = None
		self.client = client
		self.log = None
		self.loop_interval = None
		self.my_guild = None
		self.translator = Translator()
		self.lang_dict = googletrans.LANGUAGES
		self.emoji_list = None

	@commands.check(bot.is_in_origin_server)
	@commands.command(aliases=("vanillaorigins",))
	async def baseorigins(self, ctx):
		await bot.tryreply(ctx, "https://discord.com/channels/734127708488859831/749571272635187342/894472367315759154")

	@commands.check(bot.is_in_origin_server)
	@commands.command()
	async def template(self, ctx):
		if is_in_command(ctx):
			await bot.tryreply(ctx, "**Datapack Template**\nThere's a nice template for data-packs which you can use, made by CandyCaneCazoo. This way, you'll know you have the folder structure correct from the start!\nhttps://discord.com/channels/734127708488859831/749571272635187342/867715782825476137", reply=True)
		else:
			serious = self.client.get_emoji(821796259333537813)
			await ctx.reply(f"Please use your commands in <#843834879736283156>, so the other channels don't get messy! {serious}")

	@commands.check(bot.is_in_origin_server)
	@commands.command()
	async def namespace(self, ctx):
		await bot.tryreply(ctx, "The namespace and the ID should only contain the following symbols:\n\n• `0123456789` Numbers\n• `abcdefghijklmnopqrstuvwxyz` Lowercase letters\n• `_` Underscore\n• `-` Hypen/minus\n• `.` Dot\n\n\nFor example:\n\n`data/Example namespace` is invalid because it has an uppercased letter and a space, whilst `data/example-namespace` is valid.\n\n\nFor more information, visit the official wiki page about namespaces: <https://minecraft.fandom.com/wiki/Namespaced_ID>")

	@commands.check(bot.is_in_origin_server)
	@commands.command(aliases=('redirect-datapack-dev',))
	async def rdd(self, ctx):
		await bot.tryreply(ctx, "If you need help with a datapack-related issue, feel free to ask in <#810587422303584286> **by creating a thread**!\n\ne.g:")


def setup(client):
	client.add_cog(Commands(client))
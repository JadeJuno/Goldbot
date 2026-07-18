import calendar
import io
import json
import random
import typing
from copy import copy

import discord
from discord.ext import commands

from libs import botutils
from libs.prefix import PrefixParser


class DevCog(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.log = None
		botutils.log("Dev Cog ready!")

	async def cog_check(self, ctx: commands.Context):
		check = await self.bot.is_owner(ctx.author)
		if not check:
			raise commands.NotOwner
		return check

	@commands.command()
	@commands.guild_only()
	async def sync(self, ctx: commands.Context, guilds: commands.Greedy[discord.Object],
				   spec: typing.Optional[typing.Literal["~", "*", "^"]] = None):
		tree = self.bot.tree

		if not guilds:
			if spec == "~":
				synced = await tree.sync(guild=ctx.guild)
			elif spec == "*":
				tree.copy_global_to(guild=ctx.guild)
				synced = await tree.sync(guild=ctx.guild)
			elif spec == "^":
				tree.clear_commands(guild=ctx.guild)
				await tree.sync(guild=ctx.guild)
				synced = []
			else:
				synced = await tree.sync()

			await ctx.send(
				f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
			)
			return

		ret = 0
		for guild in guilds:
			try:
				await tree.sync(guild=guild)
			except discord.HTTPException:
				pass
			else:
				ret += 1

		await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

	@commands.command(name='cog')
	async def coghandle(self, ctx: commands.Context, disc: typing.Literal['load', 'unload', 'reload', 'list'],
						cog: typing.Optional[str]):

		if cog:
			cogs = (f'cogs.{cog}',)
		else:
			cogs = botutils.config['default_cogs']

		done_cogs = []
		match disc.lower():
			case 'load':
				msg = await ctx.send(f'Loading...')
				for cog in cogs:
					try:
						await self.bot.load_extension(cog)
						done_cogs.append(cog)
					except commands.errors.ExtensionAlreadyLoaded:
						pass
				if len(done_cogs) > 0:
					await msg.edit(content="Loading complete!")
				else:
					await msg.edit(content="Error: Cog(s) already loaded.")

			case 'unload':
				msg = await ctx.send(f'Unloading...')
				for cog in cogs:
					if cog == "cogs.dev":
						continue
					try:
						await self.bot.unload_extension(cog)
						botutils.log(f'{cog} Unloaded.')
						done_cogs.append(cog)
					except commands.errors.ExtensionNotLoaded:
						pass
				if len(done_cogs) > 0:
					await msg.edit(content="Unloading complete!")
				else:
					await msg.edit(content="Error: Cog(s) already unloaded.")

			case 'reload':
				msg = await ctx.send(f'Reloading...')
				for cog in cogs:
					try:
						await self.bot.reload_extension(cog)
					except commands.errors.ExtensionNotLoaded:
						pass
					else:
						botutils.log(f'{cog} Reloaded.')
						done_cogs.append(cog)
				if len(done_cogs) > 0:
					await msg.edit(content="Reloading complete!")
				else:
					await msg.edit(content="Error: Cog(s) was/were all unloaded.")
			case 'list':
				output = '\n'.join(self.bot.cogs.keys())
				await ctx.send(f"Here's all the loaded cogs: \n{output}")
			case _:
				await ctx.send("Error: Disc not valid.")

	@commands.command()
	async def test(self, ctx: commands.Context):
		print("TEST")
		embed = discord.Embed(title="Title", description="[Test Link](https://www.youtube.com)",
							  color=random.randint(0, 0xffffff), url="https://www.google.com/")
		embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
		embed.set_footer(text=f"*Requested by {ctx.author.name}.*", icon_url=ctx.author.display_avatar.url)
		embed.set_image(url="https://discordpy.readthedocs.io/en/stable/_images/snake_dark.svg")
		embed.set_thumbnail(url="https://file.garden/ZC2FWku7QDnuPZmT/Junobot%20Thumbnail.png")
		embed.add_field(name="Field 1", value="value 1")
		embed.add_field(name="Field 2", value="value 2")
		embed.add_field(name="Field 3", value="value 3")
		await ctx.send(embed=embed)
		emb_json = json.dumps(embed.to_dict(), indent='\t', ensure_ascii=False)
		await ctx.send(f"```json\n{emb_json}\n```")
		await ctx.send(f"<t:{int(calendar.timegm(ctx.message.created_at.utctimetuple()))}>")
		await botutils.tryreply(ctx, "Test")

	@commands.command(aliases=('autoerror',))
	async def auto_error(self, ctx: commands.Context):
		await ctx.send(f"{int('A')}")

	"""
	@commands.command()
	async def banreport(self, _, user: discord.Member):
		ban_list = self.bot.get_channel(920775229008142356)
		await ban_list.send(str(user.id))
		await self.log.send(f"You've banned {user} from reporting bugs.")
	"""

	@commands.command()
	async def format(self, ctx: commands.Context):
		if ctx.message.reference:
			if len(ctx.message.reference.resolved.embeds) == 0:
				output = ctx.message.reference.resolved.content
			else:
				output = ctx.message.reference.resolved.embeds[0].description
			with io.StringIO(output) as file:
				# noinspection PyTypeChecker
				await ctx.send("Here's the formatted message:",
							   file=discord.File(fp=file, filename=f'{ctx.message.id}.txt'))

	@commands.command()
	async def help_test(self, ctx: commands.Context):
		await ctx.send("Help Tested.")

	@commands.command()
	async def get_embed(self, ctx: commands.Context):
		try:
			reply = ctx.message.reference.resolved
		except AttributeError:
			await botutils.tryreply(ctx, "You're not replying to anything")
			return

		if len(reply.embeds):
			await ctx.send(
				"\n\n".join([f"```json\n{json.dumps(embed.to_dict(), indent=4)}\n```" for embed in reply.embeds]))

	@commands.group(invoke_without_command=True)
	async def prefixes(self, ctx: commands.Context, *, failed_subcmd):
		await botutils.no_subcommand_error(ctx, failed_subcmd)

	@prefixes.command(name='get')
	async def prefixes_get(self, ctx: commands.Context):
		prefixes = self.bot.command_prefix.prefixes
		servers = [self.bot.get_guild(server) for server in prefixes.keys()]
		prefix_zip = zip(servers, prefixes.items())

		s = "\n".join(f"`{server} [{server_id}]` - `{prefix}`" for server, (server_id, prefix) in prefix_zip)
		await ctx.send(s)

	@prefixes.command(name='update')
	async def prefixes_update(self, ctx: commands.Context):
		prefix_handler: PrefixParser = self.bot.command_prefix

		# This should add a prefix to every guild, if it didn't have one already.
		for guild in self.bot.guilds:
			_ = prefix_handler[guild.id]

		for guild_id in copy(prefix_handler.prefixes).keys():
			guild_id = guild_id
			guild = self.bot.get_guild(guild_id)

			if guild is None:
				prefix_handler.remove(guild_id)

		await ctx.send("Done!")


async def setup(bot):
	await bot.add_cog(DevCog(bot), override=True)

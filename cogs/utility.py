import typing

import discord
from discord.ext import commands

from libs import botutils
from libs.botutils import embed_template


class Utility(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		botutils.log("Utility Cog ready!")

	@commands.command(description="Sends a link to invite me to another server.")
	async def invite(self, ctx: commands.Context):
		invite_url = discord.utils.oauth_url(self.bot.user.id)
		emb = embed_template(title="Invite Link",
							 description=f"Here's the invite link for {self.bot.user.name}: [Invite]({invite_url})")
		await ctx.send(embed=emb)

	@commands.command(description="Sends a link to my Source Code")
	async def source(self, ctx: commands.Context):
		emb = embed_template(title="Source Code",
							 description="My source code is public, and you can find it [here](https://github.com/JadeJuno/Junobot)!")
		await ctx.send(embed=emb)

	@commands.check(botutils.is_not_report_banned)
	@commands.command(
		aliases=('bugreport', 'reportbug', 'bug-report', 'report-bug'),
		description="Let's you make a direct bug report to my creator if needed. Allows for sending images and other attachments as well.",
		extras={
			'example': 'The "j!translate" command is broken.'
		}
	)
	async def report(self, ctx: commands.Context, files: botutils.GreedyAttachments, *, message: str):
		report_channel = self.bot.get_channel(920770517424816179)

		attachments = [await attachment.to_file(spoiler=attachment.is_spoiler())
					   for attachment in files]

		embed = embed_template(title=f"{ctx.author}",
							   description=f">>> {message}", footer=f"User ID: {ctx.author.id}",
							   icon=ctx.author.display_avatar.url)

		owner_ping = self.bot.get_user(self.bot.owner_id).mention
		await report_channel.send(f'{owner_ping}\nReported from "{ctx.guild.name}" ({ctx.guild.id}):', embed=embed,
								  files=attachments)
		await ctx.send("Bug Report sent successfully")

	@commands.command(description='Sends "Pong!" and my latency.')
	async def ping(self, ctx: commands.Context):
		await ctx.send(f':ping_pong: Pong! {self.bot.latency * 1000:.0f}ms.')

	@commands.guild_only()
	@commands.command(
		extras={'example': 'j-', 'signature': '[New Prefix/"reset"]'},
		description="Changes the server's prefix to the specified prefix. If blank, it'll show the current server's prefix instead. If is \"reset\", it'll reset the prefix to the default (`j!`)"
	)
	async def prefix(self, ctx: commands.Context, new_prefix: typing.Optional[str]):
		if new_prefix:
			if ctx.author.guild_permissions.administrator:
				guild_id = ctx.guild.id
				if new_prefix.lower() == "reset":
					self.bot.command_prefix.remove(guild_id)
					await ctx.send(f"Prefix reset back to `{self.bot.command_prefix.default}`.")
				else:
					self.bot.command_prefix.update(guild_id, new_prefix)
					await ctx.send(f"Prefix changed to `{new_prefix}`.")
			else:
				raise commands.MissingPermissions(missing_permissions=['administrator'])
		else:
			await ctx.send(f"Server's prefix currently set to `{ctx.prefix}`.")


async def setup(bot: commands.Bot):
	await bot.add_cog(Utility(bot), override=True)

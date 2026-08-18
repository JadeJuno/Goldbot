import difflib
import os
import re
import tomllib
import typing
from argparse import ArgumentParser
from datetime import datetime
from typing import Optional
from warnings import deprecated

import discord
from discord.ext import commands
from dotenv import load_dotenv


def parse_config(path: str):
	with open(path, 'rb') as f:
		return tomllib.load(f)


config = parse_config("config.toml")

GreedyAttachments = commands.Greedy[discord.Attachment]


@deprecated("Will use interaction buttons in the future instead.")
async def reaction_decision(bot: commands.Bot, ctx: commands.Context, check_str: str) -> bool:
	check_message = await ctx.send(check_str)
	await check_message.add_reaction("\U00002705")
	await check_message.add_reaction("\U0000274c")

	def check(reaction_checked, reaction_user):
		user_check = reaction_user == ctx.author or reaction_user.guild_permissions.administrator and ctx.author.bot
		return user_check and reaction_checked.message == check_message and str(reaction_checked.emoji) in (
			"\U00002705", "\U0000274c")

	reaction, user = await bot.wait_for('reaction_add', check=check)
	if str(reaction.emoji) == "\U00002705":
		return True
	elif str(reaction.emoji) == "\U0000274c":
		return False
	return False


async def is_not_report_banned(ctx: commands.Context) -> bool:
	return bool(ctx)  # Just to avoid PyCharm's warning temporarily :p


def check_if_self_hosted(argparser: ArgumentParser) -> bool:
	load_dotenv()

	mode = argparser.parse_args().mode
	self_host = False
	if mode == 'full':
		self_host = False
	elif mode == 'dev':
		self_host = True

	self_host = "DEV_TOKEN" in os.environ and self_host

	return self_host


def embed_template(title: str = "", description: str = "", url: str = "", footer: str = "", image: str = "",
				   icon: str = "", color: Optional[discord.Color | int] = None) -> discord.Embed:
	if color is None:
		color = discord.Color.random()

	if description:
		embed = discord.Embed(description=description, color=color)
	else:
		embed = discord.Embed(color=color)

	if title:
		if icon:
			embed.set_author(name=title, icon_url=icon, url=url)
		else:
			embed.title = title
			embed.url = url

	if footer:
		embed.set_footer(text=footer, icon_url="https://file.garden/ZC2FWku7QDnuPZmT/Junobot%20Icon%20(No%20Text).png")

	embed.set_thumbnail(url="https://file.garden/ZC2FWku7QDnuPZmT/Junobot%20Thumbnail.png")

	if image:
		embed.set_image(url=image)

	return embed


async def error_template(ctx, message: str, error_type: typing.Literal['ERROR', 'WARNING', 'INFO'] = "ERROR",
						 send: bool = True) -> discord.Embed | None:
	ERROR_TYPES = {"ERROR": 0xFF0000, "WARNING": 0xFFFF00, "INFO": 0x00FF00}

	embed = embed_template(error_type, description=message, color=ERROR_TYPES[error_type])
	if send:
		await ctx.reply(embed=embed)
	else:
		return embed


async def tryreply(ctx: commands.Context, message: str, reply: bool = False, mention: bool = True) -> discord.Message:
	async with ctx.typing():
		try:
			return await ctx.message.reference.resolved.reply(message, mention_author=mention)
		except AttributeError:
			if reply:
				return await ctx.reply(message, mention_author=mention)
			else:
				return await ctx.send(message)


def get_param(param: commands.Parameter) -> str:
	return param.name.replace("_", " ").capitalize().strip()


def humanized_join(l: list, last: str = "or"):
	last = last.strip()
	return f"{', '.join(l[:-1])} {last} {l[-1]}"


async def no_subcommand_error(ctx: commands.Context, failed_subcmd: typing.Optional[str] = None):
	cmds = [cmd.name for cmd in ctx.command.commands]

	if failed_subcmd is not None:
		matches = difflib.get_close_matches(failed_subcmd, cmds, n=1)
		try:
			await error_template(ctx, f'Subcommand "{failed_subcmd}" not found, did you mean "{matches[0]}"?')
		except IndexError:
			await error_template(ctx, f'Subcommand "{failed_subcmd}" not found.')
	else:
		subcommands_str = humanized_join(list(map(lambda cmd: f'"{cmd}"', cmds)))
		await error_template(ctx, f'Missing subcommand. Expected {subcommands_str}.')


def make_bug_report_file(ctx: commands.Context) -> str:
	arguments = []

	for arg in ctx.args[2:]:
		arg_type = str(type(arg))
		arg_type = re.search("'(.*?)'", arg_type).group(1)
		arguments.append(f'"{arg_type} - {arg}"')

	for kw_key, kw_val in ctx.kwargs.items():
		arg_type = str(type(kw_val))
		arg_type = re.search("'(.*?)'", arg_type).group(1)
		arguments.append(f'"[{arg_type.capitalize()}] - {kw_key}: {kw_val}"')

	if len(arguments) > 0:
		args_str = ', '.join(arguments)
	else:
		args_str = '"None"'

	if not isinstance(ctx.channel, discord.DMChannel):
		channel = f"#{ctx.channel.name} ({ctx.channel.id})"
		guild = f"{ctx.guild.name} ({ctx.guild.id})"
	else:
		channel = "None [DM]"
		guild = channel

	content = f'''Author: @{ctx.author} ({ctx.author.id})
	Channel: {channel}
	Guild: {guild}
	Arguments: {args_str}
	
	Message: "{ctx.message.content}"
	'''

	return content


def to_timescale(argument: str) -> Optional[str]:
	TIMESCALES = {
		's': 'seconds', 'second': 'seconds',
		'm': 'minutes', 'minute': 'minutes',
		'h': 'hours', 'hour': 'hours',
		'd': 'days', 'day': 'days',
		'w': 'weeks', 'week': 'weeks'
	}

	argument = argument.lower()
	if argument in TIMESCALES.values():
		return argument
	else:
		try:
			return TIMESCALES[argument]
		except KeyError:
			raise commands.BadArgument


def wip_command():
	async def predicate(ctx: commands.Context) -> Optional[bool]:
		if not await ctx.bot.is_owner(ctx.author):
			raise WIPCommandError
		return True

	return commands.check(predicate)


def under_maintenance(reason: str):
	async def predicate(ctx: commands.Context) -> Optional[bool]:
		if not await ctx.bot.is_owner(ctx.author):
			raise CommandUnderMaintenanceError(reason)
		return True

	return commands.check(predicate)


def log(*args, sep=' ', end='\n', file=None):
	# TODO: Learn how real logging works. (It's getting later and later to do this by the minute...)
	now = datetime.now().strftime("%H:%M:%S")
	print(f"[{now}]:", *args, sep=sep, end=end, file=file)


class WIPCommandError(commands.errors.CheckFailure):
	pass


class CommandUnderMaintenanceError(commands.errors.CheckFailure):
	def __init__(self, reason: str):
		self.reason = reason

import json

from discord.ext import commands

from libs import botutils


class JunoHelp(commands.MinimalHelpCommand):
	with open('assets/perms.json') as f:
		PERMS = json.load(f)

	def __init__(self, **options):
		self.command_name = None
		self.appinfo = None
		super().__init__(**options, command_attrs={
			"description": "Shows a list of all the commands of the bot or the details of said commands.",
			"extras":      {
				'example':   'help',
				'signature': '[Command]'
			}
		})

	def command_not_found(self, command: str):
		return f'Command "{command}" not found.'

	async def prepare_help_command(self, _, command: str):
		self.appinfo = await self.context.bot.application_info()
		self.command_name = command

	def get_command_signature(self, command: commands.Command):
		try:
			signature = f" {command.extras['signature']}"
		except KeyError:
			signature = f" {command.signature}" if len(command.signature) else ""
			signature = signature.replace("_", " ").title()
		return f"`{self.context.clean_prefix}{command.qualified_name}{signature}`"

	async def send_bot_help(self, mapping):
		embed = botutils.embed_template(
			title="Help",
			footer=f"<>=Necessary, []=Optional.\nTo see more information about a specific command, type {self.context.clean_prefix}help <command>.\n{self.context.bot.user.display_name} was created by {self.appinfo.owner}."
		)

		for cog, _commands in mapping.items():
			filtered = await self.filter_commands(_commands, sort=True)
			command_signatures = [self.get_command_signature(c) for c in filtered]
			if command_signatures:
				cog_name = getattr(cog, "qualified_name", "No Category")
				if cog_name != "DevCog":
					embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)

		destination = self.get_destination()
		await destination.send(embed=embed)

	async def send_command_help(self, command: commands.Command):
		await command.can_run(self.context)

		try:
			example = command.extras['example']
		except KeyError:
			example = None

		embed = botutils.embed_template(
			title=f"{self.context.clean_prefix}{self.command_name}",
			footer=f"<>=Necessary, []=Optional.\nTo see more information about a specific command, type {self.context.clean_prefix}help <command>.\n{self.context.bot.user.display_name} was created by {self.appinfo.owner}."
		)

		cog_name = command.cog_name
		embed.add_field(name="**Category**", value=cog_name)

		if command.description:
			command_description = command.description
			embed.add_field(name="**Description**", value=command_description, inline=False)

		if len(command.aliases):
			aliases = [command.qualified_name]
			if command.full_parent_name:  # If command is subcommand:
				aliases.extend(f'{command.full_parent_name} {alias}' for alias in command.aliases)
			aliases = [f"`{self.context.clean_prefix}{alias}`" for alias in aliases]
			embed.add_field(name="**Aliases**", value=', '.join(aliases), inline=False)

		if 'permission' in command.extras:
			embed.add_field(name="**Permissions**", value=f'You require "{self.PERMS[command.extras["permission"]]}" permissions to use this command.')
		usage_str = f"{self.get_command_signature(command)}"
		if example is not None:
			usage_str += f"\nE.G.: `{self.context.clean_prefix}{self.command_name} {example}`"
		embed.add_field(name="**Usage**", value=usage_str, inline=False)

		destination = self.get_destination()
		await destination.send(embed=embed)

	async def send_cog_help(self, cog):
		destination = self.get_destination()
		await botutils.error_template(destination, self.command_not_found(cog.qualified_name))

	async def send_group_help(self, group):
		await group.can_run(self.context)
		destination = self.get_destination()
		prefix = self.context.clean_prefix

		embed = botutils.embed_template(
			title=f"{prefix}{self.command_name}",
			footer=f"<>=Necessary, []=Optional.\nTo see more information about a specific command, type {prefix}help <command>.\n{self.context.bot.user.display_name} was created by {self.appinfo.owner}."
		)

		if group.invoke_without_command:
			cog_name = group.cog_name
			embed.add_field(name="**Category**", value=cog_name, inline=False)

			if group.description:
				command_description = group.description
				embed.add_field(name="**Description**", value=command_description, inline=False)

			if len(group.aliases):
				aliases = [group.qualified_name]
				aliases.extend(group.aliases)
				aliases = [f"`{prefix}{alias}`" for alias in aliases]
				embed.add_field(name="**Aliases**", value=', '.join(aliases), inline=False)

			cmds = [self.get_command_signature(cmd) for cmd in group.all_commands.values()]
			embed.add_field(name="**Commands**", value='\n'.join(cmds), inline=False)
		else:
			await destination.send(f"THIS MESSAGE SHOULD NOT APPEAR. IF IT DOES, PLEASE REPORT IT WITH THE `{prefix}report` COMMAND!")

		await destination.send(embed=embed)


class Help(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self._original_help_command = bot.help_command
		bot.help_command = JunoHelp()
		bot.help_command.cog = self
		botutils.log("Help Command Ready!")

	def cog_unload(self):
		self.bot.help_command = self._original_help_command


async def setup(bot: commands.Bot):
	await bot.add_cog(Help(bot), override=True)

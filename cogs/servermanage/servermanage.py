"""Server Manage Cog, to help manage server icon and banners."""
import logging
import time
import asyncio
from datetime import datetime, timedelta
from os.path import splitext
from pathlib import Path
import discord
from redbot.core import Config, checks, commands, data_manager
from redbot.core.commands.context import Context
from redbot.core.utils import paginator
from redbot.core.bot import Red

BASE_GUILD = {"icons": {}, "dates": {}}


class Exceptions(Exception):
    pass


class InvalidAttachmentsError(Exceptions):
    pass


class InvalidFileError(Exceptions):
    pass


class InvalidImageError(Exceptions):
    pass


class ServerManage(commands.Cog):
    """Auto-assign server banner and icon on configurable days."""

    # Class constructor
    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=5842647, force_registration=True)
        # Register default (empty) settings.
        self.config.register_guild(**BASE_GUILD)

        # Initialize logger, and save to cog folder.
        saveFolder = data_manager.cog_data_path(cog_instance=self)
        self.logger = logging.getLogger("red.luicogs.ServerManage")
        if self.logger.level == 0:
            # Prevents the self.logger from being loaded again in case of module reload.
            self.logger.setLevel(logging.INFO)
            handler = logging.FileHandler(
                filename=str(saveFolder) + "/info.log", encoding="utf-8", mode="a"
            )
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(message)s", datefmt="[%d/%m/%Y %H:%M:%S]")
            )
            self.logger.addHandler(handler)

        # On cog load, we want the loop to run once.
        self.lastChecked = datetime.now() - timedelta(days=1)
        # self.bgTask = self.bot.loop.create_task(self.birthdayLoop())

    # Cancel the background task on cog unload.
    def __unload(self):  # pylint: disable=invalid-name
        # TODO add task later
        # self.bgTask.cancel()
        pass

    @staticmethod
    def validateImageAttachment(message):
        """Check to see if the message contains a valid image attachment.

        Parameters
        ----------
        message: discord.Message
            The message you wish to check.

        Raises
        ------
        InvalidFileError
            The attachment uploaded is not an image.
        InvalidImageError:
            The image uploaded is not a PNG or GIF.
        InvalidAttachmentsError:
            There isn't exactly one attachment.
        """
        attachments = message.attachments
        if len(attachments) != 1:
            raise InvalidAttachmentsError

        image = attachments[0]

        # Perform file validation: check width/height and file extension.
        if not image.height and not image.width:
            raise InvalidFileError

        if splitext(image.filename)[1].lower() not in [".png", ".gif"]:
            raise InvalidImageError

    @commands.group(name="servermanage", aliases=["sm"])
    @commands.guild_only()
    @checks.mod_or_permissions()
    async def serverManage(self, ctx: Context):
        """Manage server icons and banners."""

    @serverManage.group(name="icons")
    async def serverIcons(self, ctx: Context):
        """Manage server icons."""

    @serverIcons.command(name="add", aliases=["create"])
    async def iconAdd(self, ctx: Context, iconName: str):
        """Add a server icon to the database.

        Parameters
        ----------
        iconName: str
            The name of the icon you wish to add.
        image: attachment
            The server icon, included as an attachment.
        """
        try:
            self.validateImageAttachment(ctx.message)
        except InvalidAttachmentsError:
            await ctx.send("Please attach one file!")
            return
        except InvalidFileError:
            await ctx.send("The file is not an image, please upload an image!")
            return
        except InvalidImageError:
            await ctx.send("Please upload a PNG or GIF image!")

        await ctx.send("We made it here")
        # Check to see if this exists already
        icons = await self.config.guild(ctx.guild).icons()
        if iconName in icons.keys():
            await ctx.send("This icon already exists!")
            return

        # Save the image.
        saveFolder = data_manager.cog_data_path(cog_instance=self)
        image = ctx.message.attachments[0]
        extension = splitext(image.filename)[1].lower()
        directory = "{}/{}/icons/".format(str(saveFolder), ctx.guild.id)
        Path(directory).mkdir(parents=True, exist_ok=True)
        filepath = f"{directory}{iconName}{extension}"
        await ctx.message.attachments[0].save(filepath, use_cached=True)
        async with self.config.guild(ctx.guild).icons() as icons:
            icons[iconName] = {}
            icons[iconName]["filename"] = f"{iconName}{extension}"
        await ctx.send("Icon saved!")

    @serverIcons.command(name="remove", aliases=["del", "delete", "rm"])
    async def iconRemove(self, ctx: Context, iconName: str):
        """Remove a server icon from the database.

        Parameters
        ----------
        iconName: str
            The icon name you wish to remove.
        """

    @serverIcons.command(name="show")
    async def iconShow(self, ctx: Context, iconName: str):
        """Show a server icon from the database.

        Parameters
        ----------
        iconName: str
            The icon name you wish to show.
        """

    @serverIcons.command(name="list", aliases=["ls"])
    async def iconList(self, ctx: Context):
        """List the dates associated with server icons."""

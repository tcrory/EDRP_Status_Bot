#! /usr/bin/env python3
""" Discord bot to display status information for the number of players logged in
    to the ED RP private group on Elite.
"""

import aiohttp
import asyncio
import discord
import logging
import bot_config as config
import edrp_api as edrp
from discord.ext import commands
from discord.ext.commands import Bot


# Set up logging.
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='edrp_status_bot.log', mode='w')
handler.setFormatter(
    logging.Formatter(
        'EDRP|%(asctime)s|%(levelname)s|%(name)s|%(message)s'
    )
)
logger.addHandler(handler)

# Set up the initial coroutine for updating the bot presence.
loop = asyncio.get_event_loop()
bot = Bot(command_prefix=config.COMMAND_PREFIX, loop=loop)


async def maintain_accurate_bot_presence():
    """ Update the bot presence with values returned from the EDRP API."""
    async with aiohttp.ClientSession() as session:
        try:
            while True:
                if bot.is_logged_in:
                    await update_bot_presence(session)
                else:
                    logger.warning('BOT|Bot is not currently logged in.')
                await asyncio.sleep(60)
        except asyncio.CancelledError:
            return


async def update_bot_presence(session):
    """ Update the bot presence with values returned from the EDRP API.

        :return: Success of API call.
        :rtype: bool
    """
    total_cmdrs = await edrp.get_active_count(session)
    if total_cmdrs is None:
        logger.error('BOT|Unable to retrieve a count of active CMDRs from the EDRP API.')
        return False
    logger.info('BOT|The EDRP API reports {} CMDRs active.'.format(total_cmdrs))
    game_name = 'EDRP: {} CMDRs'.format(total_cmdrs)
    await bot.change_presence(game=discord.Game(name=game_name))
    return True


# Setup the discord bot event handlers.
@bot.event
async def on_ready():
    """ When bot is ready, update the bot presence."""
    logger.info('BOT|Bot is now ready.')
    async with aiohttp.ClientSession() as session:
        await update_bot_presence(session)


async def windows_signal_handler():
    """ The signal handler will not work on Windows when using
        asyncio.get_event_loop().run_forever()

        This simple loop allows for proper signal handling.
    """
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        return


# Start the task and bot.
logger.info('BOT|Starting custom tasks.')
loop.create_task(windows_signal_handler())
loop.create_task(maintain_accurate_bot_presence())
logger.info('BOT|Starting Discord bot.')
bot.run(config.TOKEN)
logger.info('BOT|Discord bot closed.')

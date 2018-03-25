#! /usr/bin/python3.5
""" Discord bot to display status information for the number of players logged in
    to the ED RP private group on Elite.
"""

import aiohttp
import asyncio
import discord
import logging
import time
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


async def maintain_accurate_bot_presence(bot):
    """ Update the bot presence with values returned from the EDRP API."""
    async with aiohttp.ClientSession() as session:
        try:
            while True:
                if bot.is_logged_in:
                    await update_bot_presence(session, bot)
                else:
                    logger.warning('BOT|Bot is not currently logged in.')
                await asyncio.sleep(60)
        except asyncio.CancelledError:
            await session.close()
            return


async def update_bot_presence(session, bot):
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


def main():
    """ Start the bot and any additional tasks."""
    # Remake the event loop and the bot.
    logger.info('BOT|Creating a new event loop.')
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    bot = Bot(command_prefix=config.COMMAND_PREFIX, loop=loop)

    # Disable all commands.
    bot.remove_command('help')
    bot.recursively_remove_all_commands()

    # Setup the discord bot event handlers.
    @bot.event
    async def on_ready():
        """ When bot is ready, update the bot presence."""
        logger.info('BOT|Bot is now ready.')
        async with aiohttp.ClientSession() as session:
            try:
                await update_bot_presence(session, bot)
            except asyncio.CancelledError:
                await session.close()
                return

    # Start the task and bot.
    logger.info('BOT|Starting custom tasks.')
    loop.create_task(windows_signal_handler())
    loop.create_task(maintain_accurate_bot_presence(bot))
    logger.info('BOT|Starting Discord bot.')
    try:
        bot.run(config.TOKEN)
    except aiohttp.ClientError:
        # In the event of an aiohttp disconnect, close the loop and pass the exception.
        # This code gathered from the discord.py run() function.
        logger.error('BOT|Caught an aiohttp.ClientError exception.')
        if not loop.is_closed():
            logger.warning('BOT|Closing the bot.')
            loop.run_until_complete(bot.logout())
            pending = asyncio.Task.all_tasks(loop=loop)
            gathered = asyncio.gather(*pending, loop=loop)
            try:
                gathered.cancel()
                loop.run_until_complete(gathered)
                # we want to retrieve any exceptions to make sure that
                # they don't nag us about it being un-retrieved.
                gathered.exception()
            except:
                pass
        logger.warning('BOT|Re-raising the aiohttp.ClientError exception so that the bot may be restarted.')
        raise aiohttp.ClientError
    finally:
        # Close the event loop if it is still open.
        if not loop.is_closed():
            loop.close()


while True:
    try:
        # Start the task and bot.
        main()
    except discord.DiscordException as err:
        # Log stack trace.
        logger.error('BOT|Caught unhandled Discord exception:', exc_info=True)
        restart_delay = 60
        logger.info('BOT|Waiting for {} seconds.'.format(restart_delay))
        time.sleep(restart_delay)
        logger.info('BOT|Attempting to restart bot.')
        continue
    except aiohttp.ClientError as err:
        logger.warning('BOT|Caught the re-raised aiohttp.ClientError exception.')
        restart_delay = 600
        logger.info('BOT|Waiting for {} seconds.'.format(restart_delay))
        time.sleep(restart_delay)
        logger.info('BOT|Attempting to restart bot.')
        continue
    else:
        logger.critical('BOT|Caught unhandled exception:', exc_info=True)
        break

logger.info('BOT|Discord bot closed.')

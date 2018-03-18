#! /usr/bin/python3.5
""" Methods for generating async HTTP requests for the EDRP API."""

import aiohttp
import asyncio
import async_timeout
import json
import logging

__version__ = '0.0.1'


EDRP_API_URL = 'http://edrp-api.danowebstudios.com'

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


# Low Level API Functions
async def post(session, payload):
    """ Create an HTTP POST request for the EDRP API.

        :param session: aiohttp.ClientSession() object.
        :param payload: Payload for the HTTP POST request.
        :return: Response from HTTP POST request.
    """
    # Replace spaces in the payload with '+'.
    payload = payload.replace(' ', '+')
    url = '{}{}'.format(EDRP_API_URL, payload)
    # Make the POST request.
    async with async_timeout.timeout(10):
        async with session.post(url) as response:
            if response.status != 200:
                error = 'API|POST Response Status: {}, Response Text: {}'.format(
                    response.status,
                    await response.text()
                )
                logger.error(error)
                return None
            return await response.text()


async def get(session, payload):
    """ Create an HTTP GET request for the EDRP API.

        :param session: aiohttp.ClientSession() object.
        :param payload: Payload for the HTTP GET request.
        :return: JSON object received from the EDRP API.
    """
    # Replace spaces in the payload with '+'.
    payload = payload.replace(' ', '+')
    url = '{}{}'.format(EDRP_API_URL, payload)
    # Make the GET request.
    async with async_timeout.timeout(10):
        async with session.get(url) as response:
            if response.status != 200:
                error = 'EDRP API|GET Response Status: {}, Response Text: {}'.format(
                    response.status,
                    await response.text()
                )
                return None
            try:
                return await response.json(content_type='text/html')
            except aiohttp.ContentTypeError as err:
                logger.error(
                    (
                        'API|Unable to convert the response to JSON. Raw Response: {}'
                    ).format(await response.read()),
                    exc_info=True
                )
                return await response.text()


# High Level API Functions
async def post_logon(session, cmdr):
    """ Set an event marker for a CMDR logging onto the plugin.

        :param session: aiohttp.ClientSession() object.
        :param cmdr: CMDR name.
        :return:
    """
    await post(session, '/logon/{}'.format(cmdr))


async def post_logoff(session, cmdr):
    """ Set an event marker for a CMDR logging off the plugin.

        :param session: aiohttp.ClientSession() object.
        :param cmder: CMDR name.
        :return:
    """
    await post(session, '/logoff/{}'.format(cmdr))


async def post_station(session, cmdr, station):
    """ Set an event marker for a CMDR entering a station.

        :param session: aiohttp.ClientSession() object.
        :param cmdr: CMDR name.
        :param station: Station name.
        :return:
    """
    await post(session, '/station/{}/{}'.format(station, cmdr))


async def post_system(session, cmdr, system):
    """ Set an event marker for a CMDR entering a star system.

        :param session: aiohttp.ClientSession() object.
        :param cmdr: CMDR name.
        :param system: System name.
        :return:
    """
    await post(session, '/system/{}/{}'.format(system, cmdr))


async def get_active(session):
    """ Get a list of users with an event from the plugin within the last 10
        minutes.

        :param session: aiohttp.ClientSession() object.
        :return: List of user names.
    """
    response_json = await get(session, '/active')
    if not response_json or 'message' not in response_json:
        return None
    # Message will be returned as a string of JSON that needs to be loaded.
    try:
        msg_json = json.loads(response_json['message'])
    except json.JSONDecodeError:
        log.error(
            (
                'Unable to load the JSON response to get_active(): {}'
            ).format(response_json['message']),
            exc_info=True
        )
        return None
    # Loading the message JSON should give you a list of dictionary objects.
    if type(msg_json) != list:
        return None
    # Pull the CMDR names from the list of dictionaries.
    cmdr_names = []
    for msg_dict in msg_json:
        if 'cmdrName' not in msg_dict:
            log.warning(
                (
                    'Unable to retrieve CMDR Name. '
                    'Object Type: {}, Object Value: {}'
                ).format(type(msg_dict), msg_dict)
            )
            continue
        cmdr_names.append(msg_dict['cmdrName'])
    return cmdr_names


async def get_active_count(session):
    """ Get a count of the users with an event from the plugin within the last 10
        minutes.

        :param session: aiohttp.ClientSession() object.
        :return: User count.
    """
    response_json = await get(session, '/active-count')
    if not response_json or 'message' not in response_json:
        return None
    # Message should be a string of an integer value.
    try:
        active_count = int(response_json['message'])
    except (ValueError, TypeError) as err:
        logger.error(
            (
                'API|Unable to convert the active-count response message to an '
                'integer. Message Type: {}, Raw Message: {}'
            ).format(type(response_json), response_json),
            exc_info=True
        )
        return None
    return active_count

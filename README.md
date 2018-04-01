# EDRP Status Bot

A Discord bot used for tracking CMDRs on the ED RP private group.

## Requirements

* Python 3.5+
* Python Packages:
    * asyncio
    * aiohttp
    * async_timeout
    * discord.py

## Functionality

* Logs on to the ED RP Discord server.
* Queries active CMDR information from the EDRP API.
* Displays the number of active CMDRs as a `Game` status.<br>
(e.g. "Playing EDRP: *n* CMDRs")

## EDRP API

* Current API is an open JSON API which can be accessed at:<br>
https://edrp-api.danowebstudios.com/

## Information Gathering

Information is gathered by the CMDRs via the EDRP Plugin for the Elite Dangerous Market Connector.

#### EDRP Plugin
* Instructions for the EDRP Plugin can be found at:<br>
https://github.com/Danoweb/elite-dangerous-roleplay-tracker-plugin

#### Elite Dangerous Market Connector
* Documentation about Elite Dangerous Market Connector and writing plugins for it can be found at:<br>
https://github.com/Marginal/EDMarketConnector/blob/master/PLUGINS.md

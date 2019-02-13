# -*- coding: utf-8 -*-
#
# Mailman webhook is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# Mailman webhook is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Mailman webhook.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Ondrej Kolin <okolin@benocs.com>
#
# Inspired by the Hypperkitty mailman plugin 
# and tutorial http://threebean.org/blog/plugins-for-mailman3/

"""
Class implementation of Mailman's IArchiver interface
This will be imported by Mailman Core and must thus be Python3-compatible.
"""

from __future__ import absolute_import, unicode_literals

import os
import requests
import traceback
import json
import logging

from mailman.interfaces.archiver import IArchiver
from zope.interface import implementer
from mailman.config import config
from mailman.config.config import external_configuration
from configparser import NoOptionError
from httplib2 import Http
from typing import Dict

logger = logging.getLogger("mailman.archiver")


def _log_error(exc):
    logger.error('Webhook: %s', exc)


@implementer(IArchiver)
class Archiver(object):

    name = "webhook"
    keys = [
        "archived-at",
        "delivered-to",
        "from",
        "cc",
        "to",
        "in-reply-to",
        "message-id",
        "subject",
        "x-message-id-hash",
        "references",
        "x-mailman-rule-hits",
        "x-mailman-rule-misses",
    ]
    config = None
    list_urls = {}
    message_format = '''
            [{list_name}]
            From: {from}
            Subject: {subject} 
            {text} \n
        ''' 
    def _load_config(self):
        """
        Find the location of the HyperKitty-specific config file from Mailman's
        main config file and load the values.
        """
        # Read our specific configuration file
        archiver_config = external_configuration(
                config.archiver.webhook.configuration)
        try:
            self.url = archiver_config.get("global", "url")
        except (KeyError, NoOptionError):
            self.url = ""
            pass
        try:
            self.message_format = archiver_config.get("global", "message_format")  
        except (KeyError, NoOptionError):
            pass
        try:
            for section in archiver_config.sections():
                if section.startswith("list."):
                    list_name = section[5:]
                    self.list_urls[list_name] = archiver_config[section]["url"]
                    if archiver_config[section]["url"] != "":
                        _log_error(list_name + " channel is ready to send out messages!")
                else:
                    continue
        except (KeyError, NoOptionError) as e: 
            _log_error("While parsing the config for lists configuration, there was an error " + str(e.message))

    def __init__(self):
        """ Just initialize fedmsg. """
        self._load_config()

    def archive_message(self, mlist, msg):
        """Send the message to the "archiver".

        In our case, we just publish it to the fedmsg bus.

        :param mlist: The IMailingList object.
        :param msg: The message object.
        """
        # Try to read the subject
        subject = "- Another message -"
        # Message reading will have to be expended
        msg_content = msg.get_payload(None)
        try:
            subject = msg["subject"]
        except:
            pass
        format_dict = {
            "list_name" : mlist.list_name,
            "from" : msg["from"],
            "subject" : subject,
            "text" : msg_content
        }

        information_msg: str = self.message_format.format(**format_dict)
        self._post_to_rocketchat_webhook(information_msg, mlist.list_name)

    def _post_to_rocketchat_webhook(self, message, list_name):
        h = Http()
        json_object = json.dumps({
            "text" : message
        })
        # Load the url, if empty, do nothing
        url = self.url
        try:
            url = self.list_urls[list_name]
        except KeyError as e:
            pass
        if url == "":
            _log_error("For channel {} is the webhook url empty.".format(list_name)) 
            return
        resp, content = h.request(url, "POST", json_object)
        if resp.status == 200:
            json_object = json.loads(content)
            if not json_object["success"]:
                _log_error("Rocket.chat says the post was not successfull" + str())
        else:
            _log_error("Rocket.chat http response was not 200 \n" + url + "\n" + str(resp))




    def list_url(self, mlist):
        """ This doesn't make sense for webhook.
        But we must implement for IArchiver.
        """
        return None

    def permalink(self, mlist, msg):
        """ This doesn't make sense for webhook. 
        But we must implement for IArchiver.
        """
        return None


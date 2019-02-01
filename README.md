# Sending mailman messages to Rocketchat

This is a small Python class, located in `/usr/lib/python3/dist-packages/mailman_webhook/__init.py__` for connecting your rocket.chat instance to a mailman (send e-mail messages from mailman to rocket.chat webhook)

Configuration is located in `/etc/mailman3/mailman-webhook.cfg`. The plugin (archiver) must be activated in the main config `/etc/mailman3/mailman.cfg` file setting up the class path like this:

```
[archiver.webhook]
class: mailman_webhook.Archiver
enable: yes
configuration: /etc/mailman3/mailman-webhook.cfg
```
## Logging

Plugin logs in the default log file prefixing the messages with `Webhook:`

Messages should come on:

*   <div class="li">Errors</div>

*   <div class="li">Channel matched</div>

*   <div class="li">Message not forwarded to rocket.chat (because of settings)</div>

## List

```
# Configuration of the new mailing list -> channel
[list.example_list]
url = "http://rocket.chat/webhook/url/..."
```

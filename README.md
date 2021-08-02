# Blood on the Clocktower
Blood on the Clocktower is a fantastic social deduction game that can be played online via Discord. This is a simple bot which runs in Discord to assist running Blood on the Clocktower games online.

Once the bot is running, you can react to the message sent by the bot to move players between private and public voice channels.

### Actions
- :white_check_mark: gives the user the `Player` role, and unclicking removes the `Player` role
- :crescent_moon: moves all users marked with the `Player` or `Story Teller` role to individual cottages
- :sunny: moves all users marked with the `Player` or `Story Teller` role to `Beneath the Clocktower`
- :scroll: warns all users that nominations are soon and will move all users in `Ravenswood Bluff` to `Beneath the Clocktower`

### Starting the bot
The bot will default to sending messages in the `commands` text channel. Upon starting, it will check the last 100 messages and delete any that it previously authored.

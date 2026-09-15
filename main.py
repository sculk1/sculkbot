# Discord bot that watches for Cosmic Princess Kaguya references.

import logging
import os
import random
import re
import time
from urllib.parse import unquote, urlparse

import discord
from dotenv import load_dotenv

from keywords import (
    MOST_CERTAINLY_CPK,
    NEGATIVE_EXCLUSIONS,
    TITLES,
    UNAMBIGUOUS_CPK_REF,
)


TARGET_USER_ID = 780846736922509312
COMMAND_PREFIX = "§"
HELP_COMMAND = f"{COMMAND_PREFIX}help"
SILENCE_COMMAND = f"{COMMAND_PREFIX}silence"
UNSILENCE_COMMAND = f"{COMMAND_PREFIX}unsilence"
SELF_IGNORE_COMMAND = f"{COMMAND_PREFIX}selfignore"
NICK_COMMAND = f"{COMMAND_PREFIX}nick"
SAY_COMMAND = f"{COMMAND_PREFIX}say"
BANNER_EMOJIS = (
    "<:iro0:1549505868620628138>"
    "<:iro1:1549505891588382760>"
    "<:iro2:1549505908596412436>"
    "<:iro3:1549505924299886712>"
    "<:iro4:1549505942947762296>"
    "<:iro5:1549505956428382288>"
    "<:iro6:1549505968545472593>"
    "<:iro7:1549505980348375091>"
    "<:iro8:1549505993526739125>"
    "<:iro9:1549506023633715342>"
)
IROHA_COMMAND = f"{COMMAND_PREFIX}iroha"
MAX_SILENCE_MINUTES = 10
MAX_NICKNAME_LENGTH = 32
PUBLIC_HELP_MESSAGE = (
    "<:irohabot:1549502389520957571>Available commands:\n"
    f"{HELP_COMMAND} - show this help message\n"
    f"{SILENCE_COMMAND} [1-{MAX_SILENCE_MINUTES}] - silence CPK notifications in this channel\n"
    f"{UNSILENCE_COMMAND} - re-enable CPK notifications in this channel\n"
    f"{IROHA_COMMAND} - <:iroha:1549502368196984832> display the Iroha banner <:iroha:1549502368196984832>"
)
TARGET_HELP_MESSAGE = (
    f"{PUBLIC_HELP_MESSAGE}\n"
    f"{SELF_IGNORE_COMMAND} - toggle your notifications\n"
    f"{NICK_COMMAND} <name> - change the bot's nickname in this server\n"
    f"{SAY_COMMAND} <message> - make the bot say a message"
)
CPK_LINK_PING_MESSAGE = f"<:iroha:1549502368196984832>Cosmic Princess Kaguya post/link spotted <@{TARGET_USER_ID}>!"
STANDARD_PING_MESSAGES = (
    f"<:iroha:1549502368196984832> CPK mentioned! <@{TARGET_USER_ID}>",
)
URL_PATTERN = re.compile(
    r"(?:(?:https?://|www\.)[^\s<>()]+|"
    r"(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/[^\s<>()]*)?)",
    re.IGNORECASE,
)
# These are normalized below, so spaces, hyphens, underscores, and case do not matter.
# Keep the short "cpk" keyword out because it is too ambiguous in a URL.
CPK_LINK_FORMS = tuple(title for title in TITLES if title != "cpk") + (
    "cho kaguyahime pr",
    "chokaguyahimepr",
    "cho kaguyahime",
)
CPK_LINK_PARTIAL_FORMS = (
    "cosmic princess",
    "cosmicprincess",
    "princess kaguya",
    "princesskaguya",
    "cho kaguya",
    "chokaguya",
    "kaguya hime",
    "kaguyahime",
    "cho kaguyahime pr",
    "chokaguyahimepr",
)
LOGGER = logging.getLogger(__name__)


def matches_phrase(phrase: str, text: str) -> bool:
    # Match phrases as complete words instead of matching inside other words.
    pattern = rf"\b{re.escape(phrase)}\b"
    return re.search(pattern, text, re.IGNORECASE) is not None


def should_ping(message_content: str) -> bool:
    text = message_content.casefold()

    # Titles and unique names always win; exclusions only filter broad references.
    if any(matches_phrase(phrase, text) for phrase in (*TITLES, *UNAMBIGUOUS_CPK_REF)):
        return True

    if any(matches_phrase(phrase, text) for phrase in NEGATIVE_EXCLUSIONS):
        return False

    return any(matches_phrase(phrase, text) for phrase in MOST_CERTAINLY_CPK)


def normalize_link_text(value: str) -> str:
    # Keep letters and numbers from every supported script; remove URL separators.
    return "".join(character for character in value.casefold() if character.isalnum())


NORMALIZED_CPK_LINK_FORMS = tuple(
    normalize_link_text(form) for form in CPK_LINK_FORMS
)
NORMALIZED_CPK_LINK_PARTIAL_FORMS = tuple(
    normalize_link_text(form) for form in CPK_LINK_PARTIAL_FORMS
)


def contains_cpk_link(message_content: str) -> bool:
    # Check every URL component so domains, paths, queries, and fragments work.
    for link in URL_PATTERN.findall(message_content):
        normalized_link = link.rstrip(".,!?;:)")
        parsed_link = urlparse(normalized_link)
        url_text = unquote(
            " ".join(
                part
                for part in (
                    parsed_link.netloc,
                    parsed_link.path,
                    parsed_link.params,
                    parsed_link.query,
                    parsed_link.fragment,
                )
                if part
            )
        ).casefold()
        compact_url = normalize_link_text(url_text)

        if any(form in compact_url for form in NORMALIZED_CPK_LINK_FORMS):
            return True

        if any(form in compact_url for form in NORMALIZED_CPK_LINK_PARTIAL_FORMS):
            return True

    return False


def standard_reply() -> str:
    response = random.choice(STANDARD_PING_MESSAGES)

    if random.randrange(100) == 0:
        gif_url = os.getenv("CPK_GIF_URL")
        if gif_url:
            response = f"{response}\n{gif_url}"
        else:
            LOGGER.warning("no gif url")

    return response


class SculkBot(discord.Client):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.silenced_channels: dict[int, float] = {}
        self.ignored_users: set[int] = set()

    async def on_ready(self) -> None:
        LOGGER.info("Logged in as %s (ID: %s)", self.user, self.user.id)

    async def on_resumed(self) -> None:
        LOGGER.info("Discord session resumed")

    async def on_disconnect(self) -> None:
        LOGGER.warning("Disconnected from Discord")

    async def on_error(self, event_method: str, *args: object, **kwargs: object) -> None:
        LOGGER.exception("Unhandled error in Discord event: %s", event_method)

    async def on_message(self, message: discord.Message) -> None:
        if self.user is not None and message.author.id == self.user.id:
            return

        command_parts = message.content.casefold().split()
        if command_parts and command_parts[0] == HELP_COMMAND:
            help_message = (
                TARGET_HELP_MESSAGE
                if message.author.id == TARGET_USER_ID
                else PUBLIC_HELP_MESSAGE
            )
            await message.reply(help_message, mention_author=False)
            return

        if command_parts and command_parts[0] == IROHA_COMMAND:
            await self.handle_iroha_command(message)
            return

        if command_parts and command_parts[0] == UNSILENCE_COMMAND:
            await self.handle_unsilence_command(message)
            return

        if command_parts and command_parts[0] == SELF_IGNORE_COMMAND:
            await self.handle_self_ignore_command(message)
            return

        if command_parts and command_parts[0] == NICK_COMMAND:
            await self.handle_nick_command(message)
            return

        if command_parts and command_parts[0] == SAY_COMMAND:
            await self.handle_say_command(message)
            return

        if command_parts and command_parts[0] == SILENCE_COMMAND:
            await self.handle_silence_command(message, command_parts)
            return

        if message.author.id in self.ignored_users:
            return

        silence_expires_at = self.silenced_channels.get(message.channel.id, 0)
        if silence_expires_at > time.monotonic():
            return
        self.silenced_channels.pop(message.channel.id, None)

        if contains_cpk_link(message.content):
            await message.reply(CPK_LINK_PING_MESSAGE, mention_author=False)
            LOGGER.info("Sent link ping for message %s", message.id)
            return

        if should_ping(message.content):
            await message.reply(standard_reply(), mention_author=False)
            LOGGER.info("Sent keyword ping for message %s", message.id)

    async def handle_silence_command(
        self,
        message: discord.Message,
        command_parts: list[str],
    ) -> None:
        if len(command_parts) > 2:
            await message.reply(
                f"Usage: {SILENCE_COMMAND} [1-{MAX_SILENCE_MINUTES}]",
                mention_author=False,
            )
            return

        try:
            minutes = int(command_parts[1]) if len(command_parts) == 2 else MAX_SILENCE_MINUTES
        except ValueError:
            await message.reply(
                f"Usage: {SILENCE_COMMAND} [1-{MAX_SILENCE_MINUTES}]",
                mention_author=False,
            )
            return

        if not 1 <= minutes <= MAX_SILENCE_MINUTES:
            await message.reply(
                f"Silence duration must be between 1 and {MAX_SILENCE_MINUTES} minutes<:Iroahstress:1549502338144669806>",
                mention_author=False,
            )
            return

        self.silenced_channels[message.channel.id] = time.monotonic() + minutes * 60
        await message.reply(
            f"CPK notifications silenced in this channel for {minutes} minute(s)<:Iroahstress:1549502338144669806>",
            mention_author=False,
        )
        LOGGER.info(
            "Silenced notifications in channel %s for %s minute(s)",
            message.channel.id,
            minutes,
        )

    async def handle_unsilence_command(self, message: discord.Message) -> None:
        was_silenced = self.silenced_channels.pop(message.channel.id, None) is not None
        response = (
            "CPK notifications are enabled again in this channel."
            if was_silenced
            else "CPK notifications were not silenced in this channel."
        )
        await message.reply(response, mention_author=False)
        LOGGER.info("Unsilenced notifications in channel %s", message.channel.id)

    async def handle_nick_command(self, message: discord.Message) -> None:
        if message.author.id != TARGET_USER_ID:
            await message.reply(
                "Only the configured sculk can use this command<:Iroahstress:1549502338144669806>",
                mention_author=False,
            )
            return

        if message.guild is None:
            await message.reply(
                "<:Iroahstress:1549502338144669806>",
                mention_author=False,
            )
            return

        nickname = message.content.partition(" ")[2].strip()
        if not nickname:
            await message.reply(
                f"Usage: {NICK_COMMAND} <name>",
                mention_author=False,
            )
            return

        if len(nickname) > MAX_NICKNAME_LENGTH:
            await message.reply(
                f"Keep it under {MAX_NICKNAME_LENGTH} <:Iroahstress:1549502338144669806>",
                mention_author=False,
            )
            return

        bot_member = message.guild.me
        if bot_member is None:
            await message.reply(
                "I could not find my server membership",
                mention_author=False,
            )
            return

        try:
            await bot_member.edit(nick=nickname)
        except discord.Forbidden:
            LOGGER.warning("Missing permission<:Iroahstress:1549502338144669806> %s", message.guild.id)
            await message.reply(
                "I need the Manage Nicknames permission to do that",
                mention_author=False,
            )
            return
        except discord.HTTPException:
            LOGGER.exception("Failed to change nickname in %s", message.guild.id)
            await message.reply(
                "Discord rejected the nickname change. Please try again.",
                mention_author=False,
            )
            return

        await message.reply(
            f"My nickname is now **{nickname}** in this server.",
            mention_author=False,
        )
        LOGGER.info("Changed nickname in guild %s", message.guild.id)

    async def handle_self_ignore_command(self, message: discord.Message) -> None:
        if message.author.id != TARGET_USER_ID:
            await message.reply(
                "Only sculk1 can use this command",
                mention_author=False,
            )
            return

        if message.author.id in self.ignored_users:
            self.ignored_users.remove(message.author.id)
            response = "Your CPK notifications are enabled"
            LOGGER.info("Enabled notifications for user %s", message.author.id)
        else:
            self.ignored_users.add(message.author.id)
            response = "Your CPK notifications are now ignored"
            LOGGER.info("Ignored notifications for user %s", message.author.id)

        await message.reply(response, mention_author=False)

    async def handle_say_command(self, message: discord.Message) -> None:
        if message.author.id != TARGET_USER_ID:
            await message.reply(
                "Only the configured notification user can use this command.",
                mention_author=False,
            )
            return

        text = message.content.partition(" ")[2].strip()
        if not text:
            await message.reply(
                f"Usage: {SAY_COMMAND} <message>",
                mention_author=False,
            )
            return

        await message.channel.send(text)
        LOGGER.info("Sent target user's message in channel %s", message.channel.id)

    async def handle_iroha_command(self, message: discord.Message) -> None:
        await message.reply(BANNER_EMOJIS, mention_author=False)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def create_intents() -> discord.Intents:
    intents = discord.Intents.default()
    intents.guilds = True
    intents.messages = True
    intents.message_content = True
    return intents


def main() -> None:
    load_dotenv()
    configure_logging()
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        raise RuntimeError("DISCORD_TOKEN is not set in the environment or .env file")

    LOGGER.info("Starting Discord bot")
    SculkBot(intents=create_intents()).run(token, log_handler=None)


if __name__ == "__main__":
    main()

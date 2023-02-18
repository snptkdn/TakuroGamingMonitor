import discord
from dotenv import load_dotenv
import os
from enum import Enum
from typing import Optional

intents = discord.Intents.all()
client = discord.Client(intents=intents)
load_dotenv()

class StatusType(Enum):
    Start = 1
    End = 2
    NotChange = 3

def getStatusType(before: discord.Member, after: discord.Member) -> StatusType:
    before = before.activity
    after = after.activity

    if before is None and after is not None:
        return StatusType.Start
    elif before is not None and after is None:
        return StatusType.End
    elif before is None and after is None:
        return StatusType.NotChange
    elif before is not None and after is not None:
        is_same = before.type == after.type 
        return StatusType.Start if not is_same else StatusType.NotChange
    else:
        return StatusType.NotChange


def is_from_takuro(user_id: int):
    load_dotenv()
    return str(user_id) == os.getenv("TAKURO")

def get_message(status_type: StatusType, activity_type: discord.ActivityType, context: discord.Member) -> Optional[str]:
    title = get_activity_title(activity_type, context)
    suffix = get_activity_suffix(activity_type, context)
    if title is None or suffix is None:
        return None

    if status_type is StatusType.Start:
        return "みんな！！！\n<@{}>が{}を{}始めたよ！！！！".format(
            os.getenv("TAKURO"),
            title,
            suffix
        )
    else:
        return "みんな、、、\n<@{}>が{}を{}終わっちゃったみたい...悲しいね".format(
            os.getenv("TAKURO"),
            title,
            suffix
        )

def get_activity_title(activity_type: discord.ActivityType, context: discord.Member) -> Optional[str]:
    if activity_type is discord.ActivityType.playing:
        return "{}".format(context.activity.title)
    elif activity_type is discord.ActivityType.listening:
        return "{}で{}".format(context.activity.name, context.activity.artist)
    else:
        return None

def get_activity_suffix(activity_type: discord.ActivityType, context: discord.Member) -> Optional[str]:
    if activity_type is discord.ActivityType.playing:
        return "やり"
    elif activity_type is discord.ActivityType.listening:
        return "聴き"
    else:
        return None

def get_should_use_context(status_type: StatusType, before: discord.Member, after: discord.Member) -> Optional[discord.Member]:
    if status_type is StatusType.Start:
        return after
    elif status_type is StatusType.End:
        return before
    else:
        return None


@client.event
async def on_ready():
    print("on_ready")
    print(discord.__version__)

@client.event
async def on_presence_update(before: discord.Member, after: discord.Member):
    if not is_from_takuro(before.id):
        return

    status_type = getStatusType(before, after)
    if status_type is StatusType.NotChange:
        return

    message = get_message(
        status_type,
        get_should_use_context(status_type, before, after).activity.type,
        get_should_use_context(status_type, before, after)
    )

    if message is None:
        return

    await after.guild.get_channel(int(os.getenv("CHANNEL"))).send(message)


client.run(os.getenv("TOKEN"))


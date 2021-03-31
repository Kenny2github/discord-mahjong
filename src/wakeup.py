import os
import asyncio
from discord.ext.commands import Bot

def recurse_mtimes(mtimes: dict, root: str, *s: str):
    for i in os.listdir(os.path.join(*s, root)):
        if os.path.isdir(os.path.join(*s, root, i)):
            recurse_mtimes(mtimes, i, *s, root)
        elif not i.endswith(('.py', '.sql', '.json')):
            pass
        else:
            mtimes[os.path.join(*s, root, i)] \
                = os.path.getmtime(os.path.join(*s, root, i))

async def wakeup(client: Bot):
    mtimes = {}
    extra_names = [
        'i18n\\__init__.py',
        'emojis\\__init__.py',
    ]
    recurse_mtimes(mtimes, os.path.dirname(os.path.abspath(__file__)))
    for name in extra_names:
        mtimes[name] = os.path.getmtime(name)
    while 1:
        try:
            await asyncio.sleep(1)
        except (KeyboardInterrupt, asyncio.CancelledError):
            await client.close()
            return
        if client.should_stop:
            await client.close()
            return
        for fn, mtime in mtimes.items():
            if os.path.getmtime(fn) > mtime:
                await client.close()
                return
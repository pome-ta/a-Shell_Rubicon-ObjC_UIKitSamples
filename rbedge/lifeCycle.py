import asyncio
from pyrubicon.objc.eventloop import RubiconEventLoop

__all__ = [
  'loop',
]

loop = RubiconEventLoop()
asyncio.set_event_loop(loop)


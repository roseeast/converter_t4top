import asyncio
from typing import Optional, Coroutine

class QueueManager:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.is_processing = False

    async def add_task(self, coro: Coroutine):
        await self.queue.put(coro)
        if not self.is_processing:
            asyncio.create_task(self.process_queue())

    async def process_queue(self):
        if self.is_processing:
            return
        
        self.is_processing = True
        
        while not self.queue.empty():
            task = await self.queue.get()
            try:
                await task
            except Exception as e:
                print(f"Error processing queue task: {e}")
            finally:
                self.queue.task_done()
        
        self.is_processing = False

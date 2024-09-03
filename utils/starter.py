from utils.core import logger
from utils.dogs import DogsHouse


async def start(thread: int, session_name: str, phone_number: str, proxy: [str, None]):
    dogs = DogsHouse(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
    account = session_name + '.session'
    try:
        token = await dogs.login(proxy)
        await dogs.goTotask(proxy,token)
        await dogs.goToTask1(proxy,token)
    except Exception as e:
        logger.error(f'Thread {thread} | {account} | Error: {e}')

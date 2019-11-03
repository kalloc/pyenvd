import datetime
import logging
import os
import re
from collections import defaultdict
from typing import DefaultDict

import aiofiles.os
import aiorpcx

logger = logging.getLogger('envd')
ALPNANUM = re.compile('^[a-z0-9A-Z]+$')


class ServerSession(aiorpcx.RPCSession):
    CACHES: DefaultDict = defaultdict(
        lambda: {
            'expire': datetime.datetime.fromtimestamp(0),
            'body': None
        }
    )

    def __init__(self, env_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.env_path = env_path

    async def method_config(self, config_name: str):
        logger.info(f'call config({config_name})', extra={'clientip': self.remote_address()})
        item = self.CACHES[config_name]
        now = datetime.datetime.now()
        if item['expire'] > now:
            return item['body']

        try:
            filename = f'{self.env_path}/{config_name}.env'
            if os.path.abspath(filename) != filename or not ALPNANUM.match(config_name):
                return aiorpcx.ProtocolError(1, 'wrong config name')
            async with aiofiles.open(filename) as fp:
                lines = filter(
                    lambda item: item and not item.startswith('#'),
                    map(
                        lambda item: item.strip(),
                        await fp.readlines()
                    )
                )
                body = '\n'.join(lines)
                self.CACHES[config_name] = {
                    'expire': datetime.datetime.now() + datetime.timedelta(minutes=5),
                    'body': body
                }
                return body

        except FileNotFoundError:
            return aiorpcx.ProtocolError(2, 'unsupported config name')

    async def handle_request(self, request):
        name = f'method_{request.method}'
        method = getattr(self, name)

        if not method:
            raise KeyError(request.method)
        coro = aiorpcx.handler_invocation(method, request)()
        return await coro

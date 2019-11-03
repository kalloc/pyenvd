import asyncio
import logging

import click
from daemonize import Daemonize

import aiorpcx

from envd.server import ServerSession

logger = logging.getLogger('envd')


@click.command()
@click.option('--host', type=str, default='127.0.0.1', help='Listen on host')
@click.option('--port', type=click.IntRange(1, 65535), default=31337, help='Listen on port')
@click.option('--env-path',
              type=click.Path(file_okay=False, resolve_path=True, exists=True),
              default='.config',
              help='Directory witg env')
@click.option('--daemonize', is_flag=True, default=False, help='run in background')
@click.option('--pid',
              type=click.Path(dir_okay=False, writable=True),
              default='/tmp/envd.pid',
              help='path to pid')
def serve(
    host: str = '',
    port: int = 0,
    env_path: str = None,
    daemonize: bool = False,
    pid: str = None,
):
    def main():
        FORMAT = '%(asctime)-15s %(clientip)s %(message)s'
        if not daemonize:
            logging.basicConfig(format=FORMAT)
            logger.setLevel(logging.INFO)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(
            aiorpcx.serve_rs(lambda *a, **kw: ServerSession(env_path, *a, **kw), host, port),
        ))
        loop.run_forever()

    if daemonize:
        daemon = Daemonize(app="envd", pid=pid, action=main)
        daemon.start()
    else:
        main()


if __name__ == '__main__':
    serve()

import hashlib, shutil, requests
from pathlib import Path
import urllib.parse
from typing import BinaryIO
import signal
import logging


def streamResource(url: str, stream: BinaryIO, chunk_size: int = 4096):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, stream, chunk_size)
        return True
    return False


def dl_file(url: str, path: str):
    with open(path, 'wb') as f:
        streamResource(url, f)


# This is not intended for security purposes. :)
# noinspection InsecureHash
def md5Stream(stream: BinaryIO, chunk_size: int = 1024) -> str:
    md5 = hashlib.md5()
    while chunk := stream.read(chunk_size):
        md5.update(chunk)
    return md5.hexdigest()


def md5File(path: str, chunk_size: int = 1024) -> str:
    with open(path, 'rb') as f:
        return md5Stream(f, chunk_size)


def getFileNameFromURL(url: str) -> str:
    return urllib.parse.unquote(Path(url).name)


class DelayedKeyboardInterrupt(object):
    """ Code stolen from:
    https://stackoverflow.com/questions/842557/how-to-prevent-a-block-of-code-from-being-interrupted-by-keyboardinterrupt-in-py
    """
    signal_received = None

    def __enter__(self):
        self.signal_received = False
        self.old_handler = signal.signal(signal.SIGINT, self.handler)

    def handler(self, sig, frame):
        self.signal_received = (sig, frame)
        logging.debug('SIGINT received. Delaying KeyboardInterrupt.')

    def __exit__(self, sig_type, value, traceback):
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            self.old_handler(*self.signal_received)

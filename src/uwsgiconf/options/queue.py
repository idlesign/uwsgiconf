from ..base import OptionsGroup


class Queue(OptionsGroup):
    """Queue.

    At the low level it is a simple block-based shared array,
    with two optional counters, one for stack-style, LIFO usage,
    the other one for FIFO.

    http://uwsgi-docs.readthedocs.io/en/latest/Queue.html

    """

    def enable(
            self,
            size: int,
            *,
            block_size: int | None = None,
            store: str | None = None,
            store_sync_interval: int | None = None
    ):
        """Enables shared queue of the given size.

        :param size: Queue size.

        :param block_size: Block size in bytes. Default: 8 KiB.

        :param store: Persist the queue into file.

        :param store_sync_interval: Store sync interval in master cycles (usually seconds).

        """
        self._set('queue', size)
        self._set('queue-blocksize', block_size)
        self._set('queue-store', store)
        self._set('queue-store-sync', store_sync_interval)

        return self._section

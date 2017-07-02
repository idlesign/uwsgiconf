from ..base import OptionsGroup
from ..variables import CPU_CORES


class MuleFarm(object):

    def __init__(self, alias, mule_numbers):
        """

        :param str|unicode alias:
        :param list[int] mule_numbers:
        """
        # todo http://uwsgi-docs.readthedocs.io/en/latest/Signals.html#signals-targets
        self.alias = alias
        self.mule_numbers = mule_numbers

    def __str__(self):
        return '%s:%s' % (self.alias, ','.join(map(str, self.mule_numbers)))


class Workers(OptionsGroup):
    """Workers aka [working] processes."""

    cls_mule_farm = MuleFarm

    def set_basic_params(self, count=None, zombie_reaper=None, limit_addr_space=None, limit_count=None,
                         cpu_affinity=None):
        """

        :param int count: Spawn the specified number of workers/processes.
            Set the number of workers for preforking mode.
            This is the base for easy and safe concurrency in your app.
            More workers you add, more concurrent requests you can manage.
            Each worker corresponds to a system process, so it consumes memory,
            choose carefully the right number. You can easily drop your system
            to its knees by setting a too high value.
            Setting ``workers`` to a ridiculously high number will *not*
            magically make your application web scale -- quite the contrary.

        :param bool zombie_reaper: call waitpid(-1,...) after each request to get rid of zombies
            Enables reaper mode. After each request the server will call ``waitpid(-1)``
            to get rid of zombie processes.
            If you spawn subprocesses in your app and you happen to end up with zombie processes
            all over the place you can enable this option. (It really would be better
            if you could fix your application's process spawning usage though.)

        :param int limit_addr_space: limit process address space (vsz) (in megabytes)
            Limits the address space usage of each uWSGI (worker) process using POSIX/UNIX ``setrlimit()``.
            For example, ``limit-as 256`` will disallow uWSGI processes to grow over 256MB of address space.
            Address space is the virtual memory a process has access to. It does *not* correspond to physical memory.
            Read and understand this page before enabling this option: http://en.wikipedia.org/wiki/Virtual_memory

        :param int limit_count: limit the number of spawnable processes

        :param int cpu_affinity: number of cores for each worker (Linux only)
            Set the number of cores (CPUs) to allocate to each worker process.

            * 4 workers, 4 CPUs, affinity is 1,
                each worker is allocated one CPU.

            * 4 workers, 2 CPUs, affinity is 1,
                workers get one CPU each (0; 1; 0; 1).

            * 4 workers, 4 CPUs, affinity is 2,
                workers get two CPUs each in a round-robin fashion (0, 1; 2, 3; 0, 1; 2; 3).

            * 8 workers, 4 CPUs, affinity is 3,
                workers get three CPUs each in a round-robin fashion
                (0, 1, 2; 3, 0, 1; 2, 3, 0; 1, 2, 3; 0, 1, 2; 3, 0, 1; 2, 3, 0; 1, 2, 3).

        """
        # todo map socket to a worker - map-socket = 0:1
        # networking.register_socket - workers_binding

        self.set_count_auto(count)
        self._set('reaper', zombie_reaper, cast=bool)

        self._set('limit-as', limit_addr_space)
        self._set('limit-nproc', limit_count)

        self._set('cpu-affinity', cpu_affinity)

        return self._section

    def set_count_auto(self, count=CPU_CORES):
        """Sets workers count.

        By default sets it to detected number of available cores

        :param int count:
        """
        self._set('workers', count)

        return self._section

    def set_thread_params(self, enable_threads=None, per_worker=None, stack_size=None):
        """

        :param bool enable_threads: Enable threads in the embedded languages.
            This will allow to spawn threads in your app.
            Threads will simply *not work* if this option is not enabled. There will likely be no error,
            just no execution of your thread code.

        :param int per_worker: Run each worker in prethreaded mode with the specified number
            of threads per worker.\n\nDo not use with ``gevent``.
            NOTE: Enables threads automatically.

        :param int stack_size: set threads stacksize

        """
        self._set('enable-threads', enable_threads, cast=bool)
        self._set('threads', per_worker)

        if per_worker:
            self._section.print_out('Threads per worker: %s' % per_worker)

        self._set('threads-stacksize', stack_size)

        return self._section

    def set_mule_params(self, mules=None, harakiri_timeout=None, farms=None):
        """

        :param int|list mules: add the specified mules or number of mules

        :param int harakiri_timeout: Set harakiri timeout for mule tasks

        :param list[MuleFarm] farms: Mule farms list.

            Examples:
                * cls_mule_farm('first', 2)
                * cls_mule_farm('first', [4, 5])

        """
        farms = farms or []

        next_mule_number = 1
        farm_mules_count = 0

        for farm in farms:

            if isinstance(farm.mule_numbers, int):
                farm.mule_numbers = list(range(next_mule_number, next_mule_number + farm.mule_numbers))
                next_mule_number = farm.mule_numbers[-1] + 1

            farm_mules_count += len(farm.mule_numbers)

            self._set('farm', farm, multi=True)

        if mules is None and farm_mules_count:
            mules = farm_mules_count

        if isinstance(mules, int):
            self._set('mules', mules)

        elif isinstance(mules, list):

            for mule in mules:
                self._set('mule', mule, multi=True)

        self._set('mule-harakiri', harakiri_timeout)

        return self._section

    def set_reload_params(self, min_lifetime=None, max_lifetime=None, max_requests=None,
                          max_addr_space=None, max_rss=None,
                          max_addr_space_forced=None, max_rss_forced=None):
        """Workers reload parameters.

        :param int min_lifetime: A worker cannot be destroyed/reloaded unless it has been alive
            for N seconds (default 60). This is an anti-fork-bomb measure.
            Since 1.9

        :param int max_lifetime: Reload workers after this many seconds. Disabled by default.
            Since 1.9

        :param int max_requests: reload workers after the specified amount of managed
            requests (avoid memory leaks)
            When a worker reaches this number of requests it will get recycled (killed and restarted).
            You can use this option to "dumb fight" memory leaks.

            Also take a look at the ``reload-on-as`` and ``reload-on-rss`` options
            as they are more useful for memory leaks.

            Beware: The default min-worker-lifetime 60 seconds takes priority over `max-requests`.

            Do not use with benchmarking as you'll get stalls
            such as `worker respawning too fast !!! i have to sleep a bit (2 seconds)...`

        :param int max_addr_space: reload a worker if its address space usage is higher
            than the specified value (in megabytes)

        :param int max_rss: reload a worker if its physical unshared memory is higher
            than the specified value (in megabytes)

        :param int max_addr_space_forced: force the master to reload a worker if its address space is higher
            than specified megabytes (in megabytes)

        :param int max_rss_forced: force the master to reload a worker if its rss memory is higher
            than specified megabytes (in megabytes)

        """
        self._set('max-requests', max_requests)

        self._set('min-worker-lifetime', min_lifetime)
        self._set('max-worker-lifetime', max_lifetime)

        self._set('reload-on-as', max_addr_space)
        self._set('reload-on-rss', max_rss)

        self._set('evil-reload-on-as', max_addr_space_forced)
        self._set('evil-reload-on-rss', max_rss_forced)

        return self._section

    def set_reload_on_exception_params(self, do_reload=None, etype=None, evalue=None, erepr=None):
        """Workers reload parameters.

        :param bool do_reload: reload a worker when an exception is raised
        :param str etype: reload a worker when a specific exception type is raised
        :param str evalue: reload a worker when a specific exception value is raised
        :param str erepr: reload a worker when a specific exception type+value (language-specific) is raised

        """
        self._set('reload-on-exception', do_reload, cast=bool)
        self._set('reload-on-exception-type', etype)
        self._set('reload-on-exception-value', evalue)
        self._set('reload-on-exception-repr', erepr)

        return self._section

    def set_harakiri_params(self, timeout=None, verbose=None, disable_for_arh=None):
        """Workers harakiri parameters.

        :param timeout: Harakiri timeout in seconds
            Every request that will take longer than the seconds specified
            in the harakiri timeout will be dropped and the corresponding
            worker is thereafter recycled.

        :param verbose: Harakiri verbose mode.
            When a request is killed by Harakiri you will get a message in the uWSGI log.
            Enabling this option will print additional info (for example,
            the current syscall will be reported on Linux platforms).

        :param disable_for_arh: Disallow Harakiri killings during after-request hook methods.

        """
        self._set('harakiri', timeout)
        self._set('harakiri-verbose', verbose)
        self._set('harakiri-no-arh', disable_for_arh)

        return self._section

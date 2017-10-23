from .workers_cheapening import *
from ..base import OptionsGroup
from ..utils import listify


class MuleFarm(object):
    """Represents a mule farm."""

    def __init__(self, name, mule_numbers):
        """
        :param str|unicode name: Farm alias.

        :param int|list[int] mule_numbers: Total mules on farm count,
            or a list of mule numbers.

        """
        # todo http://uwsgi-docs.readthedocs.io/en/latest/Signals.html#signals-targets
        self.name = name
        self.mule_numbers = mule_numbers

    def __str__(self):
        return '%s:%s' % (self.name, ','.join(map(str, self.mule_numbers)))


class Workers(OptionsGroup):
    """Workers aka [working] processes."""

    mule_farm = MuleFarm

    def set_basic_params(
            self, count=None, touch_reload=None, touch_chain_reload=None, zombie_reaper=None,
            limit_addr_space=None, limit_count=None, cpu_affinity=None):
        """

        :param int count: Spawn the specified number of workers (processes).
            Set the number of workers for preforking mode.
            This is the base for easy and safe concurrency in your app.
            More workers you add, more concurrent requests you can manage.

            Each worker corresponds to a system process, so it consumes memory,
            choose carefully the right number. You can easily drop your system
            to its knees by setting a too high value.

            Setting ``workers`` to a ridiculously high number will **not**
            magically make your application web scale - quite the contrary.

        :param str|list touch_reload: Trigger reload of (and only) workers
            if the specified file is modified/touched.

        :param str|list touch_chain_reload: Trigger chain workers reload on file touch.
            When in lazy/lazy_apps mode, you can simply destroy a worker to force it to reload the application code.
            A new reloading system named "chain reload", allows you to reload one worker at time
            (opposed to the standard way where all of the workers are destroyed in bulk)

            * http://uwsgi-docs.readthedocs.io/en/latest/articles/TheArtOfGracefulReloading.html#chain-reloading-lazy-apps

        :param bool zombie_reaper: Call waitpid(-1,...) after each request to get rid of zombies.
            Enables reaper mode. After each request the server will call ``waitpid(-1)``
            to get rid of zombie processes.
            If you spawn subprocesses in your app and you happen to end up with zombie processes
            all over the place you can enable this option. (It really would be better
            if you could fix your application's process spawning usage though.)

        :param int limit_addr_space: Limit process address space (vsz) (in megabytes)
            Limits the address space usage of each uWSGI (worker) process using POSIX/UNIX ``setrlimit()``.
            For example, ``limit-as 256`` will disallow uWSGI processes to grow over 256MB of address space.
            Address space is the virtual memory a process has access to. It does *not* correspond to physical memory.
            Read and understand this page before enabling this option: http://en.wikipedia.org/wiki/Virtual_memory

        :param int limit_count: Limit the number of spawnable processes.

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

        self._set('touch-workers-reload', touch_reload, multi=True)
        self._set('touch-chain-reload', touch_chain_reload, multi=True)

        self._set('reaper', zombie_reaper, cast=bool)

        self._set('limit-as', limit_addr_space)
        self._set('limit-nproc', limit_count)

        self._set('cpu-affinity', cpu_affinity)

        return self._section

    def run_command_as_worker(self, command, after_post_fork_hook=False):
        """Run the specified command as worker.

        :param str|unicode command:

        :param bool after_post_fork_hook: Whether to run it after `post_fork` hook.

        """
        self._set('worker-exec2' if after_post_fork_hook else 'worker-exec', command, multi=True)

        return self._section

    def set_count_auto(self, count=None):
        """Sets workers count.

        By default sets it to detected number of available cores

        :param int count:
        """
        count = count or self._section.vars.CPU_CORES

        self._set('workers', count)

        return self._section

    def set_thread_params(
            self, enable=None, count=None, count_offload=None, stack_size=None, no_wait=None):
        """Sets threads related params.

        :param bool enable: Enable threads in the embedded languages.
            This will allow to spawn threads in your app.

            .. warning:: Threads will simply *not work* if this option is not enabled.
                There will likely be no error, just no execution of your thread code.

        :param int count: Run each worker in prethreaded mode with the specified number
            of threads per worker.

            .. warning:: Do not use with ``gevent``.

            .. note:: Enables threads automatically.

        :param int count_offload: Set the number of threads (per-worker) to spawn
            for offloading. Default: 0.

            These threads run such tasks in a non-blocking/evented way allowing
            for a huge amount of concurrency. Various components of the uWSGI stack
            are offload-friendly.

            .. note:: Try to set it to the number of CPU cores to take advantage of SMP.

            * http://uwsgi-docs.readthedocs.io/en/latest/OffloadSubsystem.html

        :param int stack_size: Set threads stacksize.

        :param bool no_wait: Do not wait for threads cancellation on quit/reload.

        """
        self._set('enable-threads', enable, cast=bool)
        self._set('no-threads-wait', no_wait, cast=bool)
        self._set('threads', count)
        self._set('offload-threads', count_offload)

        if count:
            self._section.print_out('Threads per worker: %s' % count)

        self._set('threads-stacksize', stack_size)

        return self._section

    def set_mules_params(
            self, mules=None, touch_reload=None, harakiri_timeout=None, farms=None, reload_mercy=None,
            msg_buffer=None, msg_buffer_recv=None):
        """Sets mules related params.

        http://uwsgi.readthedocs.io/en/latest/Mules.html

        Mules are worker processes living in the uWSGI stack but not reachable via socket connections,
        that can be used as a generic subsystem to offload tasks.

        :param int|list mules: Add the specified mules or number of mules.

        :param str|list touch_reload: Reload mules if the specified file is modified/touched.

        :param int harakiri_timeout: Set harakiri timeout for mule tasks.

        :param list[MuleFarm] farms: Mule farms list.

            Examples:
                * cls_mule_farm('first', 2)
                * cls_mule_farm('first', [4, 5])

        :param int reload_mercy: Set the maximum time (in seconds) a mule can take
            to reload/shutdown. Default: 60.

        :param int msg_buffer: Set mule message buffer size (bytes) given
            for mule message queue.

        :param int msg_buffer: Set mule message recv buffer size (bytes).

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

        self._set('touch-mules-reload', touch_reload, multi=True)

        self._set('mule-harakiri', harakiri_timeout)
        self._set('mule-reload-mercy', reload_mercy)

        self._set('mule-msg-size', msg_buffer)
        self._set('mule-msg-recv-size', msg_buffer_recv)

        return self._section

    def set_reload_params(
            self, min_lifetime=None, max_lifetime=None,
            max_requests=None, max_requests_delta=None,
            max_addr_space=None, max_rss=None, max_uss=None, max_pss=None,
            max_addr_space_forced=None, max_rss_forced=None, watch_interval_forced=None,
            mercy=None):
        """Sets workers reload parameters.

        :param int min_lifetime: A worker cannot be destroyed/reloaded unless it has been alive
            for N seconds (default 60). This is an anti-fork-bomb measure.
            Since 1.9

        :param int max_lifetime: Reload workers after this many seconds. Disabled by default.
            Since 1.9

        :param int max_requests: Reload workers after the specified amount of managed
            requests (avoid memory leaks).
            When a worker reaches this number of requests it will get recycled (killed and restarted).
            You can use this option to "dumb fight" memory leaks.

            Also take a look at the ``reload-on-as`` and ``reload-on-rss`` options
            as they are more useful for memory leaks.

            .. warning:: The default min-worker-lifetime 60 seconds takes priority over `max-requests`.

            Do not use with benchmarking as you'll get stalls
            such as `worker respawning too fast !!! i have to sleep a bit (2 seconds)...`

        :param int max_requests_delta: Add (worker_id * delta) to the max_requests value of each worker.

        :param int max_addr_space: Reload a worker if its address space usage is higher
            than the specified value in megabytes.

        :param int max_rss: Reload a worker if its physical unshared memory (resident set size) is higher
            than the specified value (in megabytes).

        :param int max_uss: Reload a worker if Unique Set Size is higher
            than the specified value in megabytes.

            .. note:: Linux only.

        :param int max_pss: Reload a worker if Proportional Set Size is higher
            than the specified value in megabytes.

            .. note:: Linux only.

        :param int max_addr_space_forced: Force the master to reload a worker if its address space is higher
            than specified megabytes (in megabytes).

        :param int max_rss_forced: Force the master to reload a worker
            if its resident set size memory is higher than specified in megabytes.

        :param int watch_interval_forced: The memory collector [per-worker] thread memeory watch
            interval (seconds) used for forced reloads. Default: 3.

        :param int mercy: Set the maximum time (in seconds) a worker can take
            before reload/shutdown. Default: 60.

        """
        self._set('max-requests', max_requests)
        self._set('max-requests-delta', max_requests_delta)

        self._set('min-worker-lifetime', min_lifetime)
        self._set('max-worker-lifetime', max_lifetime)

        self._set('reload-on-as', max_addr_space)
        self._set('reload-on-rss', max_rss)
        self._set('reload-on-uss', max_uss)
        self._set('reload-on-pss', max_pss)

        self._set('evil-reload-on-as', max_addr_space_forced)
        self._set('evil-reload-on-rss', max_rss_forced)
        self._set('mem-collector-freq', watch_interval_forced)

        self._set('worker-reload-mercy', mercy)

        return self._section

    def set_reload_on_exception_params(self, do_reload=None, etype=None, evalue=None, erepr=None):
        """Sets workers reload on exceptions parameters.

        :param bool do_reload: Reload a worker when an exception is raised.

        :param str etype: Reload a worker when a specific exception type is raised.

        :param str evalue: Reload a worker when a specific exception value is raised.

        :param str erepr: Reload a worker when a specific exception type+value (language-specific) is raised.

        """
        self._set('reload-on-exception', do_reload, cast=bool)
        self._set('reload-on-exception-type', etype)
        self._set('reload-on-exception-value', evalue)
        self._set('reload-on-exception-repr', erepr)

        return self._section

    def set_harakiri_params(self, timeout=None, verbose=None, disable_for_arh=None):
        """Sets workers harakiri parameters.

        :param int timeout: Harakiri timeout in seconds.
            Every request that will take longer than the seconds specified
            in the harakiri timeout will be dropped and the corresponding
            worker is thereafter recycled.

        :param bool verbose: Harakiri verbose mode.
            When a request is killed by Harakiri you will get a message in the uWSGI log.
            Enabling this option will print additional info (for example,
            the current syscall will be reported on Linux platforms).

        :param bool disable_for_arh: Disallow Harakiri killings during after-request hook methods.

        """
        self._set('harakiri', timeout)
        self._set('harakiri-verbose', verbose, cast=bool)
        self._set('harakiri-no-arh', disable_for_arh, cast=bool)

        return self._section

    def set_zerg_server_params(self, socket, clients_socket_pool=None):
        """Zerg mode. Zerg server params.

        When your site load is variable, it would be nice to be able to add
        workers dynamically. Enabling Zerg mode you can allow zerg clients to attach
        to your already running server and help it in the work.

        * http://uwsgi-docs.readthedocs.io/en/latest/Zerg.html

        :param str|unicode socket: Unix socket to bind server to.

            Examples:
                * unix socket - ``/var/run/mutalisk``
                * Linux abstract namespace - ``@nydus``

        :param str|unicode|list[str|unicode] clients_socket_pool: This enables Zerg Pools.

            .. note:: Expects master process.

            Accepts sockets that will be mapped to Zerg socket.

            * http://uwsgi-docs.readthedocs.io/en/latest/Zerg.html#zerg-pools

        """
        if clients_socket_pool:
            self._set('zergpool', '%s:%s' % (socket, ','.join(listify(clients_socket_pool))), multi=True)

        else:
            self._set('zerg-server', socket)

        return self._section

    def set_zerg_client_params(self, server_sockets, use_fallback_socket=None):
        """Zerg mode. Zergs params.

        :param str|unicode|list[str|unicode] server_sockets: Attaches zerg to a zerg server.

        :param bool use_fallback_socket: Fallback to normal sockets if the zerg server is not available

        """
        self._set('zerg', server_sockets, multi=True)

        if use_fallback_socket is not None:
            self._set('zerg-fallback', use_fallback_socket, cast=bool)

            for socket in listify(server_sockets):
                self._section.networking.register_socket(self._section.networking.sockets.default(socket))

        return self._section

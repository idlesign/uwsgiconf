# uwsgify for Django

`uwsgify` adds integration with Django Framework.

First add `uwsgify` into `INSTALLED_APPS`.

```python
INSTALLED_APPS = [
    ...
    'uwsgiconf.contrib.django.uwsgify',
    ...
]
```

After that nice `uwsgi`-related staff will be available in your Django
project. For example:

-   Manage commands (see below);
-   uWSGI summary and statistics in Django Admin interface;
-   Automatic DB connections closing after `fork()`;
-   and more.

## Settings

### UWSGIFY_MODULE_INIT

`uwsgify` can import modules from your Django applications automatically
on project startup.

This is useful for background tasks (crons, timers, mules offloading) registration,
and other uwsgi stuff. E.g.:

```python
from uwsgiconf.runtime.scheduling import register_cron

@register_cron(hour=-3)  # Every 3 hours.
def repeat():
    print('hey')
```

By default `uwsgiinit.py` modules are imported.

One can change this behavior putting `UWSGIFY_MODULE_INIT=mymodule` in
Django `settings.py`. After that `uwsgify` will search for `mymodule.py`
instead of `uwsgiinit.py`.


### UWSGIFY_SKIP_TASK_ENV_VAR

Cen be used to set an environment variable name to check whether
task execution should be skipped. E.g. for temporary maintenance.

!!! note
    See notes on `@task` and decorator below.


## Tools

### Django cache

You can use uWSGI shared cache.

Just configure a backend in Django `settings.py`.

```python
CACHES = {
    "default": {
        "BACKEND": "uwsgiconf.contrib.django.uwsgify.cache.UwsgiCache",
        "LOCATION": "mycache",
    }
}
```

And don't forget to define `mycache` cache in `uwsgicfg.py`:

```python
section.caching.add_cache("mycache", max_items=100)
```

### Decorators

#### @task

This decorator is useful to give task functions (e.g. uWSGI cron, timer) superpowers.

```python
from uwsgiconf.contrib.django.uwsgify.taskutils.decorators import task
from uwsgiconf.runtime.scheduling import register_cron

@register_cron(hour=-3)
@task(cooldown=4, env_var_skip='SKIP_TASKS_RUN')
def my_task():
    ...
```

### Distributed tasks

`@task` decorator can be particularly useful to run scheduled functions exclusively 
in one datacenter (first datacenter acquired the lock is the winner). 

This implies a distributed cache, such as Redis or Database 
to store task state, including parameters and last run results.

Consecutive calls of the decorated function, when it is blocked, will be ignored
(the decorated function if called directly will return `None`).

Pass to the decorator a proper `backend` object. 

#### Cache backend

Let's say we want to use Valkey/Redis to store task locks.

We configure `myrediscache` cache in Django settings:

```python
CACHES = {
    # ...
    "myrediscache": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
    }
}
```

After that we pass `CacheBackend` to the decorator: 

```python
from uwsgiconf.contrib.django.uwsgify.taskutils.backends import CacheBackend
from uwsgiconf.contrib.django.uwsgify.taskutils.decorators import task
from uwsgiconf.runtime.scheduling import register_cron


@register_cron(minute=-10)
@task(backend=CacheBackend(cache_name='myrediscache'))
def my_task():
    ...
```

#### Database backend

Now let's suppose we need to have more control over our task, we need more context.

For that we use `DbBackend`. This not only allows exclusive task execution, 
but also is able to store task parameters and last run results.


```python
from uwsgiconf.contrib.django.uwsgify.taskutils.context import TaskContext
from uwsgiconf.contrib.django.uwsgify.taskutils.backends import DbBackend
from uwsgiconf.contrib.django.uwsgify.taskutils.decorators import task
from uwsgiconf.runtime.scheduling import register_cron


@register_cron(minute=-10)
@task(backend=DbBackend())
def my_task(*, ctx: TaskContext):  # task context is available through `ctx`
    
    if ctx.last_result.get('some') == 'other':
        # we can adjust our logic on last run results 
        ...
    
    # or we can consider parameters (can be set in Django admin)
    if ctx.params.get('save_results'):    
        # we can also store run results for further usage in next run
        ctx.result = {'some': 'other'}
```

!!! note
    Please note that for performance reasons `my_task` function needs 
    to be registered in Database beforehand. For that you can use Django Admin interface,
    or from Python (e.g. in migration file).

    ```python
    from uwsgiconf.contrib.django.uwsgify.models import Task

    Task.register('my_task', params={'a': 'b'})
    ```


## Management commands

### uwsgi_run

`uwsgi_run` management command runs uWSGI to serve your Django-based
project.

```shell
$ ./manage.py uwsgi_run

; Options are available, use --help switch to get help.
$ ./manage.py uwsgi_run --help
```

Now your project is up and running on `http://127.0.0.1:8000`.

By default the command runs your project using some defaults, but you
can configure it to your needs with the help of `uwsgicfg.py`
(constructed in a usual for **uwsgiconf** manner) placed near your
`manage.py`.

```python
from uwsgiconf.config import configure_uwsgi


def get_configurations():

    from os.path import dirname, abspath, join
    from uwsgiconf.presets.nice import PythonSection


    section = PythonSection.bootstrap(
        'http://127.0.0.1:8000',
        wsgi_module=join(dirname(abspath(__file__)), 'wsgi.py')
    )

    ...

    return section


configure_uwsgi(get_configurations)
```

!!! note
    **Embedding.** if you're using **pyuwsgi** having uWSGI and your entire
    project compiled into a single binary, and your *manage.py* is the
    entrypoint, use **\--embedded** option:
    `myproject uwsgi_run --embedded`.


### uwsgi_reload

`uwsgi_reload` management command reloads uWSGI master process, workers.

```shell
$ ./manage.py uwsgi_reload

; Options are available, use --help switch to get help.
$ ./manage.py uwsgi_reload --help
```

### uwsgi_stop

`uwsgi_stop` management command allows you to shutdown uWSGI instance.

```shell
$ ./manage.py uwsgi_stop

; Options are available, use --help switch to get help.
$ ./manage.py uwsgi_stop --help
```

### uwsgi_stats

`uwsgi_stats` management command allows you to dump uWSGI configuration
and current stats into the log.

```shell
$ ./manage.py uwsgi_stats
```

### uwsgi_log

`uwsgi_log` management command allows you to manage uWSGI log related
stuff.

```shell
$ ./manage.py uwsgi_log --rotate

; Options are available, use --help switch to get help.
$ ./manage.py uwsgi_log --help
```

### uwsgi_sysinit

`uwsgi_sysinit` management command allows you to generate system service
configs (e.g. `systemd`) to start your Django project on system start.

```shell
; Dump config to file.
$ ./manage.py uwsgi_sysinit > myapp.service

; Wire up the service config into system directory and start service
$ sudo systemctl enable --now myapp.service

; Watch application log realtime
$ sudo journalctl -fu myapp.service
```

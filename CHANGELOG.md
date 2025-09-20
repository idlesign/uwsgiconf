# uwsgiconf changelog

### Unreleased
* ++ Django Admin. Add execution duration to task list (see #15).

### v2.1.1 [2025-06-18]
* ** uwsgify. @task cooldown is now respected by short living tasks.

### v2.1.0 [2025-06-17]
* ++ uwsgify. Added 'lock_skip' parameter support for '@task'.
* ++ uwsgify. Added locking emulation.
* ** uwsgify. Fixed import when 'pkg_resources' API used.

### v2.0.0 [2025-06-10]
* !! Drop QA for Py 3.7, 3.8, 3.9.
* ++ Add 'buffer_size' option to .networking.set_basic_params().
* ++ Add privileges drop support for .configure_owner() and .set_owner_params()  (closes #9).
* ++ Add support for socket-timeout and http-timeout (closes #13).
* ++ Added custom format support for '.configure_logging_json' (closes #10).
* ++ Django. Add @task decorator with Cache and Db backends, and default 'Task' model.
* ++ Django. Added uWSGI powered cache backend.
* ++ Expose 'utils.run_uwsgi' shortcut.
* ++ Introduce uWSGI emulation for stub module to facilitate testing: caching, Farms, Mules, RPC, signals and scheduling.
* ++ Runtime. Allow Mule and Farm objects to be passed as 'target' for time and cron functions.
* ++ Runtime. Caching now can store bytes.
* ** Add QA for Py 3.11, 3.12, 3.13.
* ** Workers. .set_mules_params() now allows handling farm mules count given as a digit string (closes #6).


### v1.0.0 [2022-02-01]

* !! Python 3.6 QA is dropped.
* ** Django 4 compatibility improved.


### v0.23.0 [2021-08-31]

* !! Prepare for 1.0.0. Switch to keyword-only arguments here and there.
* ++ Django. Added 'Maintenance' section to Admin.
* ++ Section.env() now supports 'update_local' argument.
* ** uwsgify. Fix Django deprecation warning.


### v0.22.0 [2021-01-15]

* ++ Logging. Added 'fd' and 'stdio' loggers support.
* ++ Preset Nice. '.configure_certbot_https()' now accepts 'http_redirect' param.
* ++ Preset Nice. Added '.configure_logging_json()' helper.
* ** Improved support for pathlib.Path.


### v0.21.0 [2020-05-28]

* !! Dropped support for Py 2.7 and 3.5.
* !! Removed deprecated runtime.async module.
* !! Removed deprecated runtime.environ module.
* ++ Nice preset. Added .configure_https_redirect() shortcut.
* ** Fixed 'tests' packaging.
* ** Runtime .caching improved.
* ** Runtime .logging improved.
* ** Runtime .mules improved.
* ** Runtime .platform improved.
* ** Runtime .rpc improved.


### v0.20.1 [2020-01-18]

* ** Django. 'check_for_stub()' made tests-friendly (respects UWSGICONF_FORCE_STUB).
* ** Fixed uwsgify bundled uwsgiinit module loading when a custom UWSGIFY_MODULE_INIT is set.


### v0.20.0 [2019-11-21]

* ++ Django. Added 'noruntimes' and 'noerrpages' switches for 'uwsgi_run' and 'uwsgi_sysinit' commands.
* ** 'allow_shared_sockets' param of 'sockets.from_dns' and such now allows 'False'.
* ** ArgsFormatter now doesn't drop every line starting with %.
* ** ArgsFormatter. Dropped automatic escaping as not compatible with 'pyuwsgi'.


### v0.19.0 [2019-10-17]

* ++ Added SocketHttps.get_certbot_paths() helper.
* ++ Django 'uwsgi_sysinit' management command now accepts --nostatic option.
* ++ Django. Added static generic 503 page.
* ++ Networking.sockets.from_dsn() now uses shared sockets for priviledged ports when non root.
* ++ Preset Nice. Added '.configure_certbot_https()' helper.
* ++ Preset Nice. Added '.configure_maintenance_mode()' helper.
* ++ Preset Nice. Added '.get_bundled_static_path()' helper.
* ++ Runtime. Added Farms introspection utilities.
* ** 'RouteRule' 'subject' argument now defaults to 'None'. String subjects are considered to be path-info.
* ** Runtime. 'ConfigurationError' not raised on spooler import anymore.
* ** Runtime. Improved values decoding for Py3.
* ** Sysinit. Fixed 'install' command path.
* ** Sysinit. Systemd. Changed Wants and After targets.


### v0.18.1 [2019-09-22]

* ** Args formatter now uses escaping.
* ** Raise an exception when checking for a stub in 'uwsgiinit'.


### v0.18.0

* ++ Runtime. Added Spooler-related stuff.
* ++ Runtime. Scheduling. Added 'register_timer_ms()'.
* ++ Runtime. Signals. Signal objects now can be used as decorators.
* ++ Spooler. Introduced 'base_dir' for 'set_basic_params()'.
* ** Django. Embedded mode support improved.
* ** Runtime. RPC. Fixed 'make_rpc_call()'.
* ** Stub file enriched.



### v0.17.0

* !! Dropped QA for Python 2.
* !! Runtime. '.environ' module is deprecated in favor of '.platform'.
* !! Stub updated with return values.
* ++ Django. Added uwsgiinit modules autodiscover for applications.
* ++ Django. Basic uWSGI information exposed via Admin contrib.
* ++ Runtime. Added postfork functions support.
* ++ Runtime. Added signals registry for introspection.
* ++ Runtime. Cache '.set()' now accepts 'timeout' argument.
* ++ Runtime. Mules module extended, including function offloading support.
* ** Django. Fixed uwsgify default config loading.
* ** Fixed 'is_stub' attribute binding to uwsgi/uwsgi_stub modules.
* ** Fixed argument 'expires' behaviour for 'caching.add_cache()' and renamed into 'no_expire'.
* ** Runtime. Cache. Fixed '.div()' behaviour.
* ** Runtime. Fixed 'environ.uwsgi_env.buffer_size' value.
* ** Runtime. Signals. Fixed Signal.send() for non-remotes.


### v0.16.0

* ++ Added ArgsFormatter (repesent options as command line args).
* ++ Added Networking.sockets.from_dsn() as a shortcut for socket construction.
* ++ Added Section.bootstrap() shortcut.
* ++ Config.format() now supports formatter aliasing.
* ++ Django contrib. 'uwsgi_run' command now allows embedded runs.
* ++ Introduced pyuwsgi compatibility.
* ** Django contrib. Py2 compatibility improved.


### v0.15.3

* ** Django contrib compatibility improved.


### v0.15.2

* !! runtime.async module is deprecated if favor of runtime.asynced.
* ** Added QA for py3.7.
* ** Dropped QA for py<3.5.


### v0.15.1

* ** Django contrib. Fixed wsgi app file discovery for autogenerated section.
* ** Django contrib. Use temporary dir when STATIC_DIR is not set.


### v0.15.0

* ++ Added basic integration with Django Framework.
* ++ Added Fifo utility.
* ++ Added Finder utility.
* ++ Application. Added support for 'manage_script_name' option.
* ++ CLI. Added 'sysinit' command to generate Systemd and Upstart configs.
* ++ Main process. Added 'get_owner()' method.
* ++ Master. FIFO filepath now supports placeholders'.
* ++ Metrics. Store directory now supports placeholders'.
* ++ Networking. Unix sockets filepaths now support placeholders.
* ++ Routing. Added '.set_error_pages()' shortcut method.
* ++ Sections now support setting of 'runtime_dir' and 'project_name'.
* ++ Spooler. Work directory now supports placeholders.
* ** Routing. Renamed '.print_routes()' -> '.print_routing_rules()'.


### v0.14.2

* ** Fixed SocketHttps construction.


### v0.14.1

* ** Fixed register_cron() work with periods.


### v0.14.0

* !! Dropped support for py 3.3.
* ++ Runtime. register_cron() now handles periods.


### v0.13.0

* ** Runtime. 'signal_or_target' parameter is renamed into 'target'.
* ** Term 'backlog' is changed into '[listen] queue' for consistency.
* ** Fixed touch reload from py configuration file.
* ++ Nice preset extended with 'get_log_format_default()' demo helper method.
* ++ Implemented 'logging.vars.request_var' and 'logging.vars.metric'
* ** Renamed several .logging.vars.
* ** Fixed .logging 'prefix_date' parameter handling.
* ** Fixed .logging  parameter handling.
* ++ Nice preset. Added 'ignore_write_errors' shortcut support.
* ++ CLI. Added headers related methods to routing options group.
* ++ Added 'master_process.set_exception_handling_params'.
* ** 'Logging.set_filters' split into 'set_filters' and 'set_requests_filters'.
* ** Signal.register_handler target now defaults to 'worker'.


### v0.12.0

* ** Runtime. Farm.is_in renamed into Farm.is_mine.
* ** Runtime. Cache improved.
* ** Runtime. Metric is now OOP.
* ++ Nice presets now accept 'log_dedicated' arg
* ** change_dir() moved from Applications into Main process.
* ++ Improved cheapening abstractions.
* ++ Added empire.Broodlord preset


### v0.11.0

* ++ Added support for multiple configurations in one module.
* ++ Configuration now accepts 'alias' param.
* ** Nice preset. Threads are now on by default for PythonSection.
* ++ Sockets and Routers reworked.


### v0.10.0

* ++ Added 'runtime' package preview.
* ++ Nice presets now accept 'process_prefix' arg


### v0.9.0

* ++ Nice presets now accept 'log_into' arg
* ** Nice Python preset now requires an app by default
* ++ Nice presets now accept 'owner' arg
* ++ Nice presets 'threads' arg now accepts bool
* ++ Nice presets now use SIGTERM for uWSGI shutdown
* ++ Added Logging.log_into method
* ** Logger alias made optional
* ++ Introduced dedicated routers.


### v0.8.0

* ++ Subscriptions-related options partially described.
* ++ More worker-related options described.
* ++ More Python-related options described.
* ++ rsyslog logger made separate from syslog.
* ++ CLI: Added 'probe_plugins' command.
* ++ Linux KSM option described.
* ++ GeoIP param described.


### v0.7.0

* ++ Introduced Python uwsgi stub module.


### v0.6.0

* ++ CLI: implemented 'run' command.
* ** Routing modifier names now follow common pattern.


### v0.5.0

* ++ Introduced CLI with basic 'compile' command
* ++ Nice preset: harakiri made verbose.
* ++ Introduced routing modifiers.


### v0.4.0

* ++ Added 'embedded_plugins' arg for PythonSection.
* ++ Added support for embedded plugins.
* ** Fixed Carbon pusher
* ** Plugin search_dirs now precedes plugins.


### v0.3.0

* ++ Statics options group partially described.
* ++ A bunch of new actions for hooks described.


### v0.2.0

* ++ Internal routing options group partially described.
* ++ Cheapening options group described.


### v0.1.1

* ** First public release.


### v0.1.0

* ++ Basic functionality.
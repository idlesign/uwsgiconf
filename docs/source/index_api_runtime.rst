Configuration [Dynamic/Runtime]
===============================


**uwsgiconf** comes with ``runtime`` package which is similar to **uwsgidecorators** but offers different
abstractions to provide useful shortcuts and defaults.

Various modules from that package can be imported and used runtime to configure different aspects of **uWSGI**,
such as `caching`, `locks`, `signals`, `spooler`, `rpc`, etc.


.. toctree::
    :maxdepth: 3

    run_alarms
    run_asynced
    run_caching
    run_control
    run_locking
    run_logging
    run_monitoring
    run_mules
    run_platform
    run_rpc
    run_scheduling
    run_signals
    run_spooler

# Introduction

*Configure uWSGI from your Python code*

If you think you know uWSGI you're probably wrong. It is always more
than you think it is. There are so many subsystems and
[options](http://uwsgi-docs.readthedocs.io/en/latest/Options.html)
(800+) it is difficult to even try to wrap your mind around.

**uwsgiconf** allowing to define uWSGI configurations in Python tries to
improve things the following ways:

-   It structures options for various subsystems using classes and
    methods;
-   It uses docstrings and sane naming to facilitate navigation;
-   It ships some useful presets to reduce boilerplate code;
-   It encourages configuration reuse;
-   It comes with CLI to facilitate configuration;
-   It features easy to use and documented **uwsgi stub** Python module;
-   It offers **runtime** package, similar to **uwsgidecorators**, but
    with more abstractions;
-   It features integration with Django Framework;
-   It is able to generate configuration files for Systemd, Upstart.
-   It can use `pyuwsgi`.

*Consider using IDE with autocompletion and docstings support to be more
productive with uwsgiconf.*

By that time you already know that **uwsgiconf** is just another
configuration method.
[Why](http://uwsgi-docs.readthedocs.io/en/latest/FAQ.html#why-do-you-support-multiple-methods-of-configuration)?

## Requirements

1.  Python 3.9+
2.  `click` package (optional, for CLI)
3.  uWSGI (`uwsgi` or `pyuwsgi`)

## Get involved into uwsgiconf

!!! success "Submit issues"
    If you spotted something weird in application behavior or want to propose a feature you can do 
    that at <https://github.com/idlesign/uwsgiconf/issues>

!!! tip "Write code"
    If you are eager to participate in application development, 
    fork it at <https://github.com/idlesign/uwsgiconf>, write 
    your code, whether it should be a bugfix or a feature implementation,
    and make a pull request right from the forked project page.

!!! info "Spread the word"
    If you have some tips and tricks or any other words in mind that 
    you think might be of interest for the others --- publish it.

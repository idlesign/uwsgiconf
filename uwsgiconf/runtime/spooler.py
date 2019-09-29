import os
import pickle
from calendar import timegm
from datetime import datetime, timedelta

from .. import uwsgi
from ..utils import listify, get_logger, encode, decode, decode_deep

_LOG = get_logger(__name__)

_MSG_MAX_SIZE = 64 * 1024  # 64 Kb https://uwsgi-docs.readthedocs.io/en/latest/Spooler.html#spool-files


_task_functions = {}


def _get_spoolers():
    return decode_deep(listify(uwsgi.opt.get('spooler', [])))


def _register_task(spooler_obj, spooler_cls):
    """

    :param Spooler spooler_obj:
    :param Spooler spooler_cls:

    """
    def _register_task_(priority=None, postpone=None):
        # This one is returned by `_HandlerRegisterer`

        def task_decorator(func):
            # This one handles decoration with `Spooler.register_handler`.

            func_name = func.__name__

            _task_functions[func_name] = func

            _LOG.debug('Spooler. Registered function: %s', func_name)

            def task_call(*args, **kwargs):
                # Redirect task (function call) into spooler.

                return spooler_cls.send_message_raw(**SpoolerFunctionCallTask.build_message(
                    spooler=spooler_obj.name if spooler_obj else None,
                    priority=priority,
                    postpone=postpone,
                    payload={
                        'func': func_name,
                        'arg': args,
                        'kwg': kwargs,
                    }
                ))

            return task_call

        return task_decorator

    return _register_task_


class _TaskRegisterer(object):
    # Allows task decoration using both Spooler class and object.

    def __get__(self, instance, owner):
        return _register_task(instance, owner)

    def __call__(self, priority=None, postpone=None):
        """Decorator. Used to register a function which should be run in Spooler.

        :param int priority: Number. The priority of the message. Larger - less important.

            .. warning:: This works only if you enable `order_tasks` option in `spooler.set_basic_params()`.

        :param datetime|timedelta postpone: Postpone message processing till.
        """
        # Mirrors `_register_task_` arguments for IDEs ho get proper hints.


class Spooler(object):
    """Gives an access to uWSGI Spooler related functions.

    .. warning:: To use this helper one needs
        to configure spooler(s) in uWSGI config beforehand.

    .. code-block:: python

        my_spooler = Spooler.get_by_basename('myspooler')

        # @Spooler.task() to  run on first available or to run on `my_spooler`:
        @my_spooler.task(postpone=timedelta(seconds=1))
        def run_me(a, b='c'):
            ...

        # Now call this function as usual and it'll run in a spooler.
        ...
        run_me('some', b='other')
        ...


    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    task = _TaskRegisterer()
    """Decorator. Used to register a function which should be run in Spooler.
    
    .. code-block:: python
       
        my_spooler = Spooler.get_by_basename('myspooler')
        
        # @Spooler.task() to  run on first available or to run on `my_spooler`:
        @my_spooler.task(postpone=timedelta(seconds=1))  
        def run_me(a, b='c'):
            ...
    
    """

    @classmethod
    def send_message_raw(cls, message, spooler=None, priority=None, postpone=None, payload=None):
        """Sends a message to a spooler.

        :param str msg: Message to pass using spooler.

        :param str|Spooler spooler: The spooler (id or directory) to use.
            Specify the ABSOLUTE path of the spooler that has to manage this task

        :param int priority: Number. The priority of the message. Larger - less important.

            .. warning:: This works only if you enable `order_tasks` option in `spooler.set_basic_params()`.

        :param datetime|timedelta postpone: Postpone message processing till.

        :param payload: Object to pickle and pass within message.

        :rtype: str

        """
        msg = {
            'msg': message,
        }

        if spooler:

            if isinstance(spooler, Spooler):
                spooler = spooler.name

            msg['spooler'] = spooler

        if priority:
            msg['priority'] = str(priority)

        if postpone:

            if isinstance(postpone, timedelta):
                postpone += datetime.utcnow()

            if isinstance(postpone, datetime):
                postpone = timegm(postpone.timetuple())

            msg['at'] = postpone

        body = {}

        if payload:
            body['payload'] = payload

        if len(repr(msg)) >= _MSG_MAX_SIZE:
            # Message is too large move into body.
            body['msg'] = msg.pop('msg')

        if body:
            msg['body'] = pickle.dumps(body)

        return uwsgi.send_to_spooler(_msg_encode(msg))

    _valid_task_results = {uwsgi.SPOOL_OK, uwsgi.SPOOL_RETRY, uwsgi.SPOOL_IGNORE}

    @classmethod
    def _process_message_raw(cls, envelope):
        decoded = _msg_decode(envelope)

        task_name = decoded['spooler_task_name']
        msg = decoded.get('msg')
        body = decoded.get('body')

        payload = None

        if body:
            body = pickle.loads(body)
            if not msg:
                msg = body.get('msg')
            payload = body.get('payload')

        task_cls = SpoolerTask

        if msg.startswith('ucfg_'):
            message_type_id = msg.replace('ucfg_', '', 1)
            task_cls = spooler_task_types.get(message_type_id, SpoolerTask)

        task = task_cls(
            name=task_name,
            message=msg,
            payload=payload,
        )

        try:
            result = task.process()

        except Exception as e:
            _LOG.exception('Spooler. Unhandled exception in task %s', task_name)
            result = ResultRescheduled(exception=e)

        if result is None:
            result = ResultSkipped(result)

        elif not isinstance(result, TaskResult):
            result = ResultProcessed(result)

        return result.code_uwsgi

    @classmethod
    def get_spoolers(cls):
        """Returns a list of registered spoolers.

        :rtype: list[Spooler]
        """
        return [Spooler(spooler_dir) for spooler_dir in _get_spoolers()]

    @classmethod
    def get_by_basename(cls, name):
        """Returns spooler object for a given directory name.

        If there is more than one spooler with the same directory base name,
        the first one is returned.

        If not found `None` is returned.

        :param str name: Directory base name. E.g.: 'mydir' to get spooler for '/somewhere/here/is/mydir'
        :rtype: Spooler|None
        """
        spooler = None
        basename = os.path.basename

        for spooler_dir in _get_spoolers():
            if basename(spooler_dir) == name:
                spooler = Spooler(spooler_dir)
                break

        return spooler

    @classmethod
    def get_pids(cls):
        """Returns a list of all spooler processes IDs.

        :rtype: list
        """
        return uwsgi.spooler_pids()

    @classmethod
    def set_period(cls, seconds):
        """Sets how often the spooler runs.

        :param int seconds:
        :rtype: bool
        """
        return uwsgi.set_spooler_frequency(seconds)

    @classmethod
    def get_tasks(cls):
        """Returns a list of spooler jobs (filenames in spooler directory).

        :rtype: list[str]
        """
        return uwsgi.spooler_jobs()

    @classmethod
    def read_task_file(cls, path):
        """Returns a spooler task information.

        :param str path: The relative or absolute path to the task to read.
        :rtype: dict
        """
        return uwsgi.spooler_get_task(path) or {}


class TaskResult(object):
    """Represents a task processing result."""

    code_uwsgi = None

    def __init__(self, result=None, exception=None):
        self.result = result
        self.exception = exception


class ResultProcessed(TaskResult):
    """Treat task as processed."""

    code_uwsgi = uwsgi.SPOOL_OK


class ResultSkipped(TaskResult):
    """Treat task as skipped (ignored)."""

    code_uwsgi = uwsgi.SPOOL_IGNORE


class ResultRescheduled(TaskResult):
    """Treat task as rescheduled (being due to retry)."""

    code_uwsgi = uwsgi.SPOOL_RETRY


class SpoolerTask(object):
    """Consolidates information for a spooler task."""

    mark_processed = ResultProcessed
    mark_skipped = ResultSkipped
    mark_rescheduled = ResultRescheduled

    __slots__ = ['name', 'message', 'payload']

    type_id = ''

    def __init__(self, name, message, payload):
        self.name = name
        self.message = message
        self.payload = payload

    def process(self):
        """Processes the task.

        Supported results:
            * `None` - mark as ignored (skipped)
            * `TaskResult` - result type logic
            * exception - mark to retry
            * other - mark as processed

        :rtype: TaskResult|None|bool
        """
        return True

    @classmethod
    def build_message(cls, spooler, priority, postpone, payload=None):

        payload_ = {
            'spooler': spooler,
            'priority': priority,
            'postpone': postpone,
        }

        payload_.update(payload or {})

        msg = dict(
            message='ucfg_%s' % cls.type_id,
            spooler=spooler,
            priority=priority,
            postpone=postpone,
            payload=payload_,
        )
        return msg


class SpoolerFunctionCallTask(SpoolerTask):
    """Function call type. Allows delegating function calls to spoolers."""

    type_id = 'fcall'

    __slots__ = ['name', 'message', 'payload']

    def process(self):
        payload = self.payload
        func = _task_functions[payload['func']]  # We expect an exception here if not registered.
        result = func(*payload['arg'], **payload['kwg'])
        return result


# todo Py3.6+ use __init_subclass__
spooler_task_types = {task_type.type_id: task_type for task_type in [
    SpoolerFunctionCallTask,
]}
"""Known task types handlers will store here runtime."""


def _msg_encode(msg):
    """
    :param dict msg:
    :rtype: dict
    """
    return {encode(k): encode(v) for k, v in msg.items()}


def _msg_decode(msg):
    """
    :param dict msg:
    :rtype: dict
    """
    decoded = {}

    for k, v in msg.items():
        k = decode(k)
        if k != 'body':  # Consider body always pickled.
            v = decode(v)
        decoded[k] = v

    return decoded


uwsgi.spooler = Spooler._process_message_raw

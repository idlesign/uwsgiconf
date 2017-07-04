from collections import OrderedDict


VERSION = '%V'
'''uWSGI version number'''

FORMAT_ESCAPE = '%['
'''ANSI escape \\033. useful for printing colors'''

FORMAT_END = '%s[0m' % FORMAT_ESCAPE

CONF_CURRENT_SECTION = '%x'
'''The current section identifier, eg. conf.ini:section.'''
CONF_CURRENT_SECTION_NTPL = '%x'

CONF_NAME_ORIGINAL = '%o'
'''The original conf filename, as specified on the command line'''
CONF_NAME_ORIGINAL_NTPL = '%O'

TIMESTAMP_STARTUP_S = '%t'
'''Unix time s, gathered at instance startup.'''
TIMESTAMP_STARTUP_MS = '%T'
'''Unix time ms, gathered at instance startup'''

DIR_VASSALS = '%v'
'''Vassals directory - pwd.'''

HOST_NAME = '%h'
'''Host name.'''
CPU_CORES = '%k'
'''Detected CPU count.'''

USER_ID = '%u'
'''User ID.'''
USER_NAME = '%U'
'''User name.'''

GROUP_ID = '%g'
'''Use group ID.'''
GROUP_NAME = '%G'
'''Use group name.'''


def get_descriptions():
    """Returns variable to description mapping.

    :rtype: dict
    """
    descriptions = {
        DIR_VASSALS: 'the vassals directory - pwd',
        VERSION: 'the uWSGI version',
        HOST_NAME: 'the hostname',
        CONF_NAME_ORIGINAL: 'the original conf filename, as specified on the command line',
        CONF_NAME_ORIGINAL_NTPL: 'as %o but for first non-template conf',
        '%p': 'the absolute path of the conf',
        '%P': 'as %p but for first non-template conf',
        '%s': 'the filename of the conf',
        '%S': 'as %s but for first non-template conf',
        '%d': 'the absolute path of the directory containing the conf',
        '%D': 'as %d but for first non-template conf',
        '%e': 'the extension of the conf',
        '%E': 'as %e but for first non-template conf',
        '%n': 'the filename without extension',
        '%N': 'as %n but for first non-template conf',
        '%c': 'the name of the directory containing the conf file',
        '%C': 'as %c but for first non-template conf',
        TIMESTAMP_STARTUP_S: 'unix time s, gathered at instance startup',
        TIMESTAMP_STARTUP_MS: 'unix time ms, gathered at instance startup',
        CONF_CURRENT_SECTION: 'the current section identifier, eg. conf.ini:section',
        '%X': 'as %x but for first non-template conf',
        '%i': 'inode number of the file',
        '%I': 'as %i but for first non-template conf',
        FORMAT_ESCAPE: 'ANSI escape \\033. useful for printing colors',
        CPU_CORES: 'detected cpu cores',
        USER_ID: 'uid of the user',
        USER_NAME: 'username or fallback to uid of the user',
        GROUP_ID: 'gid of the user',
        GROUP_NAME: 'group name or fallback to gid of the user',
        '%j': 'HEX representation of the djb33x hash of the full conf path',
        '%J': 'as %j but for first non-template conf',
    }

    descriptions = sorted(descriptions.items(), key=lambda item: item[0].lower())

    return OrderedDict(descriptions)

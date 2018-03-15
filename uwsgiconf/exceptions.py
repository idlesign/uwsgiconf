
class UwsgiconfException(Exception):
    pass


class ConfigurationError(UwsgiconfException):
    pass


class RuntimeConfigurationError(ConfigurationError):
    pass

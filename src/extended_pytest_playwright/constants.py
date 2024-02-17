from dataclasses import dataclass


@dataclass(frozen=True)
class State:
    ON: str = 'on'
    OFF: str = 'off'
    ONLY_ON_FAILURE: str = 'only-on-failure'
    RETAIN_ON_FAILURE: str = 'retain-on-failure'


@dataclass(frozen=True)
class Browser:
    CHROMIUM: str = 'chromium'
    FIREFOX: str = 'firefox'
    WEBKIT: str = 'webkit'


@dataclass(frozen=True)
class BrowserChannel:
    CHROME: str = 'chrome'
    MSEDGE: str = 'msedge'


@dataclass(frozen=True)
class LogCli:
    CRITICAL: str = 'CRITICAL'
    ERROR: str = 'ERROR'
    WARNING: str = 'WARNING'
    INFO: str = 'INFO'
    DEBUG: str = 'DEBUG'


@dataclass(frozen=True)
class RunTestBy:
    MARK: str = '-m'
    NAME: str = '-k'
    FILE: str = 'file'

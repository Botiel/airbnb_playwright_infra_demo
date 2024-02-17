from pathlib import Path
from dataclasses import astuple
from datetime import datetime as dt
from pydantic import BaseModel, Field, ConfigDict, field_validator, ValidationInfo
from .constants import (
    RunTestBy,
    Browser,
    BrowserChannel,
    State,
    LogCli
)


ROOT = Path(__file__).resolve().parent.parent

MODEL_CONFIG = ConfigDict(
    strict=True,
    validate_default=False,
    validate_return=True,
    validate_assignment=True
)


class ViewPort(BaseModel):
    height: int = Field(ge=100)
    width: int = Field(ge=100)


class RunTestObject(BaseModel):
    model_config = MODEL_CONFIG
    run_by: str | None = Field(default=None)
    tests: list[str] = []

    @field_validator('run_by')
    @classmethod
    def check_run_by(cls, v: str | None, info: ValidationInfo) -> str | None:
        if isinstance(v, str):
            args = astuple(RunTestBy())
            assert v in args, f'{info.field_name} must be on of: {args}'
            return v


class PytestConfigurationsBase(BaseModel):
    model_config = MODEL_CONFIG

    # Credentials
    password: str
    username: str
    base_url: str

    # Test setup
    headed: bool
    tracing: str
    video: str
    screenshot: str
    full_page_screenshot: bool
    viewport: ViewPort
    browsers: list[str] = []
    browser_channel: str | None = Field(default=None)
    device: str | None = Field(default=None)
    log_cli_level: str
    workers: int = Field(default=1, gt=0, lt=5)

    # General context configurations
    ignore_https_errors: bool
    navigation_timeout: int = Field(default=45 * 1000, ge=10 * 1000)
    default_timeout: int = Field(default=5000, ge=2000)
    clipboard_permissions: bool
    use_storage_state: bool

    # General
    root_folder: Path
    reports_folder_pattern: Path

    @field_validator('screenshot', 'video', 'tracing')
    @classmethod
    def check_artifacts(cls, v: str, info: ValidationInfo) -> str:

        if info.field_name == 'screenshot':
            args = [State.ON, State.OFF, State.ONLY_ON_FAILURE]
        else:
            args = [State.ON, State.OFF, State.RETAIN_ON_FAILURE]

        assert v in args, f'{info.field_name} must be one of: {args}'

        return v

    @field_validator('base_url')
    @classmethod
    def check_base_url(cls, v: str, info: ValidationInfo) -> str:
        assert v.startswith('https://'), f'{info.field_name} must start with https://'
        return v

    @field_validator('browsers')
    @classmethod
    def check_browsers(cls, v: list[str], info: ValidationInfo) -> list[str]:
        browsers = astuple(Browser())
        for browser in v:
            assert browser in browsers, f'{info.field_name} must be on of: {browsers}'
        return v

    @field_validator('browser_channel')
    @classmethod
    def check_browser_channel(cls, v: str | None, info: ValidationInfo) -> str | None:
        if isinstance(v, str):
            channels = astuple(BrowserChannel())
            assert v in channels, f'{info.field_name} must be on of: {channels}'
            return v

    @field_validator('log_cli_level')
    @classmethod
    def check_log_cli_level(cls, v: str, info: ValidationInfo) -> str:
        log = astuple(LogCli())
        assert v in log, f'{info.field_name} must be on of: {log}'
        return v

    def extend_reports_folder_name(self, test_name: str) -> str:
        date = dt.now().strftime('%d-%m-%Y')
        time = dt.now().strftime('%H-%M-%S')
        output = str(self.reports_folder_pattern)
        return f'{output}-{test_name}-{date}_{time}'

    def generate_cli_args_from_configurations(self, test_name: str) -> list[str]:

        reports_folder = self.extend_reports_folder_name(test_name)

        # html report is disabled due to some issue with parallel execution
        args = [
            # '--template=html1/index.html',
            '--json-report',
            '--json-report-indent=4',
            '--root-folder', str(self.root_folder),
            '--output', reports_folder,
            # '--report', f'{reports_folder}/report.html',
            '--junitxml', f'{reports_folder}/report.xml',
            '--json-report-file', f'{reports_folder}/report.json',
            '--default-timeout', str(self.default_timeout),
            '--navigation-timeout', str(self.navigation_timeout),
            '--viewport', str(self.viewport.width), str(self.viewport.height),
            '--tracing', self.tracing,
            '--video', self.video,
            '--screenshot', self.screenshot,
            '--log-cli-level', self.log_cli_level,
            '--password', self.password,
            '--username', self.username,
            '--base-url', self.base_url,
            '-n', str(self.workers)
        ]

        if self.headed:
            args.append('--headed')

        if self.ignore_https_errors:
            args.append('--ignore-https-errors')

        for browser in self.browsers:
            args.extend(['--browser', browser])

        if self.browser_channel:
            args.extend(['--browser-channel', self.browser_channel])

        if self.full_page_screenshot:
            args.append('--full-page-screenshot')

        if self.device:
            args.append('--device')

        if self.use_storage_state:
            args.append('--use-storage-state')

        if self.clipboard_permissions:
            args.append('--clipboard-permissions')

        return args

    @classmethod
    def generate_configurations_template_object(cls, **kwargs):
        data = dict(
            base_url='https://localhost',
            username='admin',
            password='admin',
            headed=False,
            log_cli_level=LogCli.DEBUG,
            browsers=[Browser.CHROMIUM],
            tracing=State.RETAIN_ON_FAILURE,
            video=State.RETAIN_ON_FAILURE,
            screenshot=State.ONLY_ON_FAILURE,
            full_page_screenshot=False,
            viewport=ViewPort(height=900, width=1600),
            navigation_timeout=60 * 1000,
            default_timeout=10 * 1000,
            ignore_https_errors=True,
            use_storage_state=True,
            clipboard_permissions=True,
            root_folder=ROOT,
            reports_folder_pattern=ROOT / 'pytest_reports' / 'test-report',
        )

        if kwargs:
            data.update(kwargs)

        return cls(**data)

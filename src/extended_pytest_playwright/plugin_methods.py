
import logging
import pytest
import os
from pathlib import Path
from playwright.sync_api import Browser, BrowserContext, Page, Error
from typing import Optional, Literal


def build_artifact_test_folder(
        pytestconfig: pytest.Config,
        request: pytest.FixtureRequest,
        file_name: str,
        test_setup_result: Optional[str] = None
) -> str:

    output_dir = pytestconfig.getoption("--output")
    root = pytestconfig.getoption("--root-folder")

    report = request.node.reportinfo()
    full_path = str(report[0])

    folder_test_name = full_path.replace(root, '').replace('/', '.').replace('.py', '')
    folder_test_name = folder_test_name[1:]

    if test_setup_result:
        return os.path.join(output_dir, f"{folder_test_name}.base_test_setup", file_name)

    test_name = str(report[2]).replace('[', '_').replace(']', '')
    folder_test_name = f'{folder_test_name}.{test_name}'
    return os.path.join(output_dir, folder_test_name, file_name)


def handle_artifacts(
        context: BrowserContext,
        pytestconfig: pytest.Config,
        request: pytest.FixtureRequest,
        pages: list[Page],
        test_setup_result: Optional[Literal["failed", "passed"]] = None
) -> None:
    if test_setup_result:
        failed = True if test_setup_result == "failed" else False
        status = test_setup_result
    else:
        # If request.node is missing rep_call, then some error happened during execution
        # that prevented teardown, but should still be counted as a failure
        failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else True
        status = "failed" if failed else "passed"

    tracing_option = pytestconfig.getoption("--tracing")
    capture_trace = tracing_option in ["on", "retain-on-failure"]
    if capture_trace:
        retain_trace = tracing_option == "on" or (failed and tracing_option == "retain-on-failure")
        if retain_trace:
            trace_path = build_artifact_test_folder(
                pytestconfig,
                request,
                f"trace_{status}.zip",
                test_setup_result
            )
            context.tracing.stop(path=trace_path)
        else:
            context.tracing.stop()

    screenshot_option = pytestconfig.getoption("--screenshot")
    capture_screenshot = screenshot_option == "on" or (failed and screenshot_option == "only-on-failure")
    if capture_screenshot:
        for index, page in enumerate(pages):
            screenshot_path = build_artifact_test_folder(
                pytestconfig,
                request,
                f"screenshot-{status}-{index + 1}.png",
                test_setup_result
            )
            try:
                page.screenshot(
                    timeout=5000,
                    path=screenshot_path,
                    full_page=pytestconfig.getoption("--full-page-screenshot"),
                )
            except Error:
                pass

    context.close()

    video_option = pytestconfig.getoption("--video")
    preserve_video = video_option == "on" or (failed and video_option == "retain-on-failure")
    if preserve_video:
        for index, page in enumerate(pages):
            video = page.video
            if not video:
                continue
            try:
                video_path = build_artifact_test_folder(
                    pytestconfig,
                    request,
                    f"video-{status}-{index + 1}.webm",
                    test_setup_result
                )
                video.save_as(path=video_path)
            except Error:
                # Silent catch empty videos.
                pass


def init_context(
        browser: Browser,
        browser_context_args: dict,
        pytestconfig: pytest.Config,
        request: pytest.FixtureRequest,
        browser_name: str,
        storage_state: Path | None = None
) -> tuple[BrowserContext, list[Page]]:
    pages: list[Page] = []
    browser_context_args = browser_context_args.copy()
    context_args_marker = next(request.node.iter_markers("browser_context_args"), None)
    additional_context_args = context_args_marker.kwargs if context_args_marker else {}
    browser_context_args.update(additional_context_args)

    viewport_option = request.config.getoption('--viewport')[0]
    viewport = {
        "width": int(viewport_option[0]),
        "height": int(viewport_option[1])
    }

    context = browser.new_context(
        **browser_context_args,
        storage_state=storage_state,
        viewport=viewport,
        record_video_size=viewport,
        ignore_https_errors=request.config.getoption('--ignore-https-errors')
    )
    context.on("page", lambda page: pages.append(page))

    tracing_option = pytestconfig.getoption("--tracing")
    capture_trace = tracing_option in ["on", "retain-on-failure"]
    if capture_trace:
        try:
            title = request.node.reportinfo()[2]
        except Exception as e:
            logging.error(f'something went wrong with obtaining test name: {e}')
            title = 'tracing'
        context.tracing.start(
            title=title,
            screenshots=True,
            snapshots=True,
            sources=True,
        )

    context.set_default_timeout(timeout=int(request.config.getoption('--default-timeout')))
    context.set_default_navigation_timeout(timeout=int(request.config.getoption('--navigation-timeout')))

    if browser_name == "chromium" and request.config.getoption('--clipboard-permissions'):
        context.grant_permissions(['clipboard-write', 'clipboard-read'])

    return context, pages


def create_extended_options(parser: pytest.Parser) -> None:
    group = parser.getgroup("extended-playwright", "Extended-Playwright")
    group.addoption(
        '--username',
        action='store',
        default=None
    )
    group.addoption(
        '--password',
        action='store',
        default=None
    )
    group.addoption(
        '--viewport',
        action='append',
        nargs=2, type=int,
        default=[]
    )
    group.addoption(
        '--ignore-https-errors',
        action='store_true',
        default=False
    )
    group.addoption(
        '--clipboard-permissions',
        action='store_true',
        default=False
    )
    group.addoption(
        '--navigation-timeout',
        action='store',
        type=int,
        default=60 * 1000
    )
    group.addoption(
        '--default-timeout',
        action='store',
        type=int,
        default=15 * 1000
    )
    group.addoption(
        '--root-folder',
        action='store',
        default=None
    )
    group.addoption(
        '--use-storage-state',
        action='store_true',
        default=False
    )

    group.addoption(
        '--use-pycharm-debugger-args',
        action='store_true',
        default=False
    )

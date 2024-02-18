 * working with python version: 3.11.0
 * docker image built from: mcr.microsoft.com/playwright/python:v1.41.0-jammy
 * playwright trace viewer: https://trace.playwright.dev/
 * playwright python docs: https://playwright.dev/docs/intro


# Installation:

- create a venv with python 3.11.0 →  python -m venv venv
- activate venv: source venv/bin/activate or venv\Scripts\activate
- for mac / linux users: from the terminal →  make install
- for windows users: from the terminal →  pip install -r requirements.txt →  playwright install
- Reports and test artifacts will be generated in the end of the test inside pytest_reports folder (video, screenshots, trace file, reports)


---

# Running tests:
- for mac / linux: from the terminal →  make run-tests
- for windows: from the terminal →  python pytest_runner.py
- NOTE: the test runner is set to run "test_airbnb_flows.py" file with 3 workers and 3 browser for each test in headless mode

---

# Debugging /running tests from pycharm
1. navigate to:  Settings → Tools → python integrated tools
2. under Testing: make sure pytest is your default test runner
3. navigate to: Run → Edit configurations → Edit configuration templates
4. got to python tests → pytest (on the side bar)
5. under additional arguments add: --use-pycharm-debugger-args --ignore-https-errors
6. under environment variables: PYTHONUNBUFFERED=1
7. make sure your interpreter is set  to your project path
8. target: check script path
9. click ok and apply


---

# Available options for test configurations:


## Browser:


you can add multiple browser for your test run if needed

available browsers: chromium, webkit, firefox

Browser channel: works only with “chromium“

available browser channels: chrome, msedge

you may choose only one browser channel


## Tracing:

available options: 'on' / 'off' / 'retain-on-failure'

the trace file will capture all actions during the test including:
network traffic, requests and ui actions (also visually).

format: trace.zip

location: inside the test artifacts folder

how to use:

- open: Playwright Trace Viewer 

- drag the trace file and debug your test

- or open from the terminal → playwright show-trace [path to your trace.zip file]

## Video:

available options: 'on' / 'off' / 'retain-on-failure'

a video record of the test

format: video.webm

location: inside the test artifacts folder


## Screenshot:

available options: 'on' / 'off' / 'only-on-failure'

format: screenshot.png

location: inside the test artifacts folder

you can choose full page screenshot option inside the config file

## Timeouts:

playwright works with milliseconds time unit

example: 1000 (1 second), 12000(12 seconds), etc...

preferably, set time units above 9 seconds as follows: 10 * 1000

"default timeout" addresses a global timeout for all actions (locators, assertions, clicking etc...)

## Other

- workers: for running multiple tests in parallel 
- headed: run tests in headed / headless mode
- default timeouts: navigation / locators
- test runner: run test by name / mark / file


---

# Running tests from a test container with docker (for linux / mac users)
- make sure docker daemon is active (or just open docker desktop)
- from the terminal →  make base-image
- create a test container → make docker-new-container
- from the terminal →  make container-run-test
- NOTE: when running tests in a container make sure "headed" option in the configurations file is set to False

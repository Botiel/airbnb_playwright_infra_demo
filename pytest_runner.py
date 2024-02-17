from src.extended_pytest_playwright import PlaywrightPytestRunner
from pytest_configurations import configurations, tests


def main() -> None:
    runner = PlaywrightPytestRunner(configurations, tests)
    runner.run_tests()


if __name__ == '__main__':
    main()

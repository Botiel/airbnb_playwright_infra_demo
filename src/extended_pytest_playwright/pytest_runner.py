
from .configuration_objects import PytestConfigurationsBase, RunTestObject
from typing import Any, Optional
import subprocess


class RunnerBase:

    def __init__(self, config: Any, run_test_obj: Optional[RunTestObject] = None):
        super().__init__()
        self._run_test_obj = run_test_obj
        self._config = config

    @property
    def run_test_obj(self) -> RunTestObject:
        if self._run_test_obj:
            assert isinstance(self._run_test_obj, RunTestObject), 'self.run_test_obj is not of type RunTestObject'
            return self._run_test_obj

    @property
    def config(self) -> Any:
        if isinstance(self._config, PytestConfigurationsBase) or issubclass(self._config, PytestConfigurationsBase):
            return self._config
        raise ValueError('self.config is not class or sub-class of PytestConfigurationsBase')

    @staticmethod
    def print_pytest_cli_arguments(full_args: list[str]) -> None:

        border = '='
        top_border = f'\n{border * 60} [Pytest Cli Arguments] {border * 60}\n'
        bottom_border = f'\n{border * 144}\n'
        joined_text = ' '.join(full_args)
        line_length = 150

        print(top_border)

        while len(joined_text) > line_length:
            last_space_index = joined_text[:line_length].rfind(' ')
            if last_space_index == -1:
                last_space_index = line_length
            print(joined_text[:last_space_index])
            joined_text = joined_text[last_space_index + 1:]
        print(joined_text)

        print(bottom_border)

    def run_tests(self) -> None:
        raise NotImplementedError


class PlaywrightPytestRunner(RunnerBase):

    def __init__(self, config: Any, run_test_obj: RunTestObject):
        super().__init__(config, run_test_obj)

    def _pytest_task(self, test_name: str) -> None:
        extra_args = self.config.generate_cli_args_from_configurations(test_name=test_name)

        if self.run_test_obj.run_by == 'file':
            if not test_name.endswith('.py'):
                raise ValueError('test name should be a python file')
            args = ['pytest', test_name]
        else:
            args = ['pytest', self.run_test_obj.run_by, test_name]

        args.extend(extra_args)
        self.print_pytest_cli_arguments(args)
        subprocess.run(args=args)

    def run_tests(self) -> None:

        if not self.run_test_obj.tests:
            error = 'tests list can not be empty, check run_tests variable in pytest_run_configurations.py file'
            raise ValueError(error)

        for test in self.run_test_obj.tests:
            self._pytest_task(test_name=test)

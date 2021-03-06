import operator
import os
import unittest
import yaml
from copy import deepcopy
from pathlib import Path

from coala_quickstart.generation.SettingsClass import (
    collect_bear_settings,
    )
from coala_quickstart.green_mode.Setting import (
    find_max_min_of_setting,
    )
from coala_quickstart.green_mode.green_mode import (
    bear_test_fun,
    check_bear_results,
    generate_complete_filename_list,
    get_kwargs,
    get_setting_type,
    global_bear_test,
    initialize_project_data,
    local_bear_test,
    run_quickstartbear,
    )
from coala_quickstart.generation.Utilities import (
    append_to_contents,
    dump_yaml_to_file,
    get_yaml_contents,
    )
from coala_quickstart.green_mode.QuickstartBear import (
    QuickstartBear)
from coalib.results.Result import Result
from coalib.results.SourceRange import (
    SourcePosition,
    SourceRange,
    )
from tests.test_bears.AllKindsOfSettingsDependentBear import (
    AllKindsOfSettingsBaseBear,
    )
from tests.test_bears.TestGlobalBear import TestGlobalBear
from tests.test_bears.TestLocalBear import TestLocalBear

settings_key = 'green_mode_infinite_value_settings'


class Test_green_mode(unittest.TestCase):

    def test_get_yaml_contents(self):
        project_data = 'example_.project_data.yaml'
        full_path = str(Path(__file__).parent / project_data)
        yaml_contents = get_yaml_contents(full_path)
        test_yaml_contents = {
            'dir_structure': ['.coafile',
                              'example_file_1',
                              {'example_folder_1': ['example_file_2',
                                                    {'example_nested_folder_1':
                                                     ['example_file_3']},
                                                    {'example_nested_folder_2':
                                                     ['example_file_4']},
                                                    'example_file_5']},
                              'example_file_6']}
        self.assertEqual(yaml_contents, test_yaml_contents)

    def test_append_to_contents_1(self):
        ret_contents = append_to_contents({}, 'key', [1, 2], settings_key)
        self.assertEqual(ret_contents, {settings_key: [{'key': [1, 2]}]})

    def test_append_to_contents_2(self):
        ret_contents = append_to_contents({settings_key: []}, 'key', [1, 2],
                                          settings_key)
        self.assertEqual(ret_contents, {settings_key: [{'key': [1, 2]}]})

    def test_append_to_contents_3(self):
        ret_contents = append_to_contents({settings_key: [{'key': [3]}]},
                                          'key', [1, 2], settings_key)
        self.assertEqual(ret_contents, {settings_key: [{'key': [3, 1, 2]}]})

    def test_append_to_contents_4(self):
        ret_contents = append_to_contents({settings_key:
                                           [{'key': [3]},
                                            {'some_other_key': [True]},
                                            'some_other_entry_in_list']},
                                          'key', [1, 2], settings_key)
        self.assertEqual(ret_contents, {settings_key:
                                        [{'key': [3, 1, 2]},
                                         {'some_other_key': [True]},
                                         'some_other_entry_in_list']})

    def test_dump_yaml_to_file(self):
        file_path = str(Path(__file__).parent.parent.parent / 'output.yanl')
        dump_yaml_to_file(file_path, ['GSoC 2018'])
        file_path = Path(file_path)
        with file_path.open() as stream:
            test_contents = yaml.load(stream)
        self.assertEqual(test_contents, ['GSoC 2018'])
        os.remove(str(file_path))

    def test_initialize_project_data(self):
        dir_path = str(Path(__file__).parent) + os.sep
        contents = initialize_project_data(dir_path, [])
        pycache_index = -1
        for index, content in enumerate(contents):
            if isinstance(content, dict):
                if '__pycache__' in content.keys():
                    pycache_index = index
                    break
        if not pycache_index == -1:
            del contents[pycache_index]
        list_indices = []
        for index, content in enumerate(contents):
            if content[-4:] == 'orig':
                list_indices.append(index)
        for i in range(0, len(list_indices)):
            del contents[list_indices[i]]
            for j in range(i + 1, len(list_indices)):
                list_indices[j] = list_indices[j] - 1
        self.assertIn(
            ['QuickstartBearTest.py', 'example_.project_data.yaml',
             'green_modeTest.py', 'filename_operationsTest.py'],
            contents)

    def test_initialize_project_data(self):
        dir_path = str(Path(__file__).parent) + os.sep
        ignore_globs = ['*pycache*', '**.pyc', '**.orig']
        final_data = initialize_project_data(dir_path, ignore_globs)
        test_final_data = ['QuickstartBearTest.py',
                           'example_.project_data.yaml',
                           'green_modeTest.py',
                           'filename_operationsTest.py',
                           'bear_settings.yaml',
                           {'test_dir': ['test_file.py']}]
        self.assertCountEqual(final_data, test_final_data)

    def test_generate_complete_filename_list(self):
        dir_path = str(Path(__file__).parent) + os.sep
        ignore_globs = ['*pycache*', '**.pyc', '**.orig']
        data = initialize_project_data(dir_path, ignore_globs)
        final_data = generate_complete_filename_list(data, dir_path[:-1])
        prefix = dir_path
        test_final_data = ['QuickstartBearTest.py',
                           'example_.project_data.yaml',
                           'bear_settings.yaml',
                           'green_modeTest.py',
                           'filename_operationsTest.py',
                           'test_dir' + os.sep + 'test_file.py']
        test_final_data = [prefix + x for x in test_final_data]
        self.assertCountEqual(final_data, test_final_data)

    def test_find_max_min_of_setting_1(self):
        final_contents = find_max_min_of_setting('key', 1, {settings_key: []},
                                                 operator.gt)
        test_contents = {settings_key: [{'key': 1}]}
        self.assertEqual(final_contents, test_contents)

    def test_find_max_min_of_setting_2(self):
        final_contents = find_max_min_of_setting(
            'key', 1, {settings_key: [{'key': 0}]}, operator.gt)
        test_contents = {settings_key: [{'key': 1}]}
        self.assertEqual(final_contents, test_contents)

    def test_find_max_min_of_setting_3(self):
        final_contents = find_max_min_of_setting(
            'key', 1, {settings_key: [{'key': 2}]}, operator.gt)
        test_contents = {settings_key: [{'key': 2}]}
        self.assertEqual(final_contents, test_contents)

    def test_find_max_min_of_setting_4(self):
        final_contents = find_max_min_of_setting('key', 1, {settings_key: []},
                                                 operator.lt)
        test_contents = {settings_key: [{'key': 1}]}
        self.assertEqual(final_contents, test_contents)

    def test_find_max_min_of_setting_5(self):
        final_contents = find_max_min_of_setting(
            'key', 1, {settings_key: [{'key': 0}]}, operator.lt)
        test_contents = {settings_key: [{'key': 0}]}
        self.assertEqual(final_contents, test_contents)

    def test_find_max_min_of_setting_6(self):
        final_contents = find_max_min_of_setting(
            'key', 1, {settings_key: [{'key': 2}]}, operator.lt)
        test_contents = {settings_key: [{'key': 1}]}
        self.assertEqual(final_contents, test_contents)

    def test_run_quickstartbear(self):
        dir_path = str(Path(__file__).parent) + os.sep
        ignore_globs = ['*pycache*', '**.pyc', '**.orig']
        contents = initialize_project_data(dir_path, ignore_globs)
        contents = {'dir_structure': contents, settings_key: []}
        settings_key_values = [{'max_lines_per_file': 1000},  # default value
                               {'max_line_length': 80},
                               {'min_lines_per_file': 5}]
        test_contents = deepcopy(contents)
        test_contents[settings_key] = settings_key_values
        (final_contents, ignore_ranges, complete_file_dict,
         complete_filename_list) = run_quickstartbear(contents, dir_path)
        ignore_file_name = dir_path + 'test_dir' + os.sep + 'test_file.py'
        start = SourcePosition(ignore_file_name, line=3, column=1)
        stop = SourcePosition(ignore_file_name, line=4, column=20)
        test_ignore_ranges = SourceRange(start, stop)
        self.assertEqual(test_contents, final_contents)
        self.assertEqual(ignore_ranges, [([], test_ignore_ranges)])

    def test_run_quickstartbear_with_file_None(self):
        # Mocking the method
        QuickstartBear.execute = lambda *args, **kwargs: [None]
        dir_path = str(Path(__file__).parent) + os.sep
        contents = initialize_project_data(dir_path, [])
        contents = {'dir_structure': contents, settings_key: []}
        test_contents = deepcopy(contents)
        (final_contents, ignore_ranges, complete_file_dict,
         complete_filename_list) = run_quickstartbear(contents, dir_path)
        self.assertEqual(test_contents, final_contents)

    def test_get_setting_type(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        type_setting, val = get_setting_type(
            'key', 'GummyBear', __location__)
        self.assertEqual(type_setting, 'typeX')
        self.assertEqual(val, '')

    def test_get_kwargs_1(self):
        relevant_bears = {'test':
                          {AllKindsOfSettingsBaseBear, }}
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        dir_path = str(Path(__file__).parent) + os.sep
        ignore_globs = ['*pycache*', '**.pyc', '**.orig']
        bear_settings_obj = collect_bear_settings(relevant_bears)
        non_optional_settings = bear_settings_obj[0].non_optional_settings
        bear_settings_obj[0].optional_settings
        contents = initialize_project_data(dir_path, ignore_globs)
        contents = {'dir_structure': contents,
                    settings_key: [{'some_rubbish_setting': 'some_rubbish',
                                    'max_line_lengths': 60}]}
        kwargs = get_kwargs(non_optional_settings,
                            [AllKindsOfSettingsBaseBear],
                            contents, __location__)
        test_kwargs = {'use_bear': [True, False],
                       'max_line_lengths': [60],
                       'no_line': [1, 2]}
        self.assertEqual(kwargs, test_kwargs)

    def test_get_kwargs_2(self):
        relevant_bears = {'test':
                          {AllKindsOfSettingsBaseBear, }}
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        dir_path = str(Path(__file__).parent) + os.sep
        ignore_globs = ['*pycache*', '**.pyc', '**.orig']
        bear_settings_obj = collect_bear_settings(relevant_bears)
        bear_settings_obj[0].non_optional_settings
        optional_settings = bear_settings_obj[0].optional_settings
        contents = initialize_project_data(dir_path, ignore_globs)
        contents = {'dir_structure': contents,
                    settings_key: [{'some_rubbish_setting': 'some_rubbish',
                                    'max_line_lengths': 60}]}
        kwargs = get_kwargs(optional_settings,
                            [AllKindsOfSettingsBaseBear],
                            contents, __location__)
        test_kwargs = {'use_space': [True, False],
                       'use_tab': [True, False]}
        self.assertEqual(kwargs, test_kwargs)

    def test_check_bear_results_1(self):
        self.assertEqual(True, check_bear_results([], []))
        self.assertEqual(False, check_bear_results(['a'], []))

    def test_check_bear_results_2(self):
        start = SourcePosition('a.py', line=368, column=4)
        end = SourcePosition('a.py', line=442, column=2)
        range_object = SourceRange(start, end)
        results = [Result(affected_code=[range_object],
                          message='green_mode', origin=QuickstartBear)]

        start = SourcePosition('a.py', line=268, column=4)
        end = SourcePosition('a.py', line=542, column=2)
        ignore_object = SourceRange(start, end)
        ignore_ranges = [('+', ignore_object)]
        self.assertTrue(check_bear_results(results, ignore_ranges))

    def test_check_bear_results_3(self):
        start = SourcePosition('a.py', line=368, column=4)
        end = SourcePosition('a.py', line=442, column=2)
        range_object = SourceRange(start, end)
        results = [Result(affected_code=[range_object],
                          message='green_mode', origin=QuickstartBear)]

        start = SourcePosition('a.py', line=468, column=4)
        end = SourcePosition('a.py', line=478, column=2)
        ignore_object = SourceRange(start, end)
        ignore_ranges = [('+=', ignore_object)]
        self.assertFalse(check_bear_results(results, ignore_ranges))

    def test_bear_test_fun_1(self):
        from pyprint.ConsolePrinter import ConsolePrinter
        printer = ConsolePrinter()
        bears = {'Python': [TestLocalBear, TestGlobalBear]}
        relevant_bears = {'test':
                          {TestLocalBear, TestGlobalBear, }}
        bear_settings_obj = collect_bear_settings(relevant_bears)
        file_dict = {'A.py': {'a\n', 'b\n'}, 'C.py': {'c\n', 'd\n'}}
        dir_path = str(Path(__file__).parent) + os.sep
        contents = initialize_project_data(dir_path, [])
        file_names = ['A.py', 'C.py']
        non_op_results, unified_results = bear_test_fun(
            bears, bear_settings_obj, file_dict, [], contents,
            file_names, 5, 5, printer)
        test_non_op_results = [{TestLocalBear:
                                [{'filename': 'A.py'},
                                 {'filename': 'C.py'}]},
                               {TestGlobalBear: [{}]}]
        test_unified_results = [{TestLocalBear:
                                 [{'filename': 'A.py',
                                   'yield_results': False},
                                  {'filename': 'C.py',
                                   'yield_results': False}]},
                                {TestGlobalBear: [{'yield_results': False}]}]
        self.assertCountEqual(non_op_results[1][TestGlobalBear],
                              test_non_op_results[1][TestGlobalBear])
        self.assertCountEqual(unified_results[1][TestGlobalBear],
                              test_unified_results[1][TestGlobalBear])
        self.assertCountEqual(non_op_results[0][TestLocalBear],
                              test_non_op_results[0][TestLocalBear])
        self.assertCountEqual(unified_results[0][TestLocalBear],
                              test_unified_results[0][TestLocalBear])

    def test_bear_test_fun_2(self):
        from pyprint.ConsolePrinter import ConsolePrinter
        printer = ConsolePrinter()
        bears = {'Python': [TestLocalBear, TestGlobalBear]}
        relevant_bears = {'test':
                          {TestLocalBear, TestGlobalBear, }}
        bear_settings_obj = collect_bear_settings(relevant_bears)
        file_dict = {'A.py': {'a\n', 'b\n'}, 'C.py': {'c\n', 'd\n'}}
        dir_path = str(Path(__file__).parent) + os.sep
        contents = initialize_project_data(dir_path, [])
        file_names = ['A.py', 'C.py']
        non_op_results, unified_results = bear_test_fun(
            bears, bear_settings_obj, file_dict, [], contents,
            file_names, 1, 1, printer)
        test_non_op_results = [{TestLocalBear:
                                [{'filename': 'A.py'},
                                 {'filename': 'C.py'}]},
                               {TestGlobalBear: [{}]}]
        test_unified_results = [{TestLocalBear:
                                 [{'filename': 'A.py',
                                   'yield_results': False},
                                  {'filename': 'C.py',
                                   'yield_results': False}]},
                                {TestGlobalBear: [{'yield_results': False}]}]
        self.assertCountEqual(non_op_results[1][TestGlobalBear],
                              test_non_op_results[1][TestGlobalBear])
        self.assertCountEqual(non_op_results[0][TestLocalBear],
                              test_non_op_results[0][TestLocalBear])
        self.assertCountEqual(unified_results, [None, None])

    def test_green_mode(self):
        pass

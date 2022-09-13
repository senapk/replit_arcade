#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# exec pip install termcolor in your system to enable colors

from __future__ import annotations

import sys
try:
    from termcolor import colored
    color_enabled = True
except ModuleNotFoundError:
    color_enabled = False
from enum import Enum
from typing import List, Tuple, Any, Optional
import os
import re
import shutil
import argparse
import subprocess
import tempfile
import io
import urllib.request
import urllib.error
import json
from subprocess import PIPE
import configparser

asc2only: bool = False


class Unit:
    def __init__(self, case: str = "", inp: str = "", outp: str = "", grade: Optional[int] = None, source: str = ""):
        self.source = source  # stores the source file of the unit
        self.case = case  # name
        self.input = inp  # input
        self.output = outp  # expected output
        self.grade = grade  # None represents proportional gr, 100 represents all
        self.index = 0
        self.duplicated: Optional[int] = None


class Symbol:
    opening = "=>"
    neutral = ""
    mark_size = len(neutral)
    success = ""
    failure = ""
    wrong = ""
    compilation = ""
    execution = ""
    hbar = "─"
    vbar = "│"
    whitespace = "\u2E31"  # interpunct
    newline = "\u21B5"  # carriage return
    cfill = "_"

    def __init__(self):
        pass

    @staticmethod
    def set_asc_only(only: bool):
        Symbol.neutral = "(.)" if only else "(»)"  # u"\u2610"  # ☐
        Symbol.mark_size = len(Symbol.neutral)
        Symbol.success = "(S)" if only else "(✓)"
        Symbol.failure = "(X)" if only else "(✗)"
        Symbol.wrong = "(W)" if only else "(ω)"
        Symbol.compilation = "(C)" if only else "(ϲ)"
        Symbol.execution = "(E)" if only else "(ϵ)"

    @staticmethod
    def get_core_symbol(symbol):
        return symbol[1]


Symbol.set_asc_only(asc2only)  # inicalizacao estatica


class Solver:
    def __init__(self, path):
        self.path: str = Solver.__add_dot_bar(path)
        self.filename: str = path.split(os.sep)[-1]
        self.user: List[Optional[str]] = []
        self.result: ExecutionResult = ExecutionResult.UNTESTED
        self.error_msg: str = ""
        self.executable: str = ""
        self.rm_executable: bool = False
        self.prepare_exec()


    def prepare_exec(self) -> None:
        path = self.path
        if " " in path:  # more than one parameter
            self.executable = path
        elif path.endswith(".py"):
            self.executable = "python " + path
        elif path.endswith(".js"):
            self.executable = "node " + path
        elif path.endswith(".ts"):
            self.executable = "ts-node " + path
        elif path.endswith(".java"):
            self.executable = Solver.__prepare_java(path)
            self.rm_executable = True
        elif path.endswith(".c"):
            self.executable = Solver.__prepare_c(path)
            self.rm_executable = True
        elif path.endswith(".hs"):
            solver_cmd = Solver.__prepare_hs(path)
            self.rm_executable = True
        elif path.endswith(".cpp"):
            self.executable = Solver.__prepare_cpp(path)
            self.rm_executable = True
        else:
            self.executable = path

    def get_mark(self):
        return self._get_mark()

    def _get_mark(self):
        if self.result == ExecutionResult.UNTESTED:
            return Symbol.neutral
        elif self.result == ExecutionResult.SUCCESS:
            return Symbol.success
        elif self.result == ExecutionResult.WRONG_OUTPUT:
            return Symbol.wrong
        elif self.result == ExecutionResult.COMPILATION_ERROR:
            return Symbol.compilation
        elif self.result == ExecutionResult.EXECUTION_ERROR:
            return Symbol.execution
        return Symbol.failure

    @staticmethod
    def __prepare_java(solver: str) -> str:
        cmd = ["javac", solver, '-d', '.']
        return_code, stdout, stderr = Runner.subprocess_run(cmd)
        print(stdout)
        print(stderr)
        if return_code != 0:
            raise Runner.CompileError(stdout + stderr)
        solver = solver.split(os.sep)[-1]  # getting only the filename
        return "java " + solver[:-5]  # removing the .java

    @staticmethod
    def __prepare_multiple_files(solver: str) -> List[str]:
        return list(map(Solver.__add_dot_bar, solver.split(Identifier.multi_file_separator)))

    @staticmethod
    def __prepare_hs(solver: str) -> str:
        solver_files = Solver.__prepare_multiple_files(solver)
        source_path = os.sep.join(solver_files[0].split(os.sep)[:-1] + [".a.hs"])
        exec_path = os.sep.join(solver_files[0].split(os.sep)[:-1] + [".a.out"])
        with open(source_path, "w") as f:
            for solver in solver_files:
                f.write(open(solver).read() + "\n")

        cmd = ["ghc", "--make", source_path, "-o", exec_path]
        return_code, stdout, stderr = Runner.subprocess_run(cmd)
        print(stdout)
        print(stderr)
        if return_code != 0:
            raise Runner.CompileError(stdout + stderr)
        return exec_path

    @staticmethod
    def __prepare_c_cpp(solver: str, pre_args: List[str], pos_args: list[str]) -> str:
        solver_files = Solver.__prepare_multiple_files(solver)
        exec_path = os.sep.join(solver_files[0].split(os.sep)[:-1] + [".a.out"])
        cmd = pre_args + solver_files + ["-o", exec_path] + pos_args
        return_code, stdout, stderr = Runner.subprocess_run(cmd)
        print(stdout)
        print(stderr)
        if return_code != 0:
            raise Runner.CompileError(stdout + stderr)
        return exec_path

    @staticmethod
    def __prepare_c(solver: str) -> str:
        # pre = ["gcc", "-Wall", "-fsanitize=address", "-Wuninitialized", "-Wparentheses", "-Wreturn-type", "-fno-diagnostics-color"] 
        pre = ["gcc", "-Wall"]
        pos = ["-lm", "-lutil"]
        return Solver.__prepare_c_cpp(solver, pre, pos)

    @staticmethod
    def __prepare_cpp(solver: str) -> str:
        # pre = ["g++", "-std=c++20", "-Wall", "-g", "-fsanitize=address", "-fsanitize=undefined", "-D_GLIBCXX_DEBUG"] # muito lento no replit
        pre = ["g++", "-std=c++20", "-Wall", "-Wextra"]
        pos = []
        print("debug1")
        return Solver.__prepare_c_cpp(solver, pre, pos)

    @staticmethod
    def __add_dot_bar(solver: str) -> str:
        if os.sep not in solver and os.path.isfile("." + os.sep + solver):
            solver = "." + os.sep + solver
        return solver



class IOBuffer:
    tab = " " * 4

    def __init__(self):
        self.buffer = io.StringIO()

    def write(self, data: str, level: int = 0) -> str:
        shift = level * IOBuffer.tab
        _data = shift + ('\n' + shift).join(data.split('\n'))
        if data.endswith('\n') and len(shift) > 0:
            _data = _data[:-len(shift)]
        self.buffer.write(_data)
        return _data

    def getvalue(self) -> str:
        return self.buffer.getvalue()


class Logger:
    _buffer = IOBuffer()
    _level = 0
    _print_enabled = True

    _store_buffer = IOBuffer()
    _store = False

    def __init__(self):
        pass

    @staticmethod
    def store():
        Logger._store = True
        Logger._store_buffer = IOBuffer()

    @staticmethod
    def recover():
        Logger._store = False
        return Logger._store_buffer.getvalue()

    @staticmethod
    def print_enable():
        Logger._print_enabled = True

    @staticmethod
    def print_disable():
        Logger._print_enabled = False

    @staticmethod
    def inc_level():
        Logger._level += 1

    @staticmethod
    def dec_level():
        if Logger._level > 0:
            Logger._level -= 1

    @staticmethod
    def _colorize(data: str):
        return data.replace(Symbol.failure, colored(Symbol.failure, 'red')).\
                    replace(Symbol.opening, colored(Symbol.opening, 'blue')). \
                    replace(Symbol.success, colored(Symbol.success, 'green')). \
                    replace(Symbol.wrong, colored(Symbol.wrong, 'yellow')). \
                    replace(Symbol.execution, colored(Symbol.execution, 'yellow')). \
                    replace(Symbol.compilation, colored(Symbol.compilation, 'yellow')). \
                    replace(Symbol.neutral, colored(Symbol.neutral, 'blue'))

    @staticmethod
    def write(data: str, level: Optional[int] = None, relative: Optional[int] = None):
        if level:
            Logger._level += level
        if relative:
            Logger._level += relative
        if Logger._store:
            data_formatted = Logger._store_buffer.write(data, Logger._level)
        else:
            data_formatted = Logger._buffer.write(data, Logger._level)
        if Logger._print_enabled and not Logger._store:
            if color_enabled:
                data_output = Logger._colorize(data_formatted)
            else:
                data_output = data_formatted
            print(data_output, end='', flush=True)
        if relative:
            Logger._level -= relative

    @staticmethod
    def clear():
        Logger._buffer = IOBuffer()

    @staticmethod
    def getvalue():
        return Logger._buffer.getvalue()


class VplParser:
    @staticmethod
    def finish(text):
        return text if text.endswith("\n") else text + "\n"

    @staticmethod
    def unwrap(text):
        while text.endswith("\n"):
            text = text[:-1]
        if text.startswith("\"") and text.endswith("\""):
            text = text[1:-1]
        return VplParser.finish(text)

    @staticmethod
    class CaseData:
        def __init__(self, case="", inp="", outp="", grade: Optional[int] = None):
            self.case: str = case
            self.input: str = VplParser.finish(inp)
            self.output: str = VplParser.unwrap(VplParser.finish(outp))
            self.grade: Optional[int] = grade

        def __str__(self):
            return "case=" + self.case + '\n' \
                   + "input=" + self.input \
                   + "output=" + self.output \
                   + "gr=" + str(self.grade)

    regex_vpl_basic = r"case= *([ \S]*) *\n *input *=(.*?)^ *output *=(.*)"
    regex_vpl_extended = r"case= *([ \S]*) *\n *input *=(.*?)^ *output *=(.*?)^ *grade *reduction *= *(\S*)% *\n?"

    @staticmethod
    def filter_quotes(x):
        return x[1:-2] if x.startswith('"') else x

    @staticmethod
    def split_cases(text: str) -> List[str]:
        regex = r"^ *[Cc]ase *="
        subst = "case="
        text = re.sub(regex, subst, text, 0, re.MULTILINE | re.DOTALL)
        return ["case=" + t for t in text.split("case=")][1:]

    @staticmethod
    def extract_extended(text) -> Optional[CaseData]:
        f = re.match(VplParser.regex_vpl_extended, text, re.MULTILINE | re.DOTALL)
        if f is None:
            return None
        try:
            gr = int(f.group(4))
        except ValueError:
            gr = None
        return VplParser.CaseData(f.group(1), f.group(2), f.group(3), gr)

    @staticmethod
    def extract_basic(text) -> Optional[CaseData]:
        m = re.match(VplParser.regex_vpl_basic, text, re.MULTILINE | re.DOTALL)
        if m is None:
            return None
        return VplParser.CaseData(m.group(1), m.group(2), m.group(3), None)

    @staticmethod
    def parse_vpl(content: str) -> List[CaseData]:
        text_cases = VplParser.split_cases(content)
        seq: List[VplParser.CaseData] = []

        for text in text_cases:
            case = VplParser.extract_extended(text)
            if case is not None:
                seq.append(case)
                continue
            case = VplParser.extract_basic(text)
            if case is not None:
                seq.append(case)
                continue
            print("invalid case: " + text)
            exit(1)
        return seq

    @staticmethod
    def to_vpl(unit: CaseData):
        text = "case=" + unit.case + "\n"
        text += "input=" + unit.input
        text += "output=\"" + unit.output + "\"\n"
        if unit.grade is not None:
            text += "grade reduction=" + str(unit.grade) + "%\n"
        return text


class Loader:
    regex_tio = r"^ *>>>>>>>> *(.*?)\n(.*?)^ *======== *\n(.*?)^ *<<<<<<<< *\n?"

    def __init__(self):
        pass

    @staticmethod
    def parse_cio(text, source, crude_mode=False):
        unit_list = []
        text = "\n" + text

        for test_case in text.split("\n#__case")[1:]:
            unit = Unit()
            unit.source = source
            unit.output = test_case
            unit_list.append(unit)

        for unit in unit_list:
            test = unit.output
            if "\n$end" in test:
                test = test.split("\n$end")[0] + "\n$end"

            lines = test.split("\n")
            tags = lines[0].strip().split(" ")
            if tags[-1].endswith("%"):
                unit.grade = int(tags[-1][0:-1])
                del tags[-1]
            else:
                unit.grade = None
            unit.case = " ".join(tags)
            unit.output = "\n".join(lines[1:])

        # concatenando testes contínuos
        for i in range(len(unit_list)):
            unit = unit_list[i]
            if "\n$end" not in unit.output and (i < len(unit_list) - 1):
                unit_list[i + 1].output = unit.output + '\n' + unit_list[i + 1].output
                unit.output = unit.output + "\n$end\n"

        for unit in unit_list:
            lines = unit.output.split('\n')
            unit.output = ""
            unit.input = ""
            # filtrando linhas vazias e comentarios
            for line in lines:
                if crude_mode:  #
                    unit.output += line + '\n'
                    if line == "" or line.startswith("$") or line.startswith("#"):
                        unit.input += line + '\n'
                else:
                    if line != "" and not line.startswith("#"):
                        unit.output += line + '\n'
                        if line.startswith("$"):
                            unit.input += line[1:] + '\n'
        for unit in unit_list:
            unit.fromCio = True

        return unit_list

    @staticmethod
    def parse_tio(text: str, source: str = "") -> List[Unit]:
        def parse_case_grade(value: str) -> Tuple[str, Optional[int]]:
            _grade: Optional[int] = None
            if value.endswith("%"):
                value = " ".join(value.split(" ")[:-1])  # todas as palavras menos a ultima
                gr = value.split(" ")[-1][:-1]           # ultima palavra sem %
                try:
                    _grade = int(gr)
                except ValueError:
                    pass
            return value, _grade

        matches = re.findall(Loader.regex_tio, text, re.MULTILINE | re.DOTALL)
        unit_list = []
        for m in matches:
            case, grade = parse_case_grade(m[0])
            unit_list.append(Unit(case, m[1], m[2], grade, source))
        return unit_list

    @staticmethod
    def parse_vpl(text: str, source: str = "") -> List[Unit]:
        data_list = VplParser.parse_vpl(text)
        output: List[Unit] = []
        for m in data_list:
            output.append(Unit(m.case, m.input, m.output, m.grade, source))
        return output

    @staticmethod
    def parse_dir(folder) -> List[Unit]:
        pattern_loader = PatternLoader()
        files = sorted(os.listdir(folder))
        matches = pattern_loader.get_file_sources(files)

        unit_list: List[Unit] = []
        try:
            for m in matches:
                unit = Unit()
                unit.source = os.path.join(folder, m.label)
                unit.grade = 100
                with open(os.path.join(folder, m.input_file)) as f:
                    value = f.read()
                    unit.input = value + ("" if value.endswith("\n") else "\n")
                with open(os.path.join(folder, m.output_file)) as f:
                    value = f.read()
                    unit.output = value + ("" if value.endswith("\n") else "\n")
                unit_list.append(unit)
        except FileNotFoundError as e:
            Logger.write(str(e))
        return unit_list

    @staticmethod
    def parse_source(source: str) -> List[Unit]:
        if os.path.isdir(source):
            return Loader.parse_dir(source)
        if os.path.isfile(source):
            #  if PreScript.exists():
            #      source = PreScript.process_source(source)
            with open(source) as f:
                content = f.read()
            if source.endswith(".vpl"):
                return Loader.parse_vpl(content, source)
            elif source.endswith(".tio"):
                return Loader.parse_tio(content, source)
            elif source.endswith(".md"):
                tests = Loader.parse_tio(content, source)
                tests += Loader.parse_cio(content, source)
                return tests
            else:
                Logger.write("warning: target format do not supported: " + source + '\n')  # make this a raise
        else:
            raise FileNotFoundError('warning: unable to find: ' + source)
        return []


class DiffMode(Enum):
    FIRST = "MODE: SHOW FIRST FAILURE ONLY"
    NONE = "MODE: SHOW NONE FAILURES"
    ALL = "MODE: SHOW ALL FAILURES"


class Param:

    def __init__(self):
        pass

    class Basic:
        def __init__(self):
            self.index: Optional[int] = None
            self.label_pattern: Optional[str] = None
            self.is_raw: bool = False
            self.keep = False
            self.display = False
            self.is_up_down = False
            self.diff_mode = DiffMode.FIRST

        def set_index(self, value: Optional[int]):
            self.index = value
            return self

        def set_label_pattern(self, label_pattern: Optional[str]):
            self.label_pattern = label_pattern
            return self

        def set_raw(self, value: bool):
            self.is_raw = value
            return self

        def set_up_down(self, value: bool):
            self.is_up_down = value
            return self

        def set_keep(self, value: bool):
            self.keep = value
            return self

        def set_display(self, value: bool):
            self.display = value
            return self

        def set_diff_mode(self, value: DiffMode):
            self.diff_mode = value
            return self

    class Manip:
        def __init__(self, unlabel: bool = False, to_sort: bool = False, to_number: bool = False):
            self.unlabel = unlabel
            self.to_sort = to_sort
            self.to_number = to_number


class Wdir:
    def __init__(self, folder: str):
        self.folder = folder
        self.solver: Optional[Solver] = None
        self.source_list: List[str] = []
        self.pack_list: List[List[Unit]] = []
        self.unit_list: List[Unit] = []

    def set_sources(self, sources: List[str]):
        self.source_list = sources
        return self

    def set_solver(self, solver: str):
        self.solver = Solver(solver)
        return self

    def load_sources(self):
        file_list: List[str] = os.listdir(self.folder)
        s_list = []
        for file in file_list:
            if file.startswith("."):
                continue
            # elif file == "Readme.md":
            #     s_list.append(file)
            elif file.endswith(".tio"):
                s_list.append(file)
            elif file.endswith(".vpl"):
                s_list.append(file)
        self.source_list = [os.path.join(self.folder, file) for file in s_list]
        return self

    def load_solvers(self):
        file_list: List[str] = os.listdir(self.folder)
        s_list = []
        for file in file_list:
            if file.lower().startswith("solver"):
                s_list.append(file)
        s_list = sorted(s_list)
        if len(s_list) == 0:
            self.solver = None
        else:
            self.solver = Solver(os.path.join(self.folder, s_list[0]))
        return self

    def parse_sources(self):
        loading_failures = 0
        for source in self.source_list:
            try:
                self.pack_list.append(Loader.parse_source(source))
            except FileNotFoundError as e:
                Logger.write(str(e) + "\n")
                loading_failures += 1
                pass
        if loading_failures > 0 and loading_failures == len(self.source_list):
            raise FileNotFoundError("failure: none source found")
        self.unit_list = sum(self.pack_list, [])
        self.__number_and_mark()
        return self

    def filter(self, index: Optional[int]):
        if index is not None:
            if 0 <= index < len(self.unit_list):
                self.unit_list = [self.unit_list[index]]
            else:
                raise ValueError("Index Number out of bounds: " + str(index))
        return self

    def __number_and_mark(self):
        new_list = []
        index = 0
        for unit in self.unit_list:
            unit.index = index
            index += 1
            search = [x for x in new_list if x.input == unit.input]
            if len(search) > 0:
                unit.duplicated = search[0].index
            new_list.append(unit)
        self.unit_list = new_list

    def manipulate(self, param):
        # filtering marked duplicated
        self.unit_list = [unit for unit in self.unit_list if unit.duplicated is None]
        if param.to_sort:
            self.unit_list.sort(key=lambda v: len(v.input))
        if param.unlabel:
            for unit in self.unit_list:
                unit.case = ""
        if param.to_number:
            number = 00
            for unit in self.unit_list:
                unit.case = LabelFactory().label(unit.case).index(number).generate()
                number += 1

    def replace_input(self, solver: Solver):
        Execution.execute_solver(solver, self.unit_list)
        if solver.result == ExecutionResult.COMPILATION_ERROR or solver.result == ExecutionResult.EXECUTION_ERROR:
            msg = "  " + solver.get_mark() + " " + solver.path + " " + solver.filename + "\n" + solver.error_msg
            raise RuntimeError(msg)
        else:
            for unit, output in zip(self.unit_list, solver.user):
                unit.output = output

    def resume(self) -> List[str]:
        def resume_count() -> str:
            return str(len([x for x in self.unit_list if x.duplicated is None])).zfill(2)

        def resume_sources() -> str:
            out = []
            if len(self.pack_list) == 0:
                out.append(Symbol.failure)
            for i in range(len(self.pack_list)):
                nome: str = self.source_list[i].split(os.sep)[-1]
                out.append(nome + "(" + str(len(self.pack_list[i])).zfill(2) + ")")
            return ", ".join(out)

        def resume_solvers() -> str:
            if self.solver is None:
                return ""
            return self.solver.get_mark() + self.solver.filename
        return [self.folder, resume_count(), resume_sources(), resume_solvers()]


class LabelFactory:
    def __init__(self):
        self._label = ""
        self._index = -1

    def index(self, value: int):
        try:
            self._index = int(value)
        except ValueError:
            raise ValueError("Index on label must be a integer")
        return self

    def label(self, value: str):
        self._label = value
        return self

    def generate(self):
        label = LabelFactory.trim_spaces(self._label)
        label = LabelFactory.remove_old_index(label)
        if self._index != -1:
            index = str(self._index).zfill(2)
            if label != "":
                return index + " " + label
            else:
                return index
        return label

    @staticmethod
    def trim_spaces(text):
        parts = text.split(" ")
        parts = [word for word in parts if word != '']
        return " ".join(parts)

    @staticmethod
    def remove_old_index(label):
        split_label = label.split(" ")
        if len(split_label) > 0:
            try:
                int(split_label[0])
                return " ".join(split_label[1:])
            except ValueError:
                return label


class Runner:

    def __init__(self):
        pass

    class CompileError(Exception):
        pass

    class ExecutionError(Exception):
        pass

    @staticmethod
    def subprocess_run(cmd_list: List[str], input_data: str = "") -> Tuple[int, Any, Any]:
        p = subprocess.Popen(cmd_list, stdout=PIPE, stdin=PIPE, stderr=PIPE, universal_newlines=True)
        stdout, stderr = p.communicate(input=input_data)
        return p.returncode, stdout, stderr

class IdentifierType(Enum):
    WDIR = "WORKING DIR"
    OBI = "OBI"
    MD = "MD"
    TIO = "TIO"
    VPL = "VPL"
    SOLVER = "SOLVER"


class Identifier:
    multi_file_separator = ","

    def __init__(self):
        pass

    @staticmethod
    def get_type(target: str) -> IdentifierType:
        if os.path.isdir(target):
            return IdentifierType.OBI
        elif target.endswith(".md"):
            return IdentifierType.MD
        elif target.endswith(".tio"):
            return IdentifierType.TIO
        elif target.endswith(".vpl"):
            return IdentifierType.VPL
        else:
            return IdentifierType.SOLVER

    # group targets with colon between then
    # ['lib.cpp,', 'main.cpp', 'teste.tio']
    # ['lib.cpp,main.cpp', 'teste.tio']
    @staticmethod
    def join_multi_file_solvers(input_list: List[str]) -> List[str]:
        out = []
        separator = Identifier.multi_file_separator
        for entry in input_list:
            if entry == separator:
                out[-1] += separator
            elif len(out) != 0 and out[-1].endswith(separator):
                out[-1] += entry
            else:
                out.append(entry)
        return out

    @staticmethod
    def split_input_list(input_list: List[str]) -> Tuple[str, List[str]]:
        input_list = Identifier.join_multi_file_solvers(input_list)

        solvers = [target for target in input_list if Identifier.get_type(target) == IdentifierType.SOLVER]
        sources = [target for target in input_list if target not in solvers]

        solver = None if len(solvers) == 0 else solvers[0]
        return solver, sources

    @staticmethod
    def mount_wdir_list(target_list: List[str], folders: List[str], param: Param.Basic) -> List[Wdir]:

        wdir_list: List[Wdir] = []
        solvers, sources = Identifier.split_input_list(target_list)
        if len(target_list) == 0 and folders is None:
            folders = ["."]
        if sources or solvers:
            wdir_list.append(Wdir(".").set_sources(sources).set_solver(solvers).parse_sources().filter(param.index))
        if folders is not None:
            wdir_list += [Wdir(f).load_solvers().load_sources().parse_sources().filter(param.index) for f in folders]
        return wdir_list


class ExecutionResult(Enum):
    UNTESTED = "UNTESTED"
    SUCCESS = "SUCCESS"
    WRONG_OUTPUT = "WRONG OUTPUT"
    COMPILATION_ERROR = "COMPILATION ERROR"
    EXECUTION_ERROR = "EXECUTION ERROR"


class Execution:

    def __init__(self):
        pass

    @staticmethod
    def __execute_single_case(exec_cmd: str, input_data: str) -> str:
        cmd = exec_cmd.split(" ")
        return_code, stdout, stderr = Runner.subprocess_run(cmd, input_data)
        if return_code != 0:
            raise Runner.ExecutionError(stdout + stderr)
        return stdout

    @staticmethod
    def __exec_and_check(solver: Solver, unit_list: List[Unit], keep: bool = False) -> None:
        for _i in range(len(unit_list)):
            solver.user.append(None)
        for i in range(len(unit_list)):
            solver.user[i] = Execution.__execute_single_case(solver.executable, unit_list[i].input)
            if solver.user[i] == unit_list[i].output:
                Logger.write(Symbol.get_core_symbol(Symbol.success))
            else:
                Logger.write(Symbol.get_core_symbol(Symbol.failure))
        if solver.rm_executable and not keep:
            if solver.executable.startswith("java "):
                for x in [item for item in os.listdir(".") if item.endswith(".class")]:
                    os.remove(x)
            else:
                os.remove(solver.executable)

    @staticmethod
    def __check_all_answers_right(solver: Solver, unit_list: List[Unit]) -> bool:
        return len([unit for unit, output in zip(unit_list, solver.user) if unit.output == output]) == len(unit_list)

    @staticmethod
    def execute_solver(solver: Solver, unit_list: List[Unit], keep: bool = False) -> None:
        try:
            Execution.__exec_and_check(solver, unit_list, keep)
            if Execution.__check_all_answers_right(solver, unit_list):
                solver.result = ExecutionResult.SUCCESS
            else:
                solver.result = ExecutionResult.WRONG_OUTPUT
        except Runner.CompileError as e:
            solver.result = ExecutionResult.COMPILATION_ERROR
            solver.error_msg = str(e)
        except (Runner.ExecutionError, FileNotFoundError, PermissionError) as e:
            solver.result = ExecutionResult.EXECUTION_ERROR
            solver.error_msg = str(e)


class Report:
    __term_width: Optional[int] = None

    def __init__(self):
        pass

    @staticmethod
    def get_terminal_size():
        if Report.__term_width is None:
            term_width = shutil.get_terminal_size()[0]
            if term_width % 2 == 0:
                term_width -= 1
            Report.__term_width = term_width
        return Report.__term_width

    @staticmethod
    def set_terminal_size(value: int):
        if value % 2 == 0:
            value -= 1
        Report.__term_width = value

    @staticmethod
    def centralize(text, sep=' ', left_border: Optional[str] = None, right_border: Optional[str] = None):
        if left_border is None:
            left_border = sep
        if right_border is None:
            right_border = sep
        term_width = Report.get_terminal_size()
        pad = sep if len(text) % 2 == 0 else ""
        tw = term_width - 2
        filler = sep * int(tw / 2 - len(text) / 2)
        return left_border + pad + filler + text + filler + right_border

    @staticmethod
    def max_just_calc(mat: List[List[str]]) -> List[int]:

        # ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')

        nl = len(mat)
        nc = len(mat[0]) if nl > 0 else 0
        max_list = [0] * nc
        for line in range(nl):
            for c in range(nc):
                data = mat[line][c]
#                data = ansi_escape.sub('', data)
                max_list[c] = max(max_list[c], len(data))
        return max_list

    @staticmethod
    def left_just(mat: List[List[str]]) -> List[List[str]]:
        max_list = Report.max_just_calc(mat)
        output = []
        for line in mat:
            out = []
            for i in range(len(line)):
                if i == 0:
                    out.append(line[i].center(max_list[i], Symbol.cfill))
                else:
                    out.append(line[i].center(max_list[i], Symbol.cfill))
            output.append(out)
        return output

    @staticmethod
    def format_header(user: Optional[str], unit: Unit, source_fill: int = 0, case_fill: int = 0):
        front = ""
        grade = str(unit.grade).zfill(3) if unit.grade else "---"
        if not user:
            front += Symbol.neutral
        elif user == unit.output:
            front += Symbol.success
        else:
            front += Symbol.failure
        front += "[" + str(unit.index).zfill(2) + "] GR:" + grade
        line = front + " " + unit.source.ljust(source_fill) + " (" + unit.case.ljust(case_fill) + ")"
        gr = "      " if unit.duplicated is None else " [" + str(unit.duplicated).zfill(2) + "] "
        return line + gr

    @staticmethod
    def calc_filler(unit_list: List[Unit]) -> List[int]:
        mat = [[x.source, x.case] for x in unit_list]
        max_list = Report.max_just_calc(mat)
        return max_list

    @staticmethod
    def format_header_list(solver: Optional[Solver], unit_list: List[Unit], filler: List[int]) -> str:
        user_list = solver.user if solver else [None] * len(unit_list)
        out = [Report.format_header(output, unit, filler[0], filler[1]) for output, unit in zip(user_list, unit_list)]
        return '\n'.join(out)

    @staticmethod
    def render_white(text: Optional[str]) -> Optional[str]:
        if text is None:
            return None
        text = text.replace(' ', Symbol.whitespace)
        text = text.replace('\n', Symbol.newline + '\n')
        return text

    @staticmethod
    def side_by_side(text_a, text_b, sep=" "):
        term_width = Report.get_terminal_size()
        middle = int(term_width / 2)
        ta = text_a.split("\n")
        tb = text_b.split("\n")
        size = max(len(ta), len(tb)) - 1
        if len(text_b) > 0 and text_b[-1] != '\n':
            size += 1

        data = [list(" " * term_width) for _x in range(size)]

        for line in range(size):
            if line < len(ta) and line < len(tb) and ta[line] == tb[line]:
                data[line][middle] = sep
            else:
                data[line][middle] = "≠"

        for line in range(len(ta)):
            for col in range(len(ta[line])):
                if ta[line][col] != ' ' and col < middle - 1:
                    data[line][col + 1] = ta[line][col]

        for line in range(len(tb)):
            for col in range(len(tb[line])):
                if tb[line][col] != ' ' and col < middle - 1:
                    data[line][col + middle + 2] = tb[line][col]

        return "\n".join(["".join(line) for line in data])

    @staticmethod
    def show_unit_list(user_list: Optional[List[str]], unit_list: List[Unit], is_raw: bool, is_up_down: bool) -> str:
        output = io.StringIO()
        _user_list = user_list if user_list is not None else [None] * len(unit_list)
        for user, unit in zip(_user_list, unit_list):
            output.write(Report.__show_unit(user, unit, is_raw, is_up_down))
        if is_raw or (user_list is None) or is_up_down:
            output.write(Report.centralize(Symbol.hbar, Symbol.hbar) + "\n")
        else:
            output.write(Report.centralize("   ", Symbol.hbar, " ", " ") + "\n")
        return output.getvalue()

    @staticmethod
    def __show_unit(user: Optional[str], unit: Unit, is_raw: bool = False, is_up_down: bool = False) -> str:

        def mount_side_by_side(left, right, filler=" ", middle=" "):
            half = int(Report.get_terminal_size() / 2)
            line = ""
            a = " " + left.center(half - 2, filler) + " "
            if len(a) > half:
                a = a[:half]
            line += a
            line += middle
            b = " " + right.center(half - 2, filler) + " "
            if len(b) > half:
                b = b[:half]
            line += b
            return line

        output = io.StringIO()
        str_input = Report.render_white(unit.input) if not is_raw else unit.input
        str_output = Report.render_white(unit.output) if not is_raw else unit.output
        str_user = Report.render_white(user) if not is_raw else user

        title = " ".join(Report.format_header(user, unit).split(" ")[1:])

        dotted = "-"
        vertical_separator = Symbol.vbar

        if is_up_down or (str_user is None):
            output.write(Report.centralize(Symbol.hbar, Symbol.hbar) + "\n")
            output.write(Report.centralize(title) + "\n")
            output.write(Report.centralize("PROGRAM INPUT", dotted) + "\n")
            output.write(str_input)
            output.write(Report.centralize("EXPECTED OUTPUT", dotted) + "\n")
            output.write(str_output)
            if str_user is not None:
                output.write(Report.centralize("USER OUTPUT", dotted) + "\n")
                output.write(str_user)
                if not str_user.endswith("\n"):
                    output.write("\n")
        else:
            output.write(Report.centralize("   ", Symbol.hbar, " ", " ") + "\n")
            output.write(mount_side_by_side(title, title, " ", vertical_separator) + "\n")
            output.write(mount_side_by_side(" INPUT ", " INPUT ", dotted, vertical_separator) + "\n")
            output.write(Report.side_by_side(str_input, str_input, vertical_separator) + "\n")
            output.write(mount_side_by_side(" EXPECTED OUTPUT ", " USER OUTPUT ", dotted, vertical_separator) + "\n")
            output.write(Report.side_by_side(str_output, str_user, vertical_separator) + "\n")

        return output.getvalue()

    @staticmethod
    def qtd_tests_ratio(unit_list: List[Unit]) -> str:
        unique_qtd = len([x for x in unit_list if x.duplicated is None])
        return "[" + str(unique_qtd).zfill(2) + "/" + str(len(unit_list)).zfill(2) + "]"

    @staticmethod
    def format_resume(line: List[Optional[str]]) -> str:
        out = Symbol.opening
        if line[0]:
            out += line[0]
        if line[1]:
            out += " (" + line[1] + ")"
        if line[2]:
            out += " [" + line[2] + "]"
        if line[3]:
            out += " [" + line[3] + "]"
        return out


class FileSource:
    def __init__(self, label, input_file, output_file):
        self.label = label
        self.input_file = input_file
        self.output_file = output_file

    def __eq__(self, other):
        return self.label == other.label and self.input_file == other.input_file and \
                self.output_file == other.output_file


class PatternLoader:
    pattern: str = ""

    def __init__(self):
        parts = PatternLoader.pattern.split(" ")
        self.input_pattern = parts[0]
        self.output_pattern = parts[1] if len(parts) > 1 else ""
        self._check_pattern()

    def _check_pattern(self):
        self.__check_double_wildcard()
        self.__check_missing_wildcard()

    def __check_double_wildcard(self):
        if self.input_pattern.count("@") > 1 or self.output_pattern.count("@") > 1:
            raise ValueError("  fail: the wildcard @ should be used only once per pattern")

    def __check_missing_wildcard(self):
        if "@" in self.input_pattern and "@" not in self.output_pattern:
            raise ValueError("  fail: is input_pattern has the wildcard @, the input_patter should have too")
        if "@" not in self.input_pattern and "@" in self.output_pattern:
            raise ValueError("  fail: is output_pattern has the wildcard @, the input_pattern should have too")

    def make_file_source(self, label):
        return FileSource(label, self.input_pattern.replace("@", label), self.output_pattern.replace("@", label))

    def get_file_sources(self, filename_list: List[str]) -> List[FileSource]:
        input_re = self.input_pattern.replace(".", "\\.")
        input_re = input_re.replace("@", "(.*)")
        file_source_list = []
        for filename in filename_list:
            match = re.findall(input_re, filename)
            if not match:
                continue
            label = match[0]
            file_source = self.make_file_source(label)
            if file_source.output_file not in filename_list:
                Logger.write("fail: file " + file_source.output_file + " not found\n")
            else:
                file_source_list.append(file_source)
        return file_source_list

    def get_odd_files(self, filename_list) -> List[str]:
        matched = []
        sources = self.get_file_sources(filename_list)
        for source in sources:
            matched.append(source.input_file)
            matched.append(source.output_file)
        unmatched = [file for file in filename_list if file not in matched]
        return unmatched


class Writer:

    def __init__(self):
        pass

    @staticmethod
    def to_vpl(unit: Unit):
        text = "case=" + unit.case + "\n"
        text += "input=" + unit.input
        text += "output=\"" + unit.output + "\"\n"
        if unit.grade is None:
            text += "\n"
        else:
            text += "grade reduction=" + str(unit.grade).zfill(3) + "%\n"
        return text

    @staticmethod
    def to_tio(unit: Unit):
        text = ">>>>>>>>"
        if unit.case != '':
            text += " " + unit.case
        elif unit.grade != 100:
            text += " " + str(unit.grade) + "%"
        text += '\n' + unit.input
        text += "========\n"
        text += unit.output
        if unit.output != '' and unit.output[-1] != '\n':
            text += '\n'
        text += "<<<<<<<<\n"
        return text

    @staticmethod
    def save_dir_files(folder: str, pattern_loader: PatternLoader, label: str, unit: Unit) -> None:
        file_source = pattern_loader.make_file_source(label)
        with open(os.path.join(folder, file_source.input_file), "w") as f:
            f.write(unit.input)
        with open(os.path.join(folder, file_source.output_file), "w") as f:
            f.write(unit.output)

    @staticmethod
    def save_target(target: str, unit_list: List[Unit], force: bool = False):
        def ask_overwrite(file):
            Logger.inc_level()
            Logger.write("file " + file + " found. Overwrite? (y/n) ")
            resp = input()
            Logger.inc_level()
            if resp.lower() == 'y':
                Logger.write("overwrite allowed\n")
                return True
            Logger.write("overwrite denied\n")
            Logger.dec_level()
            Logger.dec_level()
            return False

        def save_dir(_target: str, _unit_list):
            folder = _target
            pattern_loader = PatternLoader()
            number = 0
            for unit in _unit_list:
                Writer.save_dir_files(folder, pattern_loader, str(number).zfill(2), unit)
                number += 1

        def save_file(_target, _unit_list):
            if _target.endswith(".tio"):
                _new = "\n".join([Writer.to_tio(unit) for unit in _unit_list])
            else:
                _new = "\n".join([Writer.to_vpl(unit) for unit in _unit_list])

            file_exists = os.path.isfile(_target)

            if file_exists:
                _old = open(_target).read()
                if _old == _new:
                    Logger.write("no changes in test file\n")
                    return

            if not file_exists or (file_exists and (force or ask_overwrite(_target))):
                with open(_target, "w") as f:
                    f.write(_new)

                    if not force:
                        Logger.write("file " + _target + " wrote\n")

        target_type = Identifier.get_type(target)
        if target_type == IdentifierType.OBI:
            save_dir(target, unit_list)
        elif target_type == IdentifierType.TIO or target_type == IdentifierType.VPL:
            save_file(target, unit_list)
        else:
            Logger.write("fail: target " + target + " do not supported for build operation\n")


class Replacer:

    def __init__(self):
        pass

    @staticmethod
    def _get_borders(regex, text, options) -> List[str]:
        out = []
        last = 0
        for m in re.finditer(regex, text, options):
            out.append(text[last:m.span()[0]])
            last = m.span()[1]
        out.append(text[last:])
        return out

    @staticmethod
    def _merge_tests(borders, tests):
        out = []
        for i in range(len(borders)):
            out.append(borders[i])
            if i < len(tests):
                out.append(tests[i])
        return out

    @staticmethod
    def insert_tests(regex: str, text: str, options: int, tests: List[str]) -> str:
        borders = Replacer._get_borders(regex, text, options)
        return "".join(Replacer._merge_tests(borders, tests))


class Util:

    def __init__(self):
        pass

    @staticmethod
    def copy_to_temp(folder):
        temp_dir = tempfile.mkdtemp()
        for file in os.listdir(folder):
            if os.path.isfile(os.path.join(folder, file)):
                shutil.copyfile(os.path.join(folder, file), os.path.join(temp_dir, file))
        return temp_dir


class ActionExecute:

    def __init__(self):
        pass

    @staticmethod
    def execute(target_list: List[str], folders: List[str], param: Param.Basic) \
            -> List[Tuple[str, int, List[Tuple[str, int]]]]:

        # each wdir is a folder with its sources and solvers
        wdir_list: List[Wdir] = Identifier.mount_wdir_list(target_list, folders, param)

        # description of each wdir
        resume_list: List[List[str]] = [wdir.resume() for wdir in wdir_list]

        # max size for each entry
        sizes: List[int] = Report.max_just_calc(resume_list)

        for resume, wdir in zip(resume_list, wdir_list):
            ActionExecute.print_resume_begin(resume, sizes)
            ActionExecute.print_solvers(wdir, sizes[3], False)

            errors = ActionExecute.report_failure(wdir.solver, wdir.unit_list)
            if errors != "":
                Logger.write(errors, relative=1)
            diffs = ActionExecute.report_diffs(wdir.solver, wdir.unit_list, param)
            if diffs != "":
                Logger.write(diffs)

        return ActionExecute.calc_passed(wdir_list)

    @staticmethod
    def print_resume_begin(resume: List[str], sizes: List[int]):
        _resume = [resume[0].ljust(sizes[0], Symbol.cfill), resume[1].center(sizes[1], Symbol.cfill),
                   resume[2].center(sizes[2], Symbol.cfill), None]
        Logger.write(Report.format_resume(_resume))

    @staticmethod
    def print_solvers(wdir: Wdir, total_size: int, only_show: bool = False):
        if wdir.solver is None:
            Logger.write(" [" + Symbol.failure.center(total_size, Symbol.cfill) + "] " + Symbol.failure + "\n")
            return
        Logger.write(" [")
        if not only_show:
            Execution.execute_solver(wdir.solver, wdir.unit_list)
        Logger.write(" " + wdir.solver.filename + " " + wdir.solver.get_mark() + "]")
        Logger.write("\n")

    @staticmethod
    def report_failure(solver: Solver, unit_list: List[Unit]) -> str:
        if solver.result == ExecutionResult.SUCCESS:
            return ""
        output = IOBuffer()
        if solver.result == ExecutionResult.WRONG_OUTPUT:
            output.write(solver.get_mark() + Symbol.opening + solver.path + " " + solver.result.name + '\n')
            output.write(Report.format_header_list(solver, unit_list, Report.calc_filler(unit_list)) + '\n', 1)
        else:
            output.write(solver.get_mark() + Symbol.opening + solver.path + " " + solver.result.name + "\n")
            output.write(solver.error_msg + "\n", 1)
        return output.getvalue()

    @staticmethod
    def report_diffs(solver: Solver, unit_list: List[Unit], param: Param.Basic) -> str:
        if solver.result != ExecutionResult.WRONG_OUTPUT:
            return ""
        output = IOBuffer()
        if param.diff_mode != DiffMode.NONE:
            new_user = []
            new_unit = []
            for user, unit in zip(solver.user, unit_list):
                if user != unit.output:
                    new_user.append(user)
                    new_unit.append(unit)
            if param.diff_mode == DiffMode.FIRST:
                output.write(Report.centralize("MODE: FIRST FAILURE ONLY") + "\n")
                new_user = [new_user[0]]
                new_unit = [new_unit[0]]
            else:
                output.write(Report.centralize("MODE: ALL FAILURES") + "\n")
            output.write(Report.show_unit_list(new_user, new_unit, param.is_raw, param.is_up_down))
        return output.getvalue()

    @staticmethod
    def calc_passed(wdir_list: List[Wdir]) -> List[Tuple[str, int, List[Tuple[str, int]]]]:
        output: List[Tuple[str, int, List[Tuple[str, int]]]] = []
        for wdir in wdir_list:
            wdir_out: List[Tuple[str, int]] = []
            passed = len([unit for user, unit in zip(wdir.solver.user, wdir.unit_list) if user == unit.output])
            wdir_out.append((wdir.solver.filename, passed))
            output += [(wdir.folder, len(wdir.unit_list), wdir_out)]
        return output


class ActionList:

    def __init__(self):
        pass

    @staticmethod
    def list(target_list: List[str], folders: List[str], param: Param.Basic) -> List[Tuple[str, int]]:
        wdir_list = Identifier.mount_wdir_list(target_list, folders, param)
        resume_list = [wdir.resume() for wdir in wdir_list]
        sizes = Report.max_just_calc(resume_list)
        headers_filler = ActionList.calc_filler(wdir_list)
        for resume, wdir in zip(resume_list, wdir_list):
            ActionExecute.print_resume_begin(resume, sizes)
            ActionExecute.print_solvers(wdir, sizes[3], True)
            if wdir.unit_list:
                Logger.write(Report.format_header_list(None, wdir.unit_list, headers_filler) + '\n', relative=1)
            if param.display:
                Logger.write(Report.show_unit_list(None, wdir.unit_list, param.is_raw, param.is_up_down), 0)
        return [(wdir.folder, len(wdir.unit_list)) for wdir in wdir_list]

    @staticmethod
    def calc_filler(wdir_list: List[Wdir]) -> List[int]:
        all_unit_lists = []
        for wdir in wdir_list:
            all_unit_lists += wdir.unit_list
        return Report.calc_filler(all_unit_lists)

    @staticmethod
    def format_resume(wdir_list: List[Wdir]) -> List[str]:
        mat = [wdir.resume() for wdir in wdir_list]
        mat = Report.left_just(mat)
        return [Report.format_resume(line) for line in mat]


class Actions:

    def __init__(self):
        pass

    @staticmethod
    def list(target_list: List[str], folders: List[str], param: Param.Basic) -> List[Tuple[str, int]]:
        return ActionList.list(target_list, folders, param)

    @staticmethod
    def execute(target_list: List[str], folders: List[str], param: Param.Basic) -> \
            List[Tuple[str, int, List[Tuple[str, int]]]]:
        return ActionExecute.execute(target_list, folders, param)

    @staticmethod
    def build(target_out: str, source_list: List[str], param: Param.Manip, to_force: bool) -> bool:
        try:
            Logger.inc_level()
            wdir = Wdir(".").set_sources(source_list).parse_sources()
            wdir.manipulate(param)
            Writer.save_target(target_out, wdir.unit_list, to_force)
            Logger.dec_level()
        except FileNotFoundError as e:
            Logger.write(str(e) + "\n")
            Logger.dec_level()
            return False
        return True

    @staticmethod
    def update(target_list: List[str], param: Param.Manip, solver: Optional[str]) -> bool:
        for target in target_list:
            wdir = Wdir(".").set_sources([target]).parse_sources()
            wdir.manipulate(param)
            if solver:
                wdir.replace_input(Solver(solver))
            if not target.endswith(".md"):
                Writer.save_target(target, wdir.unit_list, True)
            else:
                with open(target) as f:
                    text = f.read()
                str_tests = [Writer.to_tio(unit) for unit in wdir.unit_list]
                output = Replacer.insert_tests(Loader.regex_tio, text, re.MULTILINE | re.DOTALL, str_tests)
                with open(target, "w") as f:
                    f.write(output)
        return True


class ITable:
    options_base = ["fup", "ed", "poo"]
    options_term = ["40", "60", "80", "100", "120", "140", "160", "180", "200"]
    options_view = ["side", "down"]
    options_mark = ["show", "hide"]
    options_exte = ["c", "cpp", "js", "ts", "py", "java", "hs"]

    @staticmethod
    def choose(intro, opt_list, par = ""):
        if par in opt_list:
            return par
        print(intro + "[ " + ", ".join(opt_list) + " ]: ", end="")
        value = input().lower()
        if value not in opt_list:
            return ITable.choose(intro, opt_list)
        return value

    @staticmethod
    def cls():
        # os.system('cls' if os.name == 'nt' else 'clear')
        pass
        
    @staticmethod
    def validate_label(label):
        if len(label) != 3:
            return False
        for c in label:
            if not c.isdigit():
                return False
        return True

    @staticmethod
    def choose_label(label = ""):
        if ITable.validate_label(label):
            return label
        while True:
            print("Label: @", end="")
            label = input()
            if ITable.validate_label(label):
                break
        return label

    @staticmethod
    def action_down(ui_list: List[str], base: str) -> str:
        label = "" if len(ui_list) < 2 else ui_list[1]
        label = ITable.choose_label(label)

        ext = "" if len(ui_list) < 3 else ui_list[2]
        ext = ITable.choose("Choose extension ", ITable.options_exte, ext)

        print("{} {} {}".format(label, ext, base))
        Main.down(base, label, ext)
        return "down" + " " + label + " " + ext

    @staticmethod
    def action_run(ui_list, mark_mode, view_mode, term_size) -> str:
        label = "" if len(ui_list) < 2 else ui_list[1]
        label = ITable.choose_label(label)
        print("Running problem " + label + " ...")
        
        Report.set_terminal_size(int(term_size))
        param = Param.Basic().set_raw(mark_mode == "hide")
        if view_mode == "down":
            param.set_up_down(True)
        param.set_diff_mode(DiffMode.ALL)
        Actions.execute([], [label], param)

        return "run " + label

    @staticmethod
    def choose_base(ui_list: List[str]) -> str:
        if len(ui_list) == 2 and ui_list[1] in ITable.options_base:
            return ui_list[1]

        return ITable.choose("Choose database ", ITable.options_base)

    @staticmethod
    def choose_term(ui_list: List[str]) -> str:
        if len(ui_list) == 2 and ui_list[1] in ITable.options_term:
            return ui_list[1]
        return ITable.choose("Choose termsize ", ITable.options_term)

    @staticmethod
    def create_default_config(configfile):
        config = configparser.ConfigParser()
        config["DEFAULT"] = {
            "base": ITable.options_base[0],
            "term": ITable.options_term[0],
            "view": ITable.options_view[0],
            "mark": ITable.options_mark[0],
            "last_cmd": ""
        }
        with open(configfile, "w") as f:
            config.write(f)

    @staticmethod
    def not_str(value: str) -> str:
        if value == ITable.options_mark[0]:
            return ITable.options_mark[1]
        if value == ITable.options_mark[1]:
            return ITable.options_mark[0]
        
        if value == ITable.options_view[0]:
            return ITable.options_view[1]
        if value == ITable.options_view[1]:
            return ITable.options_view[0]

    @staticmethod
    def print_header(config):
        
        pad = lambda s, w: s + (w - len(s)) * " "

        base  = pad(config["DEFAULT"]["base"], 4).upper()
        term  = pad(config["DEFAULT"]["term"], 4)
        view  = pad(config["DEFAULT"]["view"], 4).upper()
        mark = pad(config["DEFAULT"]["mark"], 4).upper()
        last_cmd = config["DEFAULT"]["last_cmd"]

        # padding function using length
        print("┌─────┬─────┬─────┬─────┬─────┬────┐")
        print("│h.elp│b.ase│t.erm│v.iew│m.ark│r.un│")
        print("├─────┼┈┈┈┈┈┼┈┈┈┈┈┼┈┈┈┈┈┼┈┈┈┈┈┼────┤")
        print("│d.own│ {}│ {}│{} │{} │".format(base, term, view, mark) + "e.nd│");
        print("└─────┴─────┴─────┴─────┴─────┴────┘")
        print("(" + last_cmd + "): ", end="")

    @staticmethod
    def validate_config(config):
        if "DEFAULT" not in config:
            return False
        if "base" not in config["DEFAULT"] or config["DEFAULT"]["base"] not in ITable.options_base:
            return False
        if "term" not in config["DEFAULT"] or config["DEFAULT"]["term"] not in ITable.options_term:
            return False
        if "view" not in config["DEFAULT"] or config["DEFAULT"]["view"] not in ITable.options_view:
            return False
        if "mark" not in config["DEFAULT"] or config["DEFAULT"]["mark"] not in ITable.options_mark:
            return False
        if "last_cmd" not in config["DEFAULT"]:
            return False
        return True

    @staticmethod
    def print_help():
        print("Digite a letra ou o comando e aperte enter.")
        print("h ou help: mostra esse help.")
        print("b ou base: muda a base de dados entre as disciplinas.")
        print("t ou term: muda a largura do terminal utilizado para mostrar os erros.")
        print("v ou view: alterna o modo de visualização de erros entre up_down e lado_a_lado.")
        print("m ou mark: show mostra os whitespaces e hide os esconde.")
        print("d ou down: faz o download do problema utilizando o label e a extensão.")
        print("r ou run : roda o problema utilizando sua solução contra os testes.")
        print("e ou end : termina o programa.")
        print("Na linha de execução já aparece o último comando entre (), para reexecutar basta apertar enter.")

    @staticmethod
    def search_config(filename) -> str:
        # recursively search for config file in parent directories
        path = os.getcwd()
        while True:
            configfile = os.path.join(path, filename)
            if os.path.exists(configfile):
                return configfile
            if path == "/":
                return ""
            path = os.path.dirname(path)

    @staticmethod
    def main(_args):
        default_config_file = ".config.ini"
        config = configparser.ConfigParser()
        ITable.cls()

        configfile = ITable.search_config(default_config_file)
        if configfile != "":
            os.chdir(os.path.dirname(configfile))
        else:
            configfile = default_config_file
            print("Creating default config file")
            ITable.create_default_config(configfile)
        
        config.read(configfile)
        
        if not ITable.validate_config(config):
            ITable.create_default_config(configfile)
            config.read(configfile)

        while True: 
            ITable.print_header(config)

            line = input()
            if line == "":
                line = config["DEFAULT"]["last_cmd"]

            ui_list = line.split(" ")
            cmd = ui_list[0]

            if cmd == "e" or cmd == "end":
                break
            elif cmd == "h" or cmd == "help":
                ITable.print_help()
            elif cmd == "b" or cmd == "base":
                value: str = ITable.choose_base(ui_list)
                config["DEFAULT"]["base"] = value
                ITable.cls()
            elif cmd == "t" or cmd == "term":
                config["DEFAULT"]["term"] = ITable.choose_term(ui_list)
                ITable.cls()
            elif cmd == "v" or cmd == "view":
                config["DEFAULT"]["view"] = ITable.not_str(config["DEFAULT"]["view"])
                ITable.cls()
            elif cmd == "m" or cmd == "mark":
                config["DEFAULT"]["mark"] = ITable.not_str(config["DEFAULT"]["mark"])
                ITable.cls()
            elif cmd == "d" or cmd == "down":
                last_cmd = ITable.action_down(ui_list, config["DEFAULT"]["base"])
                config["DEFAULT"]["last_cmd"] = last_cmd
            elif cmd == "r" or cmd == "run":
                last_cmd = ITable.action_run(ui_list, config["DEFAULT"]["mark"], config["DEFAULT"]["view"], config["DEFAULT"]["term"])
                config["DEFAULT"]["last_cmd"] = last_cmd
            else:
                print("Invalid command")

            with open(default_config_file, "w") as f:
                config.write(f)

        with open(default_config_file, "w") as f:
            config.write(f)



class Main:
    @staticmethod
    def execute(args):
        if args.width is not None:
            Report.set_terminal_size(args.width)
        PatternLoader.pattern = args.pattern
        param = Param.Basic().set_index(args.index).set_raw(args.raw)
        if args.vertical:
            param.set_up_down(True)
        if args.all:
            param.set_diff_mode(DiffMode.ALL)
        elif args.none:
            param.set_diff_mode(DiffMode.NONE)
        if Actions.execute(args.target_list, args.folders, param):
            return 0
        return 1

    @staticmethod
    def save_as(file_url, filename) -> bool:
        try:
            urllib.request.urlretrieve(file_url, filename)
        except urllib.error.HTTPError:
            return False
        return True

    @staticmethod
    def create_file(content, path, label=""):
        with open(path, "w") as f:
            f.write(content)
        print(path, label)

    @staticmethod
    def unpack_json(loaded, index):
        # extracting all files to folder
        for entry in loaded["upload"]:
            if entry["name"] == "vpl_evaluate.cases":
                Main.create_file(entry["contents"], os.path.join(index, "cases.tio"))

        for entry in loaded["keep"]:
            Main.create_file(entry["contents"], os.path.join(index, entry["name"]))

        for entry in loaded["required"]:
            Main.create_file(entry["contents"], os.path.join(index, entry["name"]), "(Required)")

    @staticmethod
    def down(args):
        Main.down(args.disc, args.index, args.extension)

    @staticmethod
    def down(disc, index, ext):

        # create dir
        if not os.path.exists(index):
            os.mkdir(index)

        cache_url = "https://raw.githubusercontent.com/qxcode" + disc + "/arcade/master/base/" + index + "/.cache/"

        if Main.save_as(cache_url + "Readme.md", index + os.sep + "Readme.md"):
            print(index + os.sep + "Readme.md")
        else:
            print("Problem not found")
            return

        mapi_path = os.path.join(index + "mapi.json")
        if not Main.save_as(cache_url + "mapi.json", mapi_path):
            print("Problem not found")
            return
            
        with open(mapi_path) as f:
            loaded = json.load(f)
        os.remove(mapi_path)

        Main.unpack_json(loaded, index)

        if len(loaded["required"]) == 0:
            draft_path = os.path.join(index, "solver." + ext)
            if Main.save_as(cache_url + "solver_draft." + ext, draft_path):
                print(draft_path, "(Draft)")
            else:
                open(draft_path, "w")
                print(draft_path, "(Empty)")

    @staticmethod
    def list(args):
        if args.width is not None:
            Report.set_terminal_size(args.width)
        PatternLoader.pattern = args.pattern
        param = Param.Basic().set_index(args.index).set_raw(args.raw).set_display(args.display)
        Actions.list(args.target_list, args.folders, param)
        return 0

    @staticmethod
    def build(args):
        if args.width is not None:
            Report.set_terminal_size(args.width)
        PatternLoader.pattern = args.pattern
        Actions.build(args.target, args.target_list, Param.Manip(args.unlabel, args.sort, args.number), args.force)
        return 0

    @staticmethod
    def update(args):
        if args.width is not None:
            Report.set_terminal_size(args.width)
        PatternLoader.pattern = args.pattern
        Actions.update(args.target_list, Param.Manip(args.unlabel, args.sort, args.number), args.cmd)
        return 0

    @staticmethod
    def tk_update(_args):
        tdir = tempfile.mkdtemp()
        installer = os.path.join(tdir, "installer.sh")
        cmd = ["wget", "https://raw.githubusercontent.com/senapk/tk/master/tools/install_linux.sh", "-O", installer]
        code, _data, error = Runner.subprocess_run(cmd)
        if code != 0:
            print(error)
            exit(1)
        cmd = ["sh", installer]
        code, out, err = Runner.subprocess_run(cmd)
        if code == 0:
            print(out)
        else:
            print(err)
        return 0

    @staticmethod
    def main():
        parent_basic = argparse.ArgumentParser(add_help=False)
        parent_basic.add_argument('--width', '-w', type=int, help="term width")
        parent_basic.add_argument('--raw', '-r', action='store_true', help="raw mode, disable  whitespaces rendering.")
        parent_basic.add_argument('--index', '-i', metavar="I", type=int, help='run a specific index.')
        parent_basic.add_argument('--pattern', '-p', metavar="P", type=str, default='@.in @.sol',
                                  help='pattern load/save a folder, default: "@.in @.sol"')

        parent_manip = argparse.ArgumentParser(add_help=False)
        parent_manip.add_argument('--width', '-w', type=int, help="term width.")
        parent_manip.add_argument('--unlabel', '-u', action='store_true', help='remove all labels.')
        parent_manip.add_argument('--number', '-n', action='store_true', help='number labels.')
        parent_manip.add_argument('--sort', '-s', action='store_true', help="sort test cases by input size.")
        parent_manip.add_argument('--pattern', '-p', metavar="@.in @.out", type=str, default='@.in @.sol',
                                  help='pattern load/save a folder, default: "@.in @.sol"')

        parser = argparse.ArgumentParser(prog='tk')
        subparsers = parser.add_subparsers(title='subcommands', help='help for subcommand.')

        # list
        parser_l = subparsers.add_parser('list', parents=[parent_basic], help='show case packs or folders.')
        parser_l.add_argument('target_list', metavar='T', type=str, nargs='*', help='targets.')
        parser_l.add_argument('--display', '-d', action="store_true", help='display full test description.')
        parser_l.add_argument('--folders', '-f', metavar='T', type=str, nargs='+', help='folder list')
        parser_l.set_defaults(func=Main.list)

        # run
        parser_r = subparsers.add_parser('run', parents=[parent_basic], help='run you solver.')
        parser_r.add_argument('target_list', metavar='T', type=str, nargs='*', help='solvers, test cases or folders.')
        parser_r.add_argument('--folders', '-f', metavar='T', type=str, nargs='+', help='folder list')
        parser_r.add_argument('--vertical', '-v', action='store_true', help="use vertical mode.")
        parser_r.add_argument('--label', '-l', type=str, help="only use cases that match the label.")
        parser_r.add_argument('--all', '-a', action='store_true', help="show all failures.")
        parser_r.add_argument('--none', '-n', action='store_true', help="show none failures.")
        parser_r.set_defaults(func=Main.execute)

        # build
        parser_b = subparsers.add_parser('build', parents=[parent_manip], help='build a test target.')
        parser_b.add_argument('target', metavar='T_OUT', type=str, help='target to be build.')
        parser_b.add_argument('target_list', metavar='T', type=str, nargs='+', help='input test targets.')
        parser_b.add_argument('--force', '-f', action='store_true', help='enable overwrite.')
        parser_b.set_defaults(func=Main.build)

        # update
        parser_u = subparsers.add_parser('update', parents=[parent_manip], help='update a test target.')
        parser_u.add_argument('target_list', metavar='T', type=str, nargs='+', help='input test targets.')
        parser_u.add_argument('--cmd', '-c', type=str, help="solver file or command to update outputs.")
        parser_u.set_defaults(func=Main.update)

        # down
        parser_d = subparsers.add_parser('down', help='download test from remote repository.')
        parser_d.add_argument('disc', type=str, help=" [ fup | ed | poo ]")
        parser_d.add_argument('index', type=str, help="3 digits label like 025")
        parser_d.add_argument('extension', type=str, help="[ cpp | js | py | java | c ]")
        parser_d.set_defaults(func=Main.down)

        # tk_update
        parser_tkupdate = subparsers.add_parser('tkupdate', help='update tk script(linux only).')
        parser_tkupdate.set_defaults(func=Main.tk_update)

        # loop
        parser_itable = subparsers.add_parser('loop', help='loop interactive mode')
        parser_itable.set_defaults(func=ITable.main)

        args = parser.parse_args()
        if len(sys.argv) == 1:
            Actions.execute([""], [], Param.Basic())
        else:
            try:
                args.func(args)
            except ValueError as e:
                Logger.write(str(e) + '\n')


if __name__ == '__main__':
    try:
        Main.main()
    except KeyboardInterrupt:
        Logger.write("\n\nKeyboard Interrupt\n")

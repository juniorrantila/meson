# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 The Meson development team

from __future__ import annotations

import subprocess, os.path
import typing as T

from ..mesonlib import EnvironmentException

from .compilers import Compiler, clike_debug_args, clike_optimization_args

if T.TYPE_CHECKING:
    from ..envconfig import MachineInfo
    from ..environment import Environment
    from ..linkers.linkers import DynamicLinker
    from ..mesonlib import MachineChoice

class CobolCompiler(Compiler):

    LINKER_PREFIX = '-Q Wl,'
    language = 'cobol'
    id = 'GnuCOBOL'

    def __init__(self, exelist: T.List[str], version: str, for_machine: MachineChoice,
                 is_cross: bool, info: 'MachineInfo', full_version: T.Optional[str] = None,
                 linker: T.Optional['DynamicLinker'] = None):
        super().__init__([], exelist, version, for_machine, info,
                         is_cross=is_cross, full_version=full_version,
                         linker=linker)
        self.version = version

    def get_pic_args(self) -> T.List[str]:
        return []

    def get_pie_args(self) -> T.List[str]:
        return []

    def needs_static_linker(self) -> bool:
        return True

    def get_werror_args(self) -> T.List[str]:
        return ['-Werror']

    def get_dependency_gen_args(self, outtarget: str, outfile: str) -> T.List[str]:
        return ['-MT', self.depfile_for_object(outtarget)]

    def depfile_for_object(self, objfile: str) -> T.Optional[str]:
        return os.path.splitext(objfile)[0] + '.' + self.get_depfile_suffix()

    def get_depfile_suffix(self) -> str:
        return 'd'

    def get_output_args(self, target: str) -> T.List[str]:
        return ['-o', target]

    def get_always_args(self) -> T.List[str]:
        return []

    # def get_header_import_args(self, headername: str) -> T.List[str]:
    #     return ['-import-objc-header', headername]

    def get_warn_args(self, level: str) -> T.List[str]:
        return []

    # def get_std_exe_link_args(self) -> T.List[str]:
    #     return ['-x']

    # def get_module_args(self, modname: str) -> T.List[str]:
    #     return ['-module-name', modname]

    # def get_mod_gen_args(self) -> T.List[str]:
    #     return ['-emit-module']

    def get_include_args(self, path: str, is_system: bool) -> T.List[str]:
        return ['-I' + path]

    def get_compile_only_args(self) -> T.List[str]:
        return ['-c']

    def compute_parameters_with_absolute_paths(self, parameter_list: T.List[str],
                                               build_dir: str) -> T.List[str]:
        for idx, i in enumerate(parameter_list):
            if i[:2] == '-I' or i[:2] == '-L':
                parameter_list[idx] = i[:2] + os.path.normpath(os.path.join(build_dir, i[2:]))

        return parameter_list

    def sanity_check(self, work_dir: str, environment: 'Environment') -> None:
        src = 'coboltest.cob'
        source_name = os.path.join(work_dir, src)
        output_name = os.path.join(work_dir, 'coboltest')
        with open(source_name, 'w', encoding='utf-8') as ofile:
            content = '''
      * COBOL fixed-form must be indented
000100 IDENTIFICATION DIVISION.
000200 PROGRAM-ID. hello.
000300 PROCEDURE DIVISION.
000400 DISPLAY "Cobol compilation is working.".
000500 STOP RUN.
            '''
            ofile.write(content)
        pc = subprocess.Popen(self.exelist + ['-x', '-o', output_name, src], cwd=work_dir)
        pc.wait()
        if pc.returncode != 0:
            raise EnvironmentException('Cobol compiler %s cannot compile programs.' % self.name_string())
        if self.is_cross:
            # Can't check if the binaries run so we have to assume they do
            return
        if subprocess.call(output_name) != 0:
            raise EnvironmentException('Executables created by Cobol compiler %s are not runnable.' % self.name_string())

    def get_debug_args(self, is_debug: bool) -> T.List[str]:
        return clike_debug_args[is_debug]

    def get_optimization_args(self, optimization_level: str) -> T.List[str]:
        return clike_optimization_args[optimization_level]

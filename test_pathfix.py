import os
import shutil
import subprocess
import sys
import unittest

# The following constant and function are based on os_helper
# https://github.com/python/cpython/blob/main/Lib/test/support/os_helper.py
TESTFN = "@test_{}_tmp".format(os.getpid()) + "-\xe0\xf2\u0258\u0141\u011f"


def _unlink(path):
    try:
        os.unlink(path)
    except (FileNotFoundError, NotADirectoryError):
        pass


class TestPathfixFunctional(unittest.TestCase):
    script = os.path.join(os.path.dirname(__file__), 'pathfix.py')

    def setUp(self):
        self.addCleanup(_unlink, TESTFN)

    def pathfix(self, shebang, pathfix_flags, exitcode=0, stdout='', stderr='',
                directory=''):
        if directory:
            # bpo-38347: Test filename should contain lowercase, uppercase,
            # "-", "_" and digits.
            filename = os.path.join(directory, 'script-A_1.py')
            pathfix_arg = directory
        else:
            filename = TESTFN
            pathfix_arg = filename

        with open(filename, 'w', encoding='utf8') as f:
            f.write(f'{shebang}\n' + 'print("Hello world")\n')

        encoding = sys.getfilesystemencoding()
        proc = subprocess.run(
            [sys.executable, self.script,
             *pathfix_flags, '-n', pathfix_arg],
            env={**os.environ, 'PYTHONIOENCODING': encoding},
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if stdout == '' and proc.returncode == 0:
            stdout = f'{filename}: updating\n'
        self.assertEqual(proc.returncode, exitcode, proc)
        self.assertEqual(proc.stdout.decode(encoding), stdout.replace('\n', os.linesep), proc)
        self.assertEqual(proc.stderr.decode(encoding), stderr.replace('\n', os.linesep), proc)

        with open(filename, 'r', encoding='utf8') as f:
            output = f.read()

        lines = output.split('\n')
        self.assertEqual(lines[1:], ['print("Hello world")', ''])
        new_shebang = lines[0]

        if proc.returncode != 0:
            self.assertEqual(shebang, new_shebang)

        return new_shebang

    def test_recursive(self):
        tmpdir = TESTFN + '.d'
        self.addCleanup(shutil.rmtree, tmpdir)
        os.mkdir(tmpdir)
        expected_stderr = f"recursedown('{os.path.basename(tmpdir)}')\n"
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python',
                ['-i', '/usr/bin/python3'],
                directory=tmpdir,
                stderr=expected_stderr),
            '#! /usr/bin/python3')

    def test_pathfix(self):
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python',
                ['-i', '/usr/bin/python3']),
            '#! /usr/bin/python3')
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python -R',
                ['-i', '/usr/bin/python3']),
            '#! /usr/bin/python3')

    def test_pathfix_keeping_flags(self):
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python -R',
                ['-i', '/usr/bin/python3', '-k']),
            '#! /usr/bin/python3 -R')
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python',
                ['-i', '/usr/bin/python3', '-k']),
            '#! /usr/bin/python3')

    def test_pathfix_adding_flag(self):
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python',
                ['-i', '/usr/bin/python3', '-a', 's']),
            '#! /usr/bin/python3 -s')
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python -S',
                ['-i', '/usr/bin/python3', '-a', 's']),
            '#! /usr/bin/python3 -s')
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python -V',
                ['-i', '/usr/bin/python3', '-a', 'v', '-k']),
            '#! /usr/bin/python3 -vV')
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python',
                ['-i', '/usr/bin/python3', '-a', 'Rs']),
            '#! /usr/bin/python3 -Rs')
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python -W default',
                ['-i', '/usr/bin/python3', '-a', 's', '-k']),
            '#! /usr/bin/python3 -sW default')

    def test_pathfix_adding_errors(self):
        self.pathfix(
            '#! /usr/bin/env python -E',
            ['-i', '/usr/bin/python3', '-a', 'W default', '-k'],
            exitcode=2,
            stderr="-a option doesn't support whitespaces")


if __name__ == '__main__':
    unittest.main()

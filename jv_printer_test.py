import os
import sys
import tempfile
import unittest

from subprocess import Popen, PIPE

PATH_TO_JQ = os.getenv('PATH_TO_JQ', './jq/jq')

class jv_parser_test(unittest.TestCase):

    def setUp(self):
        if not os.path.isfile(PATH_TO_JQ):
            msg = """
                    jq binary not found at '%s'.
                    To look in a different path, use:
                    env PATH_TO_JQ=/path/to/jq python %s"""
            raise ValueError(msg % (PATH_TO_JQ, __file__))

        self.gdbinit_fd, self.gdbinit_path = tempfile.mkstemp()
        gdbinit_sock = os.fdopen(self.gdbinit_fd, 'w')

        with open('./gdbinit.template', 'r') as gdbinit_template:
            for line in gdbinit_template:
                line = line.replace('/path/to/jq-gdb', os.getcwd())
                gdbinit_sock.write(line)

        gdbinit_sock.close()

    def tearDown(self):
        os.remove(self.gdbinit_path)

    def gdb(self, expr):
        cmd = ['gdb',
                '-q',                     # less output from gdb
                '-nx',                    # ignore ~/.gdbinit
                '-x', self.gdbinit_path,  # use our gdbinit
                '--args',
                    PATH_TO_JQ,
                    '--arg', 'k', 'v',    # test_local_variable looks for this
                    '.']
        proc = Popen(cmd, stdin=PIPE, stdout=PIPE)
        outs, errs = proc.communicate(input=_str("""
                break jq_compile_args
                run
                print %s
                quit
                """ % expr))
        lines = outs.splitlines()
        expected = _str("(gdb) $1 = jv: ")
        result = next(line for line in lines if line.startswith(expected))
        return result[len(expected):]

    def test_local_variable(self):
        self.assertEqual(self.gdb('args'), _str('[{"name":"k","value":"v"}]'))

    def test_invalid(self):
        self.assertEqual(self.gdb('jv_invalid()'), _str('<invalid>'))

    def test_invalid_with_msg(self):
        mk_invalid = 'jv_invalid_with_msg(jv_string("msg"))'
        self.assertEqual(self.gdb(mk_invalid), _str('<invalid:"msg">'))

    def test_null(self):
        self.assertEqual(self.gdb('jv_null()'), _str('null'))

    def test_false(self):
        self.assertEqual(self.gdb('jv_false()'), _str('false'))

    def test_true(self):
        self.assertEqual(self.gdb('jv_true()'), _str('true'))

    def test_integer(self):
        self.assertEqual(self.gdb('jv_number(100)'), _str('100'))

    def test_double(self):
        self.assertEqual(self.gdb('jv_number(1.618034)'), _str('1.618034'))

    def test_string(self):
        self.assertEqual(self.gdb('jv_string("test")'), _str('"test"'))

    def test_empty_array(self):
        self.assertEqual(self.gdb('jv_array()'), _str('[]'))

    def test_array(self):
        mk_array = 'jv_array_set(jv_array(), 2, jv_true())'
        self.assertEqual(self.gdb(mk_array), _str('[null,null,true]'))

    def test_empty_object(self):
        self.assertEqual(self.gdb('jv_object()'), _str('{}'))

    def test_object(self):
        mk_object = 'jv_object_set(jv_object(), jv_string("k"), jv_string("v"))'
        self.assertEqual(self.gdb(mk_object), _str('{"k":"v"}'))


def _str(orig):
    """For Python 3, convert string to bytes."""
    if sys.version_info[0] < 3:
        return orig
    else:
        return bytes(orig, "UTF-8")


if __name__ == '__main__':
    if sys.version_info[:2] <= (2, 6):
        unittest.main() # verbosity parameter did not exist
    else:
        unittest.main(verbosity=2)

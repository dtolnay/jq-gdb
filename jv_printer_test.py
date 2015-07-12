import os
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
        outs, errs = proc.communicate("""
                break jq_compile_args
                run
                print %s
                quit
                """ % expr)
        lines = outs.splitlines()
        expected = "(gdb) $1 = jv: "
        result = next(line for line in lines if line.startswith(expected))
        return result[len(expected):]

    def test_local_variable(self):
        self.assertEqual(self.gdb('args'), '[{"name":"k","value":"v"}]')

    def test_invalid(self):
        self.assertEqual(self.gdb('jv_invalid()'), '<invalid>')

    def test_invalid_with_msg(self):
        mk_invalid = 'jv_invalid_with_msg(jv_string("msg"))'
        self.assertEqual(self.gdb(mk_invalid), '<invalid:"msg">')

    def test_null(self):
        self.assertEqual(self.gdb('jv_null()'), 'null')

    def test_false(self):
        self.assertEqual(self.gdb('jv_false()'), 'false')

    def test_true(self):
        self.assertEqual(self.gdb('jv_true()'), 'true')

    def test_integer(self):
        self.assertEqual(self.gdb('jv_number(100)'), '100')

    def test_double(self):
        self.assertEqual(self.gdb('jv_number(1.618034)'), '1.618034')

    def test_string(self):
        self.assertEqual(self.gdb('jv_string("test")'), '"test"')

    def test_empty_array(self):
        self.assertEqual(self.gdb('jv_array()'), '[]')

    def test_array(self):
        mk_array = 'jv_array_set(jv_array(), 2, jv_true())'
        self.assertEqual(self.gdb(mk_array), '[null,null,true]')

    def test_empty_object(self):
        self.assertEqual(self.gdb('jv_object()'), '{}')

    def test_object(self):
        mk_object = 'jv_object_set(jv_object(), jv_string("k"), jv_string("v"))'
        self.assertEqual(self.gdb(mk_object), '{"k":"v"}')

if __name__ == '__main__':
    unittest.main(verbosity=2)

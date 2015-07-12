import gdb

_have_gdb_printing = True
try:
    import gdb.printing
except ImportError:
    _have_gdb_printing = False

def jv_to_eval_string(jv):
    """Make a string that can be passed to gdb.parse_and_eval to
    produce the original jv.
    """
    kind_flags = jv['kind_flags']
    pad_ = jv['pad_']
    offset = jv['offset']
    size = jv['size']
    ptr = jv['u']['ptr']
    return ('((jv){0x%x, 0x%x, 0x%x, 0x%x, (void*)0x%x})' %
            (kind_flags, pad_, offset, size, ptr))

class jv_printer:
    """Print a jv object."""

    def __init__(self, val):
        self.val = val

    def to_string(self):
        val_s = jv_to_eval_string(self.val)
        print_cmd = 'jv_dump_string(jv_copy(%s), JV_PRINT_INVALID)' 
        tostr = gdb.parse_and_eval(print_cmd % val_s)
        tostr_s = jv_to_eval_string(tostr)
        chars = gdb.parse_and_eval('jv_string_value(%s)' % tostr_s)
        result = "jv: " + chars.string()
        gdb.parse_and_eval('jv_free(%s)' % tostr_s)
        return result

def jv_lookup(val):
    if val.type.strip_typedefs().code != gdb.TYPE_CODE_STRUCT:
        return None
    expected = ['kind_flags', 'pad_', 'offset', 'size', 'u']
    if [f.name for f in val.type.fields()] == expected:
        return jv_printer(val)
    return None

def register_jv_printer():
    if _have_gdb_printing:
        gdb.printing.register_pretty_printer(None, jv_lookup)
    else:
        gdb.pretty_printers.append(jv_lookup)

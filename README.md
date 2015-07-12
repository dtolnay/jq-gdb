# jq-gdb
A gdb pretty-printer for jv objects in [jq](https://github.com/stedolan/jq) and other programs using libjq.

Setup:
- Create `~/.gdbinit` if it does not already exist
- Copy the contents of `gdbinit.template` to the end of `~/.gdbinit`
- Replace `'/path/to/jq-gdb'` with the location to which you cloned this repo

Usage:

<pre>
david@genie:/github/jq$ <b>gdb -q --args ./jq -n '{"k":"v"}'</b>
Reading symbols from ./jq...done.
(gdb) <b>break execute.c:162 if jv_get_kind(val) != JV_KIND_NULL</b>
Breakpoint 1 at 0x491de8: file execute.c, line 162.
(gdb) <b>run</b>
Starting program: /github/jq/jq -n \{\"k\":\"v\"\}
Breakpoint 1, stack_push (jq=0x9b2c80, val=jv: {"k":"v"}) at execute.c:162
162	  jq->stk_top = stack_push_block(&jq->stk, jq->stk_top, sizeof(jv));
(gdb) <b>print val</b>
$1 = jv: {"k":"v"}
(gdb) <b>print/r val</b>
$3 = {kind_flags = 7 '\a', pad_ = 0 '\000', offset = 0, size = 8, u = {ptr = 0x9b4a90, number = 5.0281890807548674e-317}}
(gdb) <b>print jv_array_set(jv_array(), 10, jv_string("hi"))</b>
$3 = jv: [null,null,null,null,null,null,null,null,null,null,"hi"]
(gdb) <b>quit</b>
</pre>

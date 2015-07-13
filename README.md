# jq-gdb
A gdb pretty-printer for jv objects in [jq](https://github.com/stedolan/jq)
and other programs using [libjq](https://github.com/stedolan/jq/wiki/C-API:-libjq).

[![Build Status](https://travis-ci.org/dtolnay/jq-gdb.svg?branch=master)](https://travis-ci.org/dtolnay/jq-gdb)

### Setup
- Clone this repo somewhere permanent
- Create `~/.gdbinit` if it does not already exist
- Copy the contents of `gdbinit.template` to the end of `~/.gdbinit`
- Replace `'/path/to/jq-gdb'` with the path to the clone

### Usage
<pre>
david@genie:/github/jq$ <b>gdb -q --args ./jq -n '{"k":"v"}'</b>
Reading symbols from ./jq...done.
(gdb) <b>break execute.c:162 if jv&#95;get&#95;kind(val) != JV&#95;KIND&#95;NULL</b>
Breakpoint 1 at 0x491de8: file execute.c, line 162.
(gdb) <b>run</b>
Starting program: /github/jq/jq -n \{\"k\":\"v\"\}
Breakpoint 1, stack&#95;push (jq=0x9b2c80, val=jv: {"k":"v"}) at execute.c:162
162	  jq-&gt;stk&#95;top = stack&#95;push&#95;block(&jq-&gt;stk, jq-&gt;stk&#95;top, sizeof(jv));
(gdb) <b>print val</b>
$1 = jv: {"k":"v"}
(gdb) <b>print/r val</b>
$3 = {kind&#95;flags = 7 '\a', pad&#95; = 0 '\000', offset = 0, size = 8, u = {ptr = 0x9b4a90, number = 5.0281890807548674e-317}}
(gdb) <b>print jv&#95;array&#95;set(jv&#95;array(), 10, jv&#95;string("hi"))</b>
$3 = jv: [null,null,null,null,null,null,null,null,null,null,"hi"]
(gdb) <b>quit</b>
</pre>

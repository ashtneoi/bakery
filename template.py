import os
from os import path


class Constant(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


MISSING = Constant("MISSING")
INTERNAL = Constant("INTERNAL")


def wrap(s, ctx):
    i = s.find(":")
    if i == -1:
        raise Exception("`wrap` section must contain a `:`")
    outer_path = path.join(ctx[INTERNAL]["tmpl_dir"], s[:i])
    ctx = ctx.copy()
    ctx["in"] = render(s[i+1 : ], ctx)
    return render_path(outer_path, ctx)


def let(s, ctx):
    i = s.find(":")
    if i == -1:
        raise Exception("`let` section must contain a `:`")
    key = s[:i]
    val = s[i+1 : ]
    ctx[key] = val
    return ""


def default_ctx(extra_ctx={}):
    ctx = {
        "wrap": wrap,
        "let": let,
    }
    ctx.update(extra_ctx)
    return ctx


def find_tag(tmpl, i):
    t1 = tmpl.find("{{", i)
    if t1 == -1:
        return
    t2 = tmpl.find("}}", t1) + 2
    if t2 == -1 + 2:
        raise Exception("Unterminated tag")
    return t1, t2


def substitute(x, subs):
    if len(subs) == 0:
        return x
    i = 0
    n = 0
    ss = []
    while True:
        i1, i2, s = subs[n]
        ss.append(x[i:i1])
        ss.append(s)
        i = i2
        for n in range(n + 1, len(subs)):
            if subs[n][0] >= i:
                break
        else:
            break
    ss.append(x[i:])
    return "".join(ss)


def render(tmpl, ctx={}):
    ctx = default_ctx(ctx)
    ctx.setdefault(INTERNAL, {}).setdefault("tmpl_dir", os.getcwd())

    i = 0
    subs = []  # list of (i1, i2, s)
    sections = []  # stack of (sub_idx, tag)

    while True:
        f = find_tag(tmpl, i)
        if f is None:
            break
        t1, t2 = f
        tag = tmpl[t1+2 : t2-2]
        if tag[0] == "#":
            tag = tag[1:]
            subs.append((t1, t2, None))
            sections.append((len(subs) - 1, tag))
        elif tag[0] == "/":
            tag = tag[1:]
            sub_idx, top_tag = sections.pop()
            if top_tag != tag:
                raise Exception("Mis-nested section tags")
            i1, s1, _ = subs[sub_idx]
            v = ctx[tag]
            inside = tmpl[s1:t1]
            if hasattr(v, "__iter__") and not isinstance(v, str):
                ss = []
                for c in v:
                    section_ctx = ctx.copy()
                    section_ctx.update(c)
                    ss.append(render(inside, section_ctx))
                s = "".join(ss)
            elif hasattr(v, "__call__"):
                s = v(inside, ctx)
            elif isinstance(v, str) or v is True:
                s = render(inside, ctx)
            elif v is False:
                s = ""
            else:
                raise Exception("Invalid type")
            subs[sub_idx] = (i1, t2, s)
        elif tag[-1] == "?":
            tag = tag[:-1]
            v = ctx.get(tag, MISSING)
            if v is MISSING:
                v = ""
            subs.append((t1, t2, v))
        else:
            subs.append((t1, t2, str(ctx[tag])))
        i = t2

    if sections:
        raise Exception("Unterminated section \"{}\"".format(sections[-1][1]))

    return substitute(tmpl, subs)


def render_path(tmpl_path, ctx={}):
    ctx = default_ctx(ctx)
    ctx.setdefault(INTERNAL, {})["tmpl_dir"] = path.dirname(tmpl_path)

    with open(tmpl_path, "r") as f:
        return render(f.read(),  ctx)

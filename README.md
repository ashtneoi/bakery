# README

## What is it?

It's a tiny template engine for Python 2 and 3. The implementation is
single-module, cross-platform (I think), and dependency-free, and the language
is small enough to learn in a few minutes. That may or may not be a good thing,
but it works for me so maybe it'll work for you.

## Is it stable?

Almost.

## Files

`bakery.py` is the template engine. The other files are for demonstration or
testing.

## API

The API consists of two functions, `render` and `render_path`.

`render(tmpl, ctx={})` renders the template string `tmpl` in the context `ctx`
(plus the default `wrap` and `let` block functions unless `ctx` overrides
them). It returns the rendered string.

`render_path(tmpl_path, ctx={})` simply reads the file named `tmpl_path` and renders
it, returning the rendered string.

## Template language

Character encoding is environment-dependent. On Linux with CPython, it's UTF-8.
Not sure about other environments yet (especially Windows).

A template contains plain text and directives. Directives are enclosed in
double curly braces ("`{{}}`") and are evaluated when the template is rendered.
There are four kinds of directives:

`{{name}}` is a variable reference. `name` (which can't contain `?`, `#`, or
`/`) is looked up in the context and its value is substituted directly, with no
further processing (even if the value contains directives itself). If the
context doesn't contain `name`, an error is raised.

`{{?name}}` is an optional variable reference. It renders the same as a
normal variable reference except that if `name` is missing from the context, it
renders to the empty string.

A block is enclosed in matching `{{#name}}` and `{{/name}}` directives. If
`name` refers to True or a nonempty string, the block body is rendered by
itself. If `name` is False or the empty string, the entire block renders to the
empty string. If `name` refers to an iterable of dicts, then for each dict,
the block body is rendered with that dict added to the context. Finally, if
`name` refers to a function, the function is called with two arguments: the
block body (as an unevaluated string) and the current context (which may not be
the same as the original context). If the value is of any other type or isn't
in the context, an error is raised.

## Provided blocks

Two blocks are provided by default. You can write your own if you want.

The `let` block assigns a value to a name in the current context. The syntax is
`{{#let}}name:value{{/let}}`. The value can contain newlines.

The `wrap` block is used to render another template. The syntax is
`{{#wrap}}filename:inside{{/wrap}}`. If the current template is a file,
`filename` is relative to the current template's containing directory. If the
current template is a string (it was invoked via `render(...)`), `filename` is
relative to the current directory.  The block's contents are rendered in the
current context with the `in` variable equal to `inside`.

## Implementation details

Rendering is done in two passes. On the first pass, the template is scanned for
directives, which are immediately rendered into strings (recursing if
necessary) and stored. On the second pass, the chunks of plain text and
rendered directives are joined together into a single string and returned.

## Current limitations

Error messages are reasonably descriptive, but they don't say where the error
occurred, which makes them difficult to debug in a large template. The renderer
should keep track of line and column numbers so it can report better errors.

Terms in the documentation don't quite match those in the implementation, and
there are a few other accuracy issues.

The current implementation is probably slow, since templates aren't
preparsed or cached in any way.

`render` and `render_path` return the entire rendered string at once, which
might be inconvenient if it's very large and not much memory is available.
Returning an iterator might help in that case, but I don't know if that's a use
case worth supporting.

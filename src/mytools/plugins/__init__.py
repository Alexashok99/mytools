"""Package for MyTools plugins.

This directory is intentionally empty by default.  Actual tools are loaded
via entry points declared in `pyproject.toml` under the
`mytools.plugins` group.  You can use this package for:

* Local development: drop a new tool module here and add an entry point
to `pyproject.toml` for quick testing.
* Including simple example plugins shipped with the package.

Having a real package prevents import errors if someone tries to import
`mytools.plugins` directly.  It does not affect plugin discovery; the CLI
continues using ``importlib.metadata.entry_points``.
"""

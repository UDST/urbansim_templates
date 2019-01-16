## Documentation

Documentation is generated using [Sphinx](http://sphinx-doc.org) and hosted with Github Pages at http://udst.github.io/urbansim_templates. 

We have multiple copies of the documentation, for developer releases and production releases. For example, `/docs/_source_latest/` has documentation source files for the most recent developer release, and `/docs/_source_stable/` has source files for the most recent production release. 

Sphinx reads from the source files, plus the docstrings in the code, and renders html files to `/docs/latest/` and `/docs/stable/`. The Github Pages settings are [online](https://github.com/UDST/urbansim_templates/settings). 

For now we're building the docs manually, which gives us maximum control:

```
sphinx-build -b html source_dir build_dir
```

Building the docs requires the python libraries `sphinx`, `numpydoc`, and `sphinx_rtd_theme`, plus the baseline requirements for `urbansim_templates`. You should rebuild the docs for each release. Rendered files won't appear online until they're merged into the master branch, but you can preview them locally. 

When you build the docs, docstrings are drawn from whatever version of the library is loaded by `import urbansim_templates`, not necessarily the copy that you're building the docs within -- so watch out for this when updating older versions.

See more discussion of docs in [PR #81](https://github.com/UDST/urbansim_templates/pull/81) and [Issue #83](https://github.com/UDST/urbansim_templates/issues/83)
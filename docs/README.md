This folder generates the UrbanSim Templates online documentation, hosted at https://udst.github.io/urbansim_templates/.

### How it works

HTML files are generated using [Sphinx](http://sphinx-doc.org) and hosted with GitHub Pages from the `gh-pages` branch of the repository. The online documentation is rendered and updated **manually**. 

### Editing the documentation

The files in `docs/source`, along with docstrings in the source code, determine what appears in the rendered documentation. Here's a [good tutorial](https://pythonhosted.org/an_example_pypi_project/sphinx.html) for Sphinx.

### Previewing changes locally

Install the copy of UrbanSim Templates that the documentation is meant to reflect. Install the documentation tools.

```
pip install ".[docs]"
```

Build the documentation. Warnings are treated as errors, matching the check that runs in CI.

```
sphinx-build -E -W --keep-going -b html docs/source docs/build/html
```

The HTML files will show up in `docs/build/html/`. 

### Uploading changes

Clone a second copy of the repository and check out the `gh-pages` branch. Copy over the updated HTML files, commit them, and push the changes to GitHub.

### Discussion

There are various discussions about documentation in the issue threads. [Issue #120](https://github.com/UDST/urbansim_templates/issues/120) is a good starting point.

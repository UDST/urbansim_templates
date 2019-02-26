Thanks for using UrbanSim Templates! 

This is an open source project that's part of the Urban Data Science Toolkit. Development and maintenance is a collaboration between UrbanSim Inc and U.C. Berkeley's Urban Analytics Lab. 

You can contact Sam Maurer, the lead developer, at `maurer@urbansim.com`.


## If you have a problem:

- Take a look at the [open issues](https://github.com/UDST/urbansim_templates/issues) and [closed issues](https://github.com/UDST/urbansim_templates/issues?q=is%3Aissue+is%3Aclosed) to see if there's already a related discussion

- Open a new issue describing the problem -- if possible, include any error messages, the operating system and version of python you're using, and versions of any libraries that may be relevant


## Feature proposals:

- Take a look at the [open issues](https://github.com/UDST/urbansim_templates/issues) and [closed issues](https://github.com/UDST/urbansim_templates/issues?q=is%3Aissue+is%3Aclosed) to see if there's already a related discussion

- Post your proposal as a new issue, so we can discuss it (some proposals may not be a good fit for the project)


## Contributing code:

- Create a new branch of `UDST/urbansim_templates`, or fork the repository to your own account

- Make your changes, following the existing styles for code and inline documentation

- Add [tests](https://github.com/UDST/urbansim_templates/tree/master/tests) if possible!

- Open a pull request to the `UDST/urbansim_templates` master branch, including a writeup of your changes -- take a look at some of the closed PR's for examples

- Current maintainers will review the code, suggest changes, and hopefully merge it!


## Updating the version number:

- Each pull request that changes substantive code should increment the development version number, e.g. from `0.2.dev7` to `0.2.dev8`, so that users know exactly which version they're running

- It works best to do this just before merging (in case other PR's are merged first, and so you know the release date for the changelog and documentation)

- There are three places where the version number needs to be changed: 
  - `setup.py`
  - `urbansim_templates/__init__.py`
  - `docs/source/index.rst`

- Please also add a section to `CHANGELOG.md` describing the changes!


## Updating the documentation: 

- See instructions in `docs/README.md`


## Preparing a production release:

- Make a new branch for release prep

- Update the version number and `CHANGELOG.md`

- Make sure all the tests are passing, and check if updates are needed to `README.md` or to the documentation

- Open a pull request to the master branch to finalize it

- After merging, tag the release on Github and follow the distribution procedures below


## Patching an earlier release:

- We're not maintaining separate code branches for dev/ production/ major releases, but you can easily recreate them from tags if you need to patch an earlier release

- In Github, create a new branch from the tag for the version you'd like to patch, calling it something like `v1-production`

- Create a second branch from that one, called something like `v1-patch`

- Make your changes in the `v1-patch` branch, and open a PR to `v1-production` to finalize it

- After merging, tag the release on Github and follow the normal distribution procedures

- After the new release is tagged, you can delete the extra branches -- a branch is just a tag pointing to the latest commit in a chain, and the commits will still be there


## Distributing a release on PyPI (for pip installation):

- Register an account at https://pypi.org, ask one of the current maintainers to add you to the project, and `pip install twine`

- Check out the copy of the code you'd like to release

- Run `python setup.py sdist bdist_wheel --universal`

- This should create a `dist` directory containing two package files -- delete any old ones before the next step

- Run `twine upload dist/*` -- this will prompt you for your pypi.org credentials

- Check https://pypi.org/project/urbansim-templates/ for the new version


## Distributing a release on Conda Forge (for conda installation):

- Make a fork of the [conda-forge/urbansim_templates-feedstock](https://github.com/conda-forge/urbansim_templates-feedstock) repository -- there may already be a fork in udst

- Edit `recipe/meta.yaml`: 
  - update the version number
  - paste a new hash matching the tar.gz file that was uploaded to pypi (it's available on the pypi.org project page)

- Check that the run requirements still match `requirements.txt`

- Open a pull request to the `conda-forge/urbansim_templates-feedstock` master branch

- Automated tests will run, and after they pass one of the current project maintainers will be able to merge the PR -- you can add your Github user name to the maintainers list in `meta.yaml` for the next update

- Check https://anaconda.org/conda-forge/urbansim-templates for the new version (may take a few minutes for it to appear)

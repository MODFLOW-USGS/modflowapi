# Developing `modflowapi`

This document explains how to set up a development environment, run the tests, and cut a release.
Conventions used in the project are noted along the way.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Requirements](#requirements)
- [Installation](#installation)
- [Linting](#linting)
- [Testing](#testing)
  - [MODFLOW executables and example models](#modflow-executables-and-example-models)
  - [Running the tests](#running-the-tests)
- [Releasing](#releasing)
  - [1. Start the release](#1-start-the-release)
  - [2. Review and approve](#2-review-and-approve)
  - [3. Automatic steps](#3-automatic-steps)
  - [4. conda-forge](#4-conda-forge)
  - [Changelog conventions](#changelog-conventions)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Requirements

Python 3.11+. Like the other MODFLOW Python projects, `modflowapi` aims to support recent Python
versions, loosely following [SPEC 0](https://scientific-python.org/specs/spec-0000/#support-window).

## Installation

Fork and clone the repository, then install the project in editable mode with the development
dependencies:

```shell
pip install -e . --group dev
```

Developers who use `uv` can sync the project instead:

```shell
uv sync --all-extras
```

The `dev` group includes the `test` and `lint` groups.

## Linting

Linting and formatting use [`ruff`](https://docs.astral.sh/ruff/), and spelling is checked with
[`codespell`](https://github.com/codespell-project/codespell):

```shell
ruff check .
ruff format .
codespell
```

These are also run in CI and must pass.

## Testing

The tests use [`pytest`](https://docs.pytest.org/) with
[`pytest-xdist`](https://pytest-xdist.readthedocs.io/) and fixtures from
[`modflow-devtools`](https://github.com/MODFLOW-ORG/modflow-devtools). They live in `autotest/` and
are run from that directory.

### MODFLOW executables and example models

The tests need the MODFLOW 6 executables, including the `libmf6` shared library, either on the
`PATH` or installed into `autotest/`. They also need the MODFLOW 6 example models. Both can be
fetched with the `mf` command that ships with `modflow-devtools`:

```shell
mf programs install libmf6 --bindir autotest
mf sync
```

FloPy's [`get-modflow`](https://github.com/modflowpy/flopy) utility is an alternative way to install
the executables. See [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for exactly what CI
installs, including the nightly build used for the example-model tests.

### Running the tests

From `autotest/`, run in parallel with verbose output:

```shell
pytest -v -n auto
```

Two markers select subsets of the suite (see [`autotest/pytest.ini`](autotest/pytest.ini)):

- `mf6`: tests that run the MODFLOW 6 example models
- `extensions`: tests for the `modflowapi` extensions

For instance, to skip the example-model tests: `pytest -v -n auto -m "not mf6"`.

## Releasing

Releases are automated by [`.github/workflows/release.yml`](.github/workflows/release.yml).
Publishing to PyPI uses [trusted publishing](https://docs.pypi.org/trusted-publishers/), so no
API token is needed, but the repository must have a `release` environment configured.

> [!IMPORTANT]
> PyPI matches a trusted publisher on the organisation name, the repository name, the workflow
> filename and the environment name. Renaming any of them silently invalidates the publisher, and
> nothing reports it until the next release fails with `invalid-publisher`. This happened when the
> organisation was renamed from `MODFLOW-USGS` to `MODFLOW-ORG`, and went unnoticed for the
> eighteen months until the next release. After any such rename, update the publisher at
> https://pypi.org/manage/project/modflowapi/settings/publishing/ to match.

### 1. Start the release

From the [Actions tab](https://github.com/MODFLOW-ORG/modflowapi/actions/workflows/release.yml),
select **Run workflow** and fill in the form:

| Input | Description |
|:--|:--|
| `branch` | Branch to release from. Defaults to `develop`. |
| `version` | Explicit version number, e.g. `0.3.0`. Defaults to the version in `version.txt` with its `.dev` suffix removed. |
| `run_tests` | Run the test suite before drafting the release. Defaults to true. |

This can also be done from the command line, for instance:

```shell
gh workflow run release.yml -f branch=develop
```

The release version is normally the development version already set in `version.txt` (e.g.
`1.2.0.dev0` releases as `1.2.0`); pass `version` only to release something else. The workflow
creates a `v<version>` release branch, updates the version number, regenerates the changelog with
[git-cliff](https://git-cliff.org/), runs the tests, and opens a draft pull request into `main`.

A release can alternatively be started by pushing a release branch named `v<major>.<minor>.<patch>`.

### 2. Review and approve

Review the release pull request, in particular `HISTORY.md`. Mark it ready for review and merge it
into `main`. Merge rather than squash, to preserve the commit history.

### 3. Automatic steps

Merging the release pull request into `main` triggers jobs that:

1. tag the release and create a GitHub release, with notes taken from `HISTORY.md`
2. build the package and publish it to [PyPI](https://pypi.org/project/modflowapi)
3. open a follow-up pull request resetting `develop` from `main`, with the version number
   incremented to the next development version

Merge the reset pull request to finish the release.

### 4. conda-forge

A few hours after the upload to PyPI, a bot opens a version pull request on the
[feedstock](https://github.com/conda-forge/modflowapi-feedstock). To start it immediately instead,
open an issue there titled `@conda-forge-admin, please update version`.

> [!IMPORTANT]
> The bot updates the version number and the checksum, and nothing else. **Check the recipe's
> `host` and `run` requirements against the dependencies the release actually declares**, which are
> the `Requires-Dist` lines of the sdist on PyPI. Both releases so far needed this by hand: 1.0.0
> because the build backend had moved from setuptools to hatchling, and 1.0.1 because the pandas
> lower bound had been raised. A maintainer can push the correction to the bot's branch.

Merging the feedstock pull request builds and uploads the package. It does not appear to a solver
until the channel index is regenerated, which takes up to about an hour; the package is visible on
anaconda.org before then.

### Changelog conventions

Release notes are generated from commit messages, so commits merged to `develop` must follow the
[conventional commits](https://www.conventionalcommits.org/) format (`feat:`, `fix:`, `refactor:`,
etc.). Commits that do not follow the convention are omitted from the changelog without warning.
See [`cliff.toml`](cliff.toml) for the commit groups and which ones are skipped.

Pull requests are squash merged, so the title becomes the commit message the notes are generated
from. [`.github/workflows/pull_request.yml`](.github/workflows/pull_request.yml) rejects a title
that is not a conventional commit header, but it cannot tell whether the type is the right one: a
user facing change titled `chore:` still passes the check and is still dropped from the notes.

Read the generated changelog on the release pull request before merging it. Anything missing is
added there, into the section for the version being cut, not to `develop`; the section does not
exist until the release workflow generates it.

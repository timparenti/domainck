# domainck

Domain WHOIS checker, built to partially replace the Domain Monitor product
from DomainTools, which retired on 2024-09-30.

## Requirements

* Python >= 3.11
* `python3-venv` (for `pip` and `ensurepip`)

## Setting up environments

This project uses `pyproject.toml` to establish dependencies for its build
environment.  The overall build process is described in general terms
[here](https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/).

### Build environment

Clone the repo and create a Python `venv` for the build environment:
```
git clone git@github.com:timparenti/domainck.git
cd ~/domainck
python3 -m venv .venv/ --prompt domainck-build
```

Install `pip` dependencies to the build environment:
```
source .venv/bin/activate
pip install --upgrade pip
pip install build
```

Install the package and its development dependencies
to the build environment in "editable" mode:
```
pip install -e ".[dev]"
```

Basic static type-checking can be done by running `mypy`
from the project root within the activated `venv`.

### Test and production environments

Create a user, `domainck`, which will run domainck in production, and establish
a Python `venv` for each environment in which it will run, e.g.:
```
sudo adduser --disabled-password domainck
sudo -s
python3 -m venv /opt/domainck-test/ --prompt domainck-test
python3 -m venv /opt/domainck-prod/ --prompt domainck-prod
chown -R domainck:domainck /opt/domainck-test/
chown -R domainck:domainck /opt/domainck-prod/
```

Then `su` as the new user and install `pip` dependencies to each environment
`$ENV`:
```
sudo su domainck
source /opt/$ENV/bin/activate
pip install --upgrade pip
pip install build
```

## Deployment

### Build environment

If not already active, activate the build environment:
```
cd ~/domainck
source .venv/bin/activate
```

Reinstall the updated package and its development dependencies
to the build environment in "editable" mode:
```
pip install -e ".[dev]"
```

### Test and production environments

From the build directory and environment, build a wheel:
```
cd ~/domainck
source .venv/bin/activate
# Bump the project version and update any other dependencies
edit pyproject.toml
python3 -m build --wheel
```
This creates a wheel in the `dist` subdirectory.  If needed, copy it to the
target environment's host.

Using the target environment's `pip`, install the application from the latest
wheel created in the build environment's `dist` subdirectory, e.g.:
```
sudo /opt/$ENV/bin/pip install ~/domainck/dist/domainck-x.y.z-py3-none-any.whl
```
where `x.y.z` is the project version.

## Usage

### Running from build

If not already active, activate the build environment:
```
cd ~/domainck
source .venv/bin/activate
```

Run `python3 -m domainck` with the desired options.
See `python3 -m domainck --help` for options.

### Running from test or production

Using the target environment's `python3`, run the application with the desired
options, e.g.:
```
sudo su domainck
cd /opt/$ENV
./bin/python3 -m domainck [options]
```

For production `cron`, this is generally best invoked under the `domainck` user as:
```
cd /opt/domainck-prod && ./bin/python3 -m domainck [options]
```
or, equivalently, if an unscheduled production run is required:
```
sudo su domainck -c "cd /opt/domainck-prod && ./bin/python3 -m domainck [options]"
```

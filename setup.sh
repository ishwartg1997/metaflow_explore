#!/bin/bash

# Preliminary shell script setup:  Terminate script execution on errors.
set -e

default_python_version=3.8.2

while getopts ":pd:" opt; do
  case ${opt} in
    p )
      python_version=${OPTARG}
      echo "Overriding python version to ${python_version}"
      ;;
    d )
      virtualenv_dir=${OPTARG}
      echo "setting up virtual environment in ${virtualenv_dir}"
      ;;
    \? )
      echo "Usage: setup.sh [-p <python version>] [-d <directory/module>]"
      echo "       The -p parameter will override the default python environment value."
      echo "       The -d Parameter will override the default directory behavior and create a virtual environment in specified directory"
      echo "       -p [optional] is the python version to use if no python version is found"
      echo "       -d [optional] is the directory to create the virutal environment in"
      exit 1
      ;;
  esac
done

if [[ -z "${virtualenv_dir}" ]]; then
  virtualenv_dir="$(pwd)"
  base_dir=""
  pushd . >/dev/null 2>&1
else
  base_dir="${virtualenv_dir}/"
  pushd ${virtualenv_dir} >/dev/null 2>&1 \
    || (echo >&2 "Cannot pushd into ${virtualenv_dir}, does it exist?" && exit 1)
fi

basename=$(basename $(pwd))

if [[ -z "${python_version}" ]]; then
  if [[ -s ".default-python-version" ]]; then
    python_version=$(cat ".default-python-version")
    echo "Using cookiecutter python version: ${python_version}"
    echo "To change this version, modify ${base_dir}.default-python-version"
  else
    python_version="${default_python_version}"
    echo "No python version file found and version not specified, defaulting: ${python_version}"
  fi
fi

# Prerequisite:  Make sure that we have pyenv installed.  If not, then exit.
echo "Ensuring that pyenv is installed..."
command -v pyenv >/dev/null 2>&1 || {
    echo >&2 "Error:  pyenv does not appear to be installed."
    echo >&2 "        Please follow the installation instructions here before running this script:"
    echo >&2 "        https://github.com/pyenv/pyenv#installation"
    exit 1
}
echo "Done."

# Use pyenv to install the prescribed version of Python.
echo "Using pyenv to install the prescribed version of Python ($python_version)..."
pyenv install $python_version --skip-existing >/dev/null 2>&1 || {
    echo >&2 "Error:  Unable to install Python version $python_version using pyenv.";
    echo >&2 "        Try updating pyenv by running:     ";
    echo >&2 "                                           ";
    echo >&2 "        brew update && brew upgrade pyenv"
    exit 1
}
echo "Done."

pyenv local $python_version

# Create a virtual environment for this project.
virtualenv_name=venv-${basename}

echo "Creating a virtual environment for this project called $virtualenv_name..."
mkdir -p .$virtualenv_name/
python -m venv .$virtualenv_name
# If we dont have a default python version when creating the environment, this is it.
if ! [[ -s ".default-python-version" ]]; then
  echo "Setting default python version: ${python_version} in .default-python-version"
  echo "$python_version" > .default-python-version
fi
echo "Done."

# Activate the virtual environment
echo "Activating the virtual environment..."
source .$virtualenv_name/bin/activate
echo "Done."

echo "Upgrading pip..."
pip install --upgrade pip
echo "Done."

echo "Installing requirements.txt..."
pip install -U -r requirements.txt
echo "Done."

popd >/dev/null 2>&1 \
    || (echo >&2 "Cannot popd was the previous directory removed?" && exit 1)

echo "
Setup succeeded!
  - Now run 'source ${base_dir}.$virtualenv_name/bin/activate' in the shell to activate the
    virtual environment.
  - Run 'deactivate' to exit the virtual environment."


## Contributing

If you have discovered a bug or have a feature suggestion, feel free to create an issue on GitHub.

If you'd like to make some changes yourself, see the following:
1. [Fork](https://help.github.com/articles/fork-a-repo/) this repository to your own GitHub account and then [clone](https://help.github.com/articles/cloning-a-repository/) it to your local device
2. Make sure to have pipenv installed locally.
3. Run `pipenv install` to install local packages.
4. Follow instructions below for various procedures.
5. Finally, submit a [pull request](https://help.github.com/articles/creating-a-pull-request-from-a-fork/) with your changes!

### Install locally
1. Make sure to [install pipenv](https://pipenv-fork.readthedocs.io/en/latest/)
2. Run `pipenv install`

### Running locally
1. Get kubernetes and AWS credentials.
2. Run `./run_local.sh`
3. Run `curl -I locahost:8080/run` in another window to run the secret manager.

### Running the tests
1. Run `pipenv run python -m unittest discover` to run all tests. Files must be `test*.py`

### Running Linter
1. Install [flake8](https://flake8.pycqa.org/en/latest/)
2. Run `flake8 ./app` to run the linter. (Can autocorrect most errors with `autopep8 --in-place --aggressive --aggressive -r <path>`)

### Upgrade Packages
1. Run `pipenv install <package>==<version>`


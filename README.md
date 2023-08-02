# Important Notes
## Migrations
Some migrations require multiple steps. They are documented in the `migrations/README.md`

# Local dev setup
## install postgres server &gt;= 10
1. create 2 x pyenv 
```
pyenv virtualenv 3.9.2 qairon-3.9.2
pyenv virtualenv 3.9.2 qairon-dev-3.9.2
```
## install pip modules in each
while installing modules you may get an error saying it can't find the postgres dev libraries, something about pkg_config.
the postgres dev libraries may be in a proprietary directory, google is your friend
```
pyenv activate qairon-3.9.2
pip install -r requirements.txt
pyenv deactivate
pyenv activate qairon-dev-3.9.2
pip install -r dev_requirements.txt
```

## Running
### SQL Alchemy config
for any invocation, cli or through IDE, running the server or db migrations, there need to be environment variables set to configure the db
`export SQLALCHEMY_DATABASE_URI=postgresql://<user>:<password>@localhost:5432/qairon`


default for local development
`export SQLALCHEMY_DATABASE_URI=postgresql://qairon:qairon@localhost:5432/qairon`


### running the server
`flask app`


### initial db setup
create the role w/password and db in postgres first that matches your sqlalchemy config
`flask db upgrade`


# Build and Publish
python setup.py clean build sdist upload -r local

```
#~/.pypirc

[distutils]
index-servers = local

[local]
repository: <appropriate URL here>
username: <redacted>
password: <redacted>
```

# End User Instructions

1. start VPN your dev vpn
1. pyenv activate &lt;appropriate pyenv virtualenv here&gt;
1. export QAIRON_ENDPOINT=&lt;appropriate URL here&gt;
1. Enjoy!

# QCLI
## Standalone Running & Debugging

* Make sure to never have the package `qairon-qcli` installed in your runtime or else things will succeed that should
fail.
* There is both a bash shim `./qcli` and the actual script that gets packaged `./qairon_cli/qcli.py` that can be executed.
* This bash shim is not packaged, it is a quick and dirty wrapper there for your convenience to be able to run the same
command, `qcli`, that you would normally run, as opposed to `qcli.py`


## Use as a module
* once the `qairon-qcli` package is installed, you may 
```
from qairon_cli.qcli import CLIController as qcli
```

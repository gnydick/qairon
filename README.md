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

```
./qcli ....
```

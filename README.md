1. activate toolbelt ops/aws/126../../us-west-2/infra0
2. aws sso login
3. kubectl port-forward service/qairon 5001
4. export QAIRON_ENDPOINT=http://localhost:5001
5. Enjoy!

./qcli ....

[comment]: <> (pip build)
python setup.py clean build sdist upload -r local

``

# Local dev setup
## install postgres server >= 10
create 2 x pyenv 
<pre>
pyenv virtualenv 3.9.2 qairon-3.9.2
pyenv virtualenv 3.9.2 qairon-dev-3.9.2
</pre>
## install pip modules in each
while installing modules you may get an error saying it can't find the postgres dev libraries, something about pkg_config. 
the postgres dev libraries may be in a proprietary directory, google is your friend
<pre>
pyenv activate qairon-3.9.2
pip install -r requirements.txt
pyenv deactivate
pyenv activate qairon-dev-3.9.2
pip install -r dev_requirements.txt
</pre>

# Running
## SQL Alchemy config
for any invocation, cli or through IDE, running the server or db migrations, there need to be environment variables set to configure the db
<pre>export SQLALCHEMY_DATABASE_URI=postgresql://&lt;user&gt;:&lt;password&gt;@localhost:5432/qairon</pre>

default for local development
<pre>export SQLALCHEMY_DATABASE_URI=postgresql://qairon:qairon@localhost:5432/qairon</pre>

## running the server
<pre>flask app</pre>

## initial db setup
create the role w/password and db in postgres first that matches your sqlalchemy config
<pre>flask db upgrade</pre>
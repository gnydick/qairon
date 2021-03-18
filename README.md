# Languages
## Python - 3.8.8
3.9.x has some incompatibilities with our code

### pyenv - latest
**Installation**

```curl https://pyenv.run | bash```

**pyenv-virtualenv plugin - latest**

```
git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv
```

**Update .bashrc**
```
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```
---
### Using
```
pyenv install 3.8.8
```
Create a new ***venv*** and ***requirements.txt*** for each module
```
pyenv virtualenv 3.8.8 <module>-3.8.8
echo <module>-3.8.8 > <module_base_dir>/.python-version
```


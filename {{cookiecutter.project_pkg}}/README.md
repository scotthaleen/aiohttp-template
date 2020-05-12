

# Getting Started

Setup a python 3.8+ virtual env

- https://github.com/pyenv/pyenv <br>
- https://github.com/pyenv/pyenv-virtualenv <br>


Install Dev Requirements

```
python -m pip install -r requirements-dev.txt
```



## Tox

Reformat Code (runs isort, black)

```
tox -e format
```


Test + Lint

```
tox
```


Package
```
tox -e package
```


## Docker

```
./build-docker.sh
```


## Docker Compose

```
docker-compose up -d --build



docker-compose stop
```



## Dev

```
python -m pip install -e .

{{ cookiecutter.project_script }}--config=app.dev.yaml --logging=logging.dev.yaml
```

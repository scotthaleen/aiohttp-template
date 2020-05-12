#!/usr/bin/env sh


DT=$(date +"%Y%m%d")
GIT=${DT}.git.$(git rev-parse --short HEAD)
VERSION="0.1"
IMAGE={{cookiecutter.dockerhub_user}}/{{cookiecutter.project_pkg}}

docker build -t "${IMAGE}:dev" -t "${IMAGE}:${VERSION}" -t "${IMAGE}:${GIT}" .

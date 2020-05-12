
FROM python:3.8-alpine

ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8

RUN apk add --no-cache gcc curl musl-dev

EXPOSE 8080

ENV APP_RESOURCES="/opt/{{cookiecutter.project_pkg}}/resources"
RUN mkdir -p /var/log/{{cookiecutter.project_pkg}}/
WORKDIR /opt/{{cookiecutter.project_pkg}}

VOLUME [ "/var/log/{{cookiecutter.project_pkg}}", "/opt/{{cookiecutter.project_pkg}}/resources" ]

COPY . {{cookiecutter.project_pkg}}/
RUN pip3 install {{cookiecutter.project_pkg}}/

COPY entrypoint.sh ./

RUN chmod +x entrypoint.sh

HEALTHCHECK --interval=25s --timeout=5s --retries=10 \
  CMD curl --silent --fail localhost:8080/healthcheck || exit 1

ENTRYPOINT ["/opt/{{cookiecutter.project_pkg}}/entrypoint.sh"]
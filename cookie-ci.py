#! /usr/bin/env python
# -*- coding: utf-8 -*-

from cookiecutter.main import cookiecutter

cookiecutter("../aiohttp-template",
             no_input=True,
             extra_context={"project_pkg": "ciserver"})

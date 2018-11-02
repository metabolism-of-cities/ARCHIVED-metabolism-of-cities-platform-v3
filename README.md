# Overview

This repository contains the source code of [Metabolism of Cities](https://metabolismofcities.org/). This repository supersedes the previous Github-hosted repository of our old website. This new website is written in Python using Django. The following technologies are used:

- Django 2.1
- Python 3
- PostgreSQL 
- Docker

# Getting started

To get started with this project, do the following:

- Clone the repository on your local machine
- Install Docker and specifically [Docker Compose](https://docs.docker.com/compose/)
- Create a number of baseline directories (see below)
- Create a configuration file (see below)
- Build your container

Once this is done, you have completed all the required steps to get the system running. Specific details below:

Let's say you have cloned this repository to /home/user/moc

    $ cd /home/user/moc
    $ mkdir src/{media,logs,static}
    $ cp src/ie/settings.sample.py src/ie/settings.py
    $ docker-compose build

Now that this is done, you can run the container like so:

    $ cd /home/user/moc
    $ docker-compose up

Wait a few moments, and the website should be up and running at http://localhost:8000

# License

MIT License

Copyright (c) 2018 Paul Hoekman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

# Import licensing notes

Some restrictions apply to third-party components. We use High Charts as our charting library. This is free to use for non-profits, but not for commercial ventures. Consult their website for more infromation.

We furthermore use a design template called Nifty. This is a paid design template with its own licensing. If you want to set up your own derivative of this platform then you must purchase your own license or use another template.

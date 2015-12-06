Home of my personal website and resume hosted on digitalocean.com running on Ubuntu LTS 12.04. Visit it at [https://www.justinlanahan.com](https://www.justinlanahan.com)

## Dependencies
##### Applications
- nginx
- gunicorn
- supervisor
- python2.7+
- postgresql
- postgresql-contrib
- libpq
- libpq-dev
- python-dev

##### Python Packages
- django
- psycopg2

## Setup
##### 0. Start fresh
```sh
$ sudo aptitude update
$ sudo aptitude upgrade
```
##### 1. PostgreSQL
```sh
$ sudo aptitude install postgresql postgresql-contrib
$ sudo su - postgres
postgres@ubuntu:~$ createuser --interactive -P
Enter name of role to add: <username>
Enter password for new role: 
Enter it again: 
Shall the new role be a superuser? (y/n) n
Shall the new role be allowed to create databases? (y/n) n
Shall the new role be allowed to create more new roles? (y/n) n
postgres@ubuntu:~$

postgres@ubuntu:~$ createdb --owner <username> <dbname>
postgres@ubuntu:~$ logout
$
```
##### 2. Application User
Don't use root for running django app! create a less privileged user.
```sh
$ sudo groupadd --system webapps
$ sudo useradd --system --gid webapps --shell /bin/bash --home /webapps/<username> <appname>
```
##### 3. Python virtualenv
Always do your work in a virtual environment! Switch to your webapp user and activate the virtual environment. This also places you in a local context with it's own local bin for ease of use.
```sh
$ sudo aptitude install python-virtualenv
$ sudo mkdir -p /webapps/<appname>/
$ sudo chown <username> /webapps/<appname>/
$ sudo su - <username>
username@ubuntu:~$ cd /webapps/<appname>/
username@ubuntu:~$ virtualenv .
username@ubuntu:~$ source bin/activate
(appname)username@ubuntu:~$
```
##### 4. Django setup
All future packages for the project should be installed from within hte virtual environment so that we do not contaminate our normal Python site-packages.
```sh
(appname)username@ubuntu:~$ pip install django
(appname)username@ubuntu:~$ django-admin.py startproject <appname>
```

##### 5. Django test
At this point you can test the basic django app with all default settings and access it at http://example.com:8000
```sh
(appname)username@ubuntu:~$ cd appname
(appname)username@ubuntu:~$ python manage.py runserver example.com:8000
```
##### 6. Configure PostgreSQL with Django
You will need to install `pscycopg2` database adapter in your virtual environment. This also requires compilation of a native C extension and thus needs to find appropriate header files and static libraries for linking with `libpq`.
```sh
$ sudo aptitude install libpq libpq-dev python-dev
(appname)username@ubuntu:~$ pip install psycopg2
```
You can now configure the databases section in your `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dbname',
        'USER': 'username',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```
Finally, build the initial database for Django.
```sh
(appname)username@ubuntu:~$ python manage.py syncdb
```

##### 7. Gunicorn
Django's default web server is single-threaded and meant only for development. Enter Gunicorn!
```sh
(appname)username@ubuntu:~$ pip install gunicorn
```
Test that Gunicorn can run the basic Django application with the following command. You can change the port here to force broser to establish a new connection. Test at http://example.com:8001
```sh
(appname)username@ubuntu:~$ gunicorn username.wsgi:application --bind example.com:8001
```
At this point you can script out Gunicorn with some config options. Copy configs/gunicorn_start into your virtual environnment bin at bin/gunicorn_start. Be sure to make this executable with below command:
```sh
$ sudo chmod u+x bin/gunicorn_start
```
As a rule-of-thumb, set the `--workers` (`NUM_WORKERS`) according to the following formula: `2 * CPUs + 1`. This way, at any given time, half of your workers will be busy doing I/O.

The `--name` (`NAME`) argument specifies how your application will identify itself in programs such as `top` or `ps`. It defaults to `gunicorn`, which might make it harder to distinguish from other webb apps powered by Gunicorn.

In order for the `--name` argument to have an effect you need to install a Python module called `setproctitle`. Again, pip needs access to the `python-dev` C header files.
```sh
(appname)username@ubuntu:~$ pip install setproctitle
```

##### 8. Starting and Monitoring with Supervisor
We need to make sure the bin/gunicorn_start script starts automatically with the system and can be restarted if it exits unexpectedly for some reason. Enter `supervisord`.
```sh
$ sudo aptitude install supervisor
```
Once installed, you can give supervisor programs to start and watch by creating conf files in the `/etc/supervisor/conf.d` directory. Copy `configs/supervisor-thor_app.conf` to `/etc/supervisor/conf.d/appname.conf`.

Now create the file to store your application's log messages:
```sh
username@ubuntu:~$ mkdir -p /webapps/appname/logs/
username@ubuntu:~$ touch /webapps/appname/logs/gunicorn_supervisor.log
```
Finally, restart, update and check status of supervisor with the new configs.
```sh
$ sudo supervisorctl reread
$ sudo supervisorctl update
$ sudo supervisorctl status appname
``` 

##### 9. Nginx
Nginx will act as a reverse proxy for us and serve our application and its statis files.
```sh
$ sudo aptitude install nginx
$ sudo service nginx start
```
You can now navigate to http://example.com and you should see "Welcome to nginx!".

Each Nginx virtual server (webapp) should have its own config file in the `/etc/nginx/sites-available` directory. You then select which sites you want to enable by making symbolic links to thos in the `/etc/nginx/sites-enabled` directory. Copy `configs/nginx-thor_app` to `/etc/nginx/sites-available/appname` then create symbolic link with `$ sudo ln -s /etc/nginc/sites-enabled/appname` then restart Nginx `$ sudo service nginx restart`.

#### Mission Accomplished!

## Running Multiple Web Applications
1. Create seperate virtual environment in `/webapps/` with Django, Gunicorn and any other dependencies.
2. Create seperate system accounts, so one doesn't pwn them all.
3. Create bin/gunicorn_start script
4. Create supervisor config files and start the app
5. Create Nginx virtual servers

## Uninstalling
If you ever need to nuke your web application, follow these steps.

1. `$ sudo rm /etc/nginx/sites-enabled/appname`. Disables virtual server from Nginx.
2. `$ sudo service nginx restart`. Completes the disabling.
3. `$ sudo rm /etc/nginx/sites-available/appname`. Remove base webapp config file from Nginx if you never intend to use it again.
4. `$ sudo supervisorctl stop appname`. Stops Supervisor from monitoring app.
5. `$ sudo rm /etc/supervisor/conf.d/appname.conf`. Removes app from Supervisor's control scripts directory.
6. `$ sudo rm -r /webapps/appname`. Final nuke of all the django files.

## TODO
- Redirect to login when POSTing on events page
- Error when submitting groupby query from admin but not from shell

## Thanks
[Michal Karzynski's Blog](http://michal.karzynski.pl/blog/2013/06/09/django-nginx-gunicorn-virtualenv-supervisor/) - Production Django setup

## License
MIT

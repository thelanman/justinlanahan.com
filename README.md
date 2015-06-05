# [justinlanahan.com](http://www.justinlanahan.com)

Home of my personal website / resume hosted on digitalocean.com

## Dependencies
- nginx
- gunicorn
- python2.7+
- django

## Setup
##### Start fresh
```sh
$ sudo aptitude update
$ sudo aptitude upgrade
```
##### PostgreSQL
```sh
$ sudo aptitude install postgresql postgresql-contrib
$ sudo su - postgres
postgres@django:~$ createuser --interactive -P
Enter name of role to add: <username>
Enter password for new role: 
Enter it again: 
Shall the new role be a superuser? (y/n) n
Shall the new role be allowed to create databases? (y/n) n
Shall the new role be allowed to create more new roles? (y/n) n
postgres@django:~$

postgres@django:~$ createdb --owner <username> <dbname>
postgres@django:~$ logout
$
```
##### Application User
```sh
$ sudo groupadd --system webapps
$ sudo useradd --system --gid webapps --shell /bin/bash --home /webapps/<username> <appname>
```
##### Python virtualenv
```sh
$ sudo aptitude install python-virtualenv
$ sudo mkdir -p /webapps/<appname>/
$ sudo chown <username> /webapps/<appname>/
$ sudo su - <username>
<username>@django:~$ cd /webapps/<appname>/
<username>@django:~$ virtualenv .
<username>@django:~$ source bin/activate
(<appname>)<username>@django:~$
```
##### Django setup
```sh
(<appname>)<username>@django:~$ pip install django
(<appname>)<username>@django:~$ django-admin.py startproject <appname>
```

## Thanks
[Michal Karzynski's Blog](http://michal.karzynski.pl/blog/2013/06/09/django-nginx-gunicorn-virtualenv-supervisor/) - Production Django setup

## License
MIT
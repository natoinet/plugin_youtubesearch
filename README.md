TuCat YouTube Search Plugin
===========================

## Installation guide

### Prerequisites

Tucat must be installed https://github.com/natoinet/tucat

### Optional : When using docker

If using Docker, you must first connect to the Djangoapp docker container :
```
  $ sudo docker exec -it tucat_djangoapp_1 bash
```

### Clone plugin_youtubesearch GitHub repository
```
  $ cd tucat
  $ git clone https://github.com/natoinet/plugin_youtubesearch
```

### Setup the plugin

1. Add your Google API key to .env

* Open the .env file
```
  $ cd ..
  $ vim .env
```

* Add at the end of the .env file
```
  GOOGLE_API_KEY=AddYour_Google_API_Key_Here
```

2. Activate the plugin in LOCAL_APPS in docker.py

* Open docker.py
```
  $ vim config/settings/docker.py
```

* Add tucat.plugin_youtubesearch at the end of LOCAL_APPS in docker.py
```
  LOCAL_APPS = (
    ..
    'tucat.plugin_youtubesearch',
  )
```

3. Migrate the database
```
  $ python manage.py makemigrations plugin_youtubesearch
  $ python manage.py migrate
```

4. Restart the Tucat
```
  $ supervisorctl
  restart all
  exit
```

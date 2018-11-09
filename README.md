TuCat YouTube Search Plugin
===========================

## Installation guide

### Prerequisites

Tucat must be installed https://github.com/natoinet/tucat

### Optional : If using docker

If using Docker, you must first connect to the Django docker container :
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

2. Open docker.py
```
  $ vim config/settings/docker.py
```

3. Add tucat.plugin_youtubesearch at the end of LOCAL_APPS in docker.py
```
  LOCAL_APPS = (
    ..
    'tucat.plugin_youtubesearch',
  )
```

4. Migrate the database
```
  $ python manage.py makemigrations plugin_youtubesearch
  $ python manage.py migrate
```

5. Restart the Tucat
```
  $ supervisorctl
  restart all
  exit
```

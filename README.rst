TuCat YouTube Search Plugin
===========================

## Installation guide
### Prerequisites: Having the Tucat installed

### Clone the plugin repository
  ```
    cd tucat

    # git clone https://github.com/natoinet/plugin_youtubesearch
  ```

### Setup
1. Add your Google API key to .env
  * Open the .env file
    ```
      # cd ..
      # vim .env
    ```
  * Add at the end of the .env file
    ```
      GOOGLE_API_KEY=AddYour_Google_API_Key_Here
    ```

2. Open docker.py
  ```
    vim config/settings/docker.py
  ```

3. Add tucat.plugin_youtubesearch at the end of LOCAL_APPS in docker.py
  ```
    LOCAL_APPS = (
      ..
      'tucat.plugin_youtubesearch',
    )
  ```

4. Migrate
  ```
    # python manage.py makemigrations plugin_youtubesearch
    # python manage.py migrate
  ```

5. Restart the Tucat
  ```
    # supervisorctl
    restart all
    exit
  ```

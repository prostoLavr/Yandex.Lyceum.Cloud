# lava-land.ru

Installing:
* packages:
  * uwsgi 
  * uwsgi-plugin-python3 or uwsgi-plugin-python
* edit uwsgi.ini: <br> if you have uwsgi-plugin-python3 <br>then use "plugins=python3" <br>else use "plugins=python"


Running: 
*     cd /path/to/Yandex.Lyceum.Cloud
*     uwsgi --ini ./uwsgi.ini

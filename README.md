# papelex_winthor
Rotinas Winthor

For testing use:

```
python 9812.py USERNAME DB_PASSWORD DB_ALIAS DB_USER APP_NUMBER
```

To deploy run:

```
pyinstaller -F -w 9812.py -i static\Winthor.ico
```

For documentationon on PyQt, access:
    http://tutorialspoint.com/pyqt


TODO:

[ ] Allow query params on webserver
[ ] Implement execute endpoint on webserver
[ ] Prevent sql injection

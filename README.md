## Trackman
Trackman is a track logger with a UI and an API compatible with WinAmp's POST
plugin, [mpd-automation](https://github.com/wuvt/mpd-automation), and
[johnny-six](https://github.com/wuvt/johnny-six). The included SSE endpoint can
be used by external scripts for live track updates, similar to how it is used
on the WUVT website. It also provides access to previous playlists and can
generate charts of what has been played.

### Deployment
These instructions are for Linux; instructions for other platforms may vary.

First, clone the repo, create an empty config, and build the appropriate Docker
image for your environment. We provide Dockerfile.dev which is configured to
use SQLite and runs Redis directly in the image, and Dockerfile, which is
recommended for production deployments as it does not run any of the required
services inside the container itself.

For Dockerfile.dev:
```
git clone https://github.com/wuvt/trackman.git
cd trackman
echo "SECRET_KEY = \"$(xxd -l 28 -p /dev/urandom)\"" > wuvt/config.py
docker build -t trackman -f Dockerfile.dev .
```

Now run it:
```
docker run --rm -p 9090:8080 trackman:latest
```

You can now access the site at <http://localhost:9090/>. An admin user account
will be created for you; the password is automatically generated and displayed
when you launch the container.

### Non-Docker Deployment
First, install redis. For example, on Debian or Ubuntu:

```
apt-get install redis
```

You'll also want to get uWSGI. You need at least version 2.0.9. For example:

```
apt-get install uwsgi uwsgi-core uwsgi-plugin-python
```

Now, build the SSE offload plugin. For example, on Debian:

```
apt-get install uuid-dev libcap-dev libpcre3-dev
uwsgi --build-plugin https://github.com/wuvt/uwsgi-sse-offload
sudo cp sse_offload_plugin.so /usr/lib/uwsgi/plugins/
```

Make sure the redis daemon is running; on Debian, this will happen
automatically.

It is recommended that you use a virtualenv for this so that you can better
separate dependencies:

```
mkdir -p ~/.local/share/virtualenv
virtualenv ~/.local/share/virtualenv/trackman
source ~/.local/share/virtualenv/trackman/bin/activate
```

Now, within this virtualenv, install the dependencies:

```
pip install -r requirements.txt
```

Next, clone the repo:

```
git clone https://github.com/wuvt/trackman.git
cd trackman
```

Create a blank file, wuvt/config.py; you can override any of the default
configuration options here if you so desire. You'll definitely need to set a
value for `SECRET_KEY`. Next, you will need to render images, create the
database, and add some sample content to the site:

```
export FLASK_APP=$PWD/wuvt/__init__.py
flask initdb && flask sampledata
```

Finally, start uWSGI:

```
uwsgi --ini uwsgi.ini:dev
```

You can now access Trackman at http://localhost:9090/

### API
TODO

Look at submit_tracks.py for an example of sending metadata to Trackman.


### License

The entirety of this software is available under the GNU Affero General Public
License:

```
Copyright 2012-2018 James Schwinabart, Calvin Winkowski, Matt Hazinski.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
```

If you have special requirements, please contact us to inquire about commercial
licensing.

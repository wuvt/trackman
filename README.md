## Trackman
Trackman is a track logger with a UI and an API compatible with WinAmp's POST
plugin, [mpd-automation](https://github.com/wuvt/mpd-automation), and
[johnny-six](https://github.com/wuvt/johnny-six). The included SSE endpoint can
be used by external scripts for live track updates, similar to how it is used
on the WUVT website. It also provides access to previous playlists and can
generate charts of what has been played.

### Deployment
These instructions are for Linux; instructions for other platforms may vary.
You will need recent (as of 2018) versions of Docker and docker-compose.

First, clone the repo, create an empty config, and build the appropriate Docker
image for your environment. We provide Dockerfile.dev which is configured for a
development environment, and Dockerfile, which is recommended for production
deployments.

For Dockerfile.dev:
```
git clone https://github.com/wuvt/trackman.git
cd trackman
echo "SECRET_KEY = \"$(xxd -l 28 -p /dev/urandom)\"" > trackman/config.py
```

Now run it:
```
docker-compose up
```

You can now access the site at <http://localhost:9090/>. An admin user account
will be created for you; the password is automatically generated and displayed
when you launch the container.

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

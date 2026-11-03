# Jupyter Server configuration for the binder image. binder/Dockerfile copies it to
# etc/jupyter/ in the Pixi environment.
#
# setup-work-dir.sh makes ~/work a symlink to /data/<workshop>/<user>, which is
# outside the home directory. With the default root directory (the home directory),
# Jupyter refuses to serve files under the symlink through its /files/ route, which
# JupyterLab uses for images in notebooks and Markdown, downloads, and opening files
# in a new browser tab. Those requests fail with 403 "is not in root static directory".
# Browsing, opening, and saving notebooks through the symlink still work.
#
# Setting the root directory to / puts the target of the symlink inside the root.
# The file browser can then go above the home directory, but only with the user's own
# permissions, which is no more access than a terminal already gives.
#
# Notes:
# - This must be a top-level jupyter_server_config file. Files in
#   jupyter_server_config.d/ are only read to enable server extensions, so a
#   root_dir set there is silently ignored.
# - A root directory set by the hub (e.g. z2jh singleuser.notebookDir) is passed on
#   the command line and overrides this file.
# - The cleaner fix is on the hub: mount each user's /data directory directly at
#   ~/work (a volume mount with a per-user subPath) instead of using a symlink. If
#   that is done, this file can be removed.
import os

c = get_config()  # noqa: F821

c.ServerApp.root_dir = "/"
# Open JupyterLab in the home directory rather than at /
c.ServerApp.preferred_dir = os.path.expanduser("~")

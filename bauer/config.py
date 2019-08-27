import os
import json
import logging
import bauer.constants as con

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# TODO: Why are changes not recognized?
class ConfigManager:

    _cfg_file = con.FILE_CFG
    _cfg = dict()

    ignore = False  # TODO: Still needed?

    def __init__(self, config_file):
        self._cfg_file = config_file
        #self._watch_changes()

    """
    def _watch_changes(self):
        # Watch for config file changes in realtime
        observer = Observer()
        change_handler = ChangeHandler(self._cfg_file, self._read_cfg)
        observer.schedule(change_handler, ".", recursive=True)
        observer.start()
    """

    def _read_cfg(self):
        if os.path.isfile(self._cfg_file):
            with open(self._cfg_file) as config_file:
                self._cfg = json.load(config_file)

    def _write_cfg(self):
        if not os.path.exists(os.path.dirname(self._cfg_file)):
            os.makedirs(os.path.dirname(self._cfg_file))

        with open(self._cfg_file, "w") as config_file:
            json.dump(self._cfg, config_file, indent=4)

    def get(self, *keys):
        if not self._cfg:
            self._read_cfg()

        value = self._cfg
        for key in keys:
            try:
                value = value[key]
            except KeyError as e:
                err = f"Couldn't read '{key}' from {self._cfg_file}"
                logging.debug(f"{repr(e)} - {err}")
                return None

        return value if value is not None else None

    # TODO: Add try / except
    def set(self, value, *keys):
        if not self._cfg:
            self._read_cfg()

        tmp_cfg = self._cfg

        for key in keys[:-1]:
            tmp_cfg = tmp_cfg.setdefault(key, {})

        tmp_cfg[keys[-1]] = value

        self.ignore = True  # TODO: Still needed?
        self._write_cfg()

    def remove(self, keys):
        if not self._cfg:
            self._read_cfg()

        try:
            del self._cfg[keys[0]][keys[1]]
            self._write_cfg()
        except KeyError as e:
            err = f"Can't remove key '{keys}'"
            logging.debug(f"{repr(e)} - {err}")
            return

        # Remove file and folder if config empty
        if len(self._cfg[keys[0]]) == 0:
            try:
                os.remove(self._cfg_file)
                os.rmdir(os.path.dirname(self._cfg_file))
            except Exception as e:
                err = f"Can't remove config {self._cfg_file}"
                logging.debug(f"{repr(e)} - {err}")


"""
class ChangeHandler(FileSystemEventHandler):
    file = None
    method = None
    old = 0

    def __init__(self, file, method):
        type(self).file = file
        type(self).method = method

    @staticmethod
    def on_modified(event):
        cfg_path = os.path.join('.', con.DIR_CFG, con.FILE_CFG)

        if event.src_path == cfg_path:
            statbuf = os.stat(event.src_path)
            new = statbuf.st_mtime

            # Workaround for watchdog bug
            # https://github.com/gorakhargosh/watchdog/issues/93
            if (new - ChangeHandler.old) > 0.5:
                if ConfigManager.ignore:
                    ConfigManager.ignore = False
                else:
                    ChangeHandler.method()

            ChangeHandler.old = new
"""

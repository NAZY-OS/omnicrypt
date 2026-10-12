#!/usr/bin/env python3
#
# OmniCrypt D-Bus System Service
# Developer: NAZY-OS
# License: GNU GPL v3

import os
import subprocess
import time
import json
from pydbus import SystemBus
from gi.repository import GLib

BACKEND_SCRIPT = "/usr/local/bin/omnicrypt.sh"
CONFIG_FILE = "/etc/omnicrypt/config.json"

class OmniCryptService:
    '''
    <node>
        <interface name="org.omnicrypt.Manager">
            <method name="GetStatus"><arg type="s" name="status_json" direction="out"/></method>
            <method name="CreateImage">
                <arg type="s" name="mapper" direction="in"/>
                <arg type="s" name="img_path" direction="in"/>
                <arg type="s" name="size_mb" direction="in"/>
                <arg type="s" name="mount" direction="in"/>
                <arg type="s" name="method" direction="in"/>
                <arg type="i" name="exit_code" direction="out"/>
            </method>
            <method name="SetupFolder">
                <arg type="s" name="target_dir" direction="in"/>
                <arg type="s" name="method" direction="in"/>
                <arg type="i" name="exit_code" direction="out"/>
            </method>
            <method name="MountImageWithPassword">
                <arg type="s" name="img_path" direction="in"/>
                <arg type="s" name="mapper_name" direction="in"/>
                <arg type="s" name="mount_point" direction="in"/>
                <arg type="s" name="password" direction="in"/>
                <arg type="i" name="exit_code" direction="out"/>
            </method>
            <method name="UnlockFolderAdvanced">
                <arg type="s" name="target_dir" direction="in"/>
                <arg type="s" name="method" direction="in"/>
                <arg type="s" name="key_file" direction="in"/>
                <arg type="s" name="password" direction="in"/>
                <arg type="i" name="autoclose_min" direction="in"/>
                <arg type="i" name="exit_code" direction="out"/>
            </method>
            <method name="LockFolder"><arg type="s" name="target_dir" direction="in"/><arg type="i" name="exit_code" direction="out"/></method>
            <signal name="StateChanged"/>
        </interface>
    </node>
    '''
    def GetStatus(self):
        if not os.path.exists(CONFIG_FILE):
            return '{"containers": []}'
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)

        containers_result = []
        for c in config.get("containers", []):
            mapper = c.get("mapper")
            img = c.get("image")
            mount = c.get("mount_point")
            method = c.get("fscrypt_method", "custom")

            luks_locked = True
            actual_mount = "N/A"
            res = subprocess.run(["cryptsetup", "status", mapper], capture_output=True)
            if res.returncode == 0:
                luks_locked = False
                mres = subprocess.run(["findmnt", "-n", "-o", "TARGET", f"/dev/mapper/{mapper}"], capture_output=True, text=True)
                actual_mount = mres.stdout.strip() or mount

            folders = []
            if not luks_locked and os.path.isdir(actual_mount):
                for entry in os.listdir(actual_mount):
                    if entry.startswith(".") or entry == "lost+found": continue
                    fpath = os.path.join(actual_mount, entry)
                    if os.path.isdir(fpath):
                        flocked = True
                        sres = subprocess.run(["fscrypt", "status", fpath], capture_output=True, text=True)
                        if "unlocked: yes" in sres.stdout.lower(): flocked = False
                        folders.append({"name": entry, "path": fpath, "locked": flocked, "method": method})

            containers_result.append({"mapper": mapper, "image": img, "mount_point": actual_mount, "luks_locked": luks_locked, "fscrypt_folders": folders})
        return json.dumps({"containers": containers_result})

    def CreateImage(self, mapper, img_path, size_mb, mount, method):
        res = subprocess.run([BACKEND_SCRIPT, "create_image", mapper, img_path, size_mb, mount, method])
        try: self.StateChanged()
        except Exception: pass
        return res.returncode

    def SetupFolder(self, target_dir, method):
        res = subprocess.run([BACKEND_SCRIPT, "setup_folder", target_dir, method])
        try: self.StateChanged()
        except Exception: pass
        return res.returncode

    def MountImageWithPassword(self, img_path, mapper_name, mount_point, password):
        p = subprocess.Popen([BACKEND_SCRIPT, "open_luks", mapper_name, img_path, mount_point], stdin=subprocess.PIPE, text=True)
        p.communicate(input=password)
        try: self.StateChanged()
        except Exception: pass
        return p.returncode

    def UnlockFolderAdvanced(self, target_dir, method, key_file, password, autoclose_min):
        p = subprocess.Popen([BACKEND_SCRIPT, "unlock_fscrypt", target_dir, method, key_file, password], stdin=subprocess.PIPE, text=True)
        p.communicate(input=password)
        if p.returncode != 0: return 1

        if autoclose_min > 0:
            def expire_job():
                subprocess.run([BACKEND_SCRIPT, "lock_fscrypt", target_dir])
                try: self.StateChanged()
                except Exception: pass
            GLib.timeout_add_seconds(autoclose_min * 60, expire_job)

        try: self.StateChanged()
        except Exception: pass
        return 0

    def LockFolder(self, target_dir):
        res = subprocess.run([BACKEND_SCRIPT, "lock_fscrypt", target_dir])
        try: self.StateChanged()
        except Exception: pass
        return res.returncode

if __name__ == "__main__":
    bus = SystemBus()
    bus.publish("org.omnicrypt.Manager", OmniCryptService())
    loop = GLib.MainLoop()
    loop.run()

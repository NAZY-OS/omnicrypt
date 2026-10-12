#!/usr/bin/env python3
#
# OmniCrypt GTK4 GUI Client
# Developer: NAZY-OS
# License: GNU GPL v3

import json
import os
import sys
import threading
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gio", "2.0")
gi.require_version("Notify", "0.7")
gi.require_version("AppIndicator3", "0.1")

from gi.repository import Gio, Gtk, GLib, Notify, AppIndicator3
from pydbus import SystemBus

Notify.init("OmniCrypt")

class OmniCryptWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title("OmniCrypt (Pro) – NAZY-OS")
        self.set_default_size(1050, 650)

        try:
            self.bus = SystemBus()
            self.proxy = self.bus.get("org.omnicrypt.Manager")
            self.proxy.onStateChanged = lambda: GLib.idle_add(self.refresh_status)
        except Exception:
            self.proxy = None

        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.set_child(main_box)

        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin_top=15, margin_bottom=15, margin_start=15, margin_end=15)
        left_box.set_size_request(480, -1)
        main_box.append(left_box)

        hb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        left_box.append(hb)

        btn_ref = Gtk.Button(label="Aktualisieren")
        btn_ref.connect("clicked", lambda w: self.refresh_status())
        hb.append(btn_ref)

        btn_create = Gtk.Button(label="+ Image")
        btn_create.connect("clicked", self.on_create_image_clicked)
        hb.append(btn_create)

        self.status_label = Gtk.Label(label="System bereit (NAZY-OS).", xalign=0)
        left_box.append(self.status_label)

        scrolled = Gtk.ScrolledWindow(vexpand=True, hexpand=True)
        left_box.append(scrolled)
        self.list_box = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
        scrolled.set_child(self.list_box)

        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin_top=15, margin_bottom=15, margin_start=15, margin_end=15)
        right_box.set_hexpand(True)
        main_box.append(right_box)

        right_box.append(Gtk.Label(label="Dateisystem-Browser (Rechtsklick auf .img zum sicheren Mounten)", xalign=0))

        fm_scrolled = Gtk.ScrolledWindow(vexpand=True, hexpand=True)
        right_box.append(fm_scrolled)

        self.current_path = Gio.File.new_for_path(os.path.expanduser("~"))
        self.dir_list_box = Gtk.ListBox()
        self.dir_list_box.connect("row-activated", self.on_row_activated)

        click_controller = Gtk.GestureClick.new()
        click_controller.set_button(3)
        click_controller.connect("pressed", self.on_right_click)
        self.dir_list_box.add_controller(click_controller)

        fm_scrolled.set_child(self.dir_list_box)

        self.refresh_status()
        self.load_directory(self.current_path)

    def set_status(self, text):
        self.status_label.set_text(f"Info: {text}")

    def run_async(self, func, *args):
        def worker():
            try:
                func(*args)
            except Exception as e:
                GLib.idle_add(self.set_status, f"Fehler: {e}")
            GLib.idle_add(self.refresh_status)
        threading.Thread(target=worker, daemon=True).start()

    def refresh_status(self):
        while (row := self.list_box.get_row_at_index(0)):
            self.list_box.remove(row)
        if not self.proxy:
            self.list_box.append(Gtk.Label(label="Keine D-Bus Verbindung."))
            return
        try:
            data = json.loads(self.proxy.GetStatus())
        except Exception:
            return

        for c in data.get("containers", []):
            frame = Gtk.Frame(label=f"Container: {c['mapper']}")
            f_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin_top=8, margin_bottom=8, margin_start=8, margin_end=8)
            frame.set_child(f_box)
            f_box.append(Gtk.Label(label=f"Bild: {c['image']}\nMount: {c['mount_point']} | Status: {'Gesperrt 🔒' if c['luks_locked'] else 'Offen 🔓'}", xalign=0))

            if not c['luks_locked']:
                btn_new_folder = Gtk.Button(label="+ Neuer verschlüsselter Ordner")
                btn_new_folder.connect("clicked", self.on_create_fscrypt_folder, c['mount_point'])
                f_box.append(btn_new_folder)

                for f in c['fscrypt_folders']:
                    r_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                    r_box.append(Gtk.Label(label=f"• {f['name']} [{f['method']}]", xalign=0, hexpand=True))
                    btn = Gtk.Button(label="Entsperren" if f['locked'] else "Sperren")
                    btn.connect("clicked", self.on_toggle_folder, f['path'], f['locked'], f['method'])
                    r_box.append(btn)
                    f_box.append(r_box)
            self.list_box.append(frame)

    def load_directory(self, gfile):
        while (row := self.dir_list_box.get_row_at_index(0)):
            self.dir_list_box.remove(row)
        if (parent := gfile.get_parent()):
            row = Gtk.ListBoxRow()
            row.path = parent
            row.set_child(Gtk.Label(label="📁 ..", xalign=0))
            self.dir_list_box.append(row)
        try:
            enumerator = gfile.enumerate_children("standard::name,standard::type", Gio.FileQueryInfoFlags.NONE, None)
            while (info := enumerator.next_file(None)):
                name = info.get_name()
                if name.startswith("."): continue
                row = Gtk.ListBoxRow()
                row.path = gfile.get_child(name)
                is_dir = info.get_file_type() == Gio.FileType.DIRECTORY
                prefix = "📁 " if is_dir else ("💽 " if name.endswith(".img") else "📄 ")
                row.set_child(Gtk.Label(label=prefix + name, xalign=0))
                self.dir_list_box.append(row)
        except Exception:
            pass
        self.current_path = gfile

    def on_row_activated(self, listbox, row):
        if hasattr(row, "path") and row.path.query_info("standard::type", Gio.FileQueryInfoFlags.NONE, None).get_file_type() == Gio.FileType.DIRECTORY:
            self.load_directory(row.path)

    def on_right_click(self, gesture, n_press, x, y):
        row = self.dir_list_box.get_row_at_y(y)
        if row and hasattr(row, "path") and (path_str := row.path.get_path()) and path_str.endswith(".img"):
            self.prompt_luks_password(path_str)

    def prompt_luks_password(self, img_path):
        dialog = Gtk.Dialog(title="LUKS-Container sicher entsperren", transient_for=self, modal=True)
        dialog.add_button("Abbrechen", Gtk.ResponseType.CANCEL)
        dialog.add_button("Entsperren", Gtk.ResponseType.OK)
        
        area = dialog.get_content_area()
        area.set_margin_top(12); area.set_margin_bottom(12); area.set_margin_start(12); area.set_margin_end(12); area.set_spacing(6)
        area.append(Gtk.Label(label=f"Passwort für Container (wird nicht gespeichert):\n{img_path}", xalign=0))
        
        entry = Gtk.Entry(visibility=False)
        area.append(entry)

        dialog.connect("response", lambda d, r: self.execute_luks_mount(d, r, img_path, entry))
        dialog.present()

    def execute_luks_mount(self, dialog, response, img_path, entry):
        pwd = entry.get_text()
        dialog.destroy()
        if response == Gtk.ResponseType.OK and self.proxy:
            mapper_name = os.path.basename(img_path).replace(".img", "")
            mount_point = f"/mnt/{mapper_name}"
            self.run_async(self.proxy.MountImageWithPassword, img_path, mapper_name, mount_point, pwd)
            self.set_status("LUKS Container sicher eingehängt.")

    def on_create_image_clicked(self, btn):
        dialog = Gtk.Dialog(title="Neues Verschlüsselungs-Image erstellen", transient_for=self, modal=True)
        dialog.add_button("Abbrechen", Gtk.ResponseType.CANCEL)
        dialog.add_button("Erstellen", Gtk.ResponseType.OK)
        
        area = dialog.get_content_area()
        area.set_margin_top(12); area.set_margin_bottom(12); area.set_margin_start(12); area.set_margin_end(12); area.set_spacing(6)
        
        area.append(Gtk.Label(label="Mapper-Name:", xalign=0))
        e_mapper = Gtk.Entry(text="secure_data")
        area.append(e_mapper)

        area.append(Gtk.Label(label="Speicherort & Dateiname (.img):", xalign=0))
        e_path = Gtk.Entry(text="/var/lib/secure_data.img")
        area.append(e_path)

        area.append(Gtk.Label(label="Größe in MB (z.B. 1024):", xalign=0))
        e_size = Gtk.Entry(text="1024")
        area.append(e_size)

        area.append(Gtk.Label(label="Mountpunkt:", xalign=0))
        e_mount = Gtk.Entry(text="/mnt/secure_data")
        area.append(e_mount)

        area.append(Gtk.Label(label="Fscrypt Methode (custom, login, raw_key):", xalign=0))
        e_method = Gtk.Entry(text="custom")
        area.append(e_method)

        dialog.connect("response", lambda d, r: self.submit_create_image(d, r, e_mapper, e_path, e_size, e_mount, e_method))
        dialog.present()

    def submit_create_image(self, dialog, response, e_mapper, e_path, e_size, e_mount, e_method):
        if response == Gtk.ResponseType.OK:
            m = e_mapper.get_text().strip()
            p = e_path.get_text().strip()
            s = e_size.get_text().strip()
            mp = e_mount.get_text().strip()
            meth = e_method.get_text().strip()
            if self.proxy:
                self.run_async(self.proxy.CreateImage, m, p, s, mp, meth)
                self.set_status(f"Image {p} erstellt.")
        dialog.destroy()

    def on_create_fscrypt_folder(self, btn, mount_point):
        dialog = Gtk.Dialog(title="Neuen fscrypt Ordner anlegen", transient_for=self, modal=True)
        dialog.add_button("Abbrechen", Gtk.ResponseType.CANCEL)
        dialog.add_button("Erstellen", Gtk.ResponseType.OK)
        
        area = dialog.get_content_area()
        area.set_margin_top(12); area.set_margin_bottom(12); area.set_margin_start(12); area.set_margin_end(12); area.set_spacing(6)
        
        area.append(Gtk.Label(label=f"Ordnername in {mount_point}:", xalign=0))
        e_name = Gtk.Entry(text="geheim")
        area.append(e_name)

        area.append(Gtk.Label(label="Methode (custom, login, raw_key):", xalign=0))
        e_method = Gtk.Entry(text="custom")
        area.append(e_method)

        dialog.connect("response", lambda d, r: self.submit_setup_folder(d, r, mount_point, e_name, e_method))
        dialog.present()

    def submit_setup_folder(self, dialog, response, mount_point, e_name, e_method):
        if response == Gtk.ResponseType.OK:
            target_path = os.path.join(mount_point, e_name.get_text().strip())
            method = e_method.get_text().strip()
            if self.proxy:
                self.run_async(self.proxy.SetupFolder, target_path, method)
                self.set_status(f"Ordner erstellt: {target_path}")
        dialog.destroy()

    def on_toggle_folder(self, btn, fpath, locked, method):
        if not locked:
            self.run_async(self.proxy.LockFolder, fpath)
            self.set_status(f"Ordner gesperrt: {fpath}")
            return

        if method == "raw_key":
            dialog = Gtk.FileDialog(title="Raw-Key Schlüsseldatei auswählen")
            dialog.open(self, None, lambda s, r: self.finish_raw_key_unlock(s, r, fpath, method))
        elif method == "login":
            self.prompt_fscrypt_password(fpath, method, "System-Login Passwort eingeben:")
        else:
            self.prompt_fscrypt_password(fpath, method, "Fscrypt Custom-Passwort eingeben:")

    def finish_raw_key_unlock(self, dialog, result, fpath, method):
        try:
            if (gfile := dialog.open_finish(result)):
                self.run_async(self.proxy.UnlockFolderAdvanced, fpath, method, gfile.get_path(), "", 10)
        except Exception:
            pass

    def prompt_fscrypt_password(self, fpath, method, label_text):
        dialog = Gtk.Dialog(title=f"Fscrypt ({method})", transient_for=self, modal=True)
        dialog.add_button("Abbrechen", Gtk.ResponseType.CANCEL)
        dialog.add_button("Entsperren", Gtk.ResponseType.OK)
        
        area = dialog.get_content_area()
        area.set_margin_top(12); area.set_margin_bottom(12); area.set_margin_start(12); area.set_margin_end(12); area.set_spacing(6)
        area.append(Gtk.Label(label=label_text, xalign=0))
        
        entry = Gtk.Entry(visibility=False)
        area.append(entry)

        dialog.connect("response", lambda d, r: self.execute_fscrypt_unlock_with_pwd(d, r, fpath, method, entry))
        dialog.present()

    def execute_fscrypt_unlock_with_pwd(self, dialog, response, fpath, method, entry):
        pwd = entry.get_text()
        dialog.destroy()
        if response == Gtk.ResponseType.OK and self.proxy:
            self.run_async(self.proxy.UnlockFolderAdvanced, fpath, method, "", pwd, 10)
            self.set_status(f"Ordner entsperrt mit Methode: {method}")

class OmniCryptApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.omnicrypt.Manager")
    def do_activate(self):
        OmniCryptWindow(application=self).present()

if __name__ == "__main__":
    sys.exit(OmniCryptApp().run(sys.argv))

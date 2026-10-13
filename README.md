<div align="center">

  <h1>🔒 OmniCrypt</h1>
  <p><strong>Professional-grade LUKS container & fscrypt manager for Linux (NAZY-OS) – v.0.93</strong></p>

  <p>
    <img src="omnicrypt.svg" width="128" height="128" alt="OmniCrypt Logo">
  </p>

  <p>
    <img src="https://img.shields.io/badge/version-v.0.93-blue.svg" alt="Version">
    <img src="https://img.shields.io/badge/license-GPL--3.0--or--later-blue.svg" alt="License">
    <img src="https://img.shields.io/badge/platform-Linux-lightgrey.svg" alt="Platform">
    <img src="https://img.shields.io/badge/toolkit-GTK4%2FAdwaita-success.svg" alt="GTK4">
    <img src="https://img.shields.io/badge/backend-Python%2FBash-informational.svg" alt="Backend">
  </p>

</div>

---

## 📖 Inhaltsverzeichnis
- [Funktionen](#-funktionen)
- [Architektur & Tech Stack](#-architektur--tech-stack)
- [Voraussetzungen & Build-Tools](#-voraussetzungen--build-tools)
- [Installationsanleitung](#-installationsanleitung)
- [Lizenz](#-lizenz)

---

## ✨ Funktionen (v.0.93)

* **🔐 Sichere Passwortverarbeitung:** Passwörter werden über sichere Standard-Input-Pipelines (stdin) übergeben und niemals persistent auf der Festplatte gespeichert.
* **🗂️ Klassisches Windows 7 Design & Menüleiste:** Klassischer Fensterril mit nativer Menüleiste, Tab-Navigation und korrektem UI-Rendering beim Start (keine schwarzen Bildschirme).
* **📁 Image- & Ordnerverwaltung:**
  * **LUKS-Container:** Durchsuchen, Erstellen neuer Sparse-Images, Formatieren (`mkfs.ext4`) und sicheres Mounten.
  * **fscrypt-Ordner:** Initialisieren, Protektoren hinzufügen, Entsperren und Sperren verschlüsselter Verzeichnisse.
* **⌨️ Globale Tastenkombinationen:** 
  * `Ctrl + Alt + G`: Fenster ein-/ausblenden oder in den Vordergrund bringen.
  * `Ctrl + Shift + L`: Notfall-Lockdown (Panic Button: sofortiges `sync`, Unmount und Sperren aller Container/Ordner).
* **tray System-Tray-Integration:** Interaktives Statusleisten-Symbol mit dynamischem Zustandswechsel (Gesichert vs. Unlocked/Aktiv) für XFCE, KDE Plasma und GNOME.
* **🔊 Audio- & Desktop-Benachrichtigungen:** Integrierte Benachrichtigungen und akustische System-Signale (``) für Sicherheitsereignisse und Inaktivitäts-Warnungen.
* **⏱️ Auto-Close-Timer & Optionen:** Konfigurierbare Inaktivitäts-Timer zur automatischen Schließung inaktiver Vaults.

---

## 🛠️ Voraussetzungen & Build-Tools

* **Arch Linux:** `base-devel`, `python`, `python-gobject`, `python-pydbus`, `gtk4`, `libayatana-appindicator`, `cryptsetup`, `fscrypt`, `meson`, `ninja`, `gobject-introspection`
* **Fedora Linux:** `Development Tools`, `python3`, `python3-gobject`, `python3-pydbus`, `gtk4`, `libayatana-appindicator-gtk3`, `cryptsetup`, `fscrypt`, `meson`, `ninja-build`, `python3-virtualenv`
* **Debian / Ubuntu:** `build-essential`, `python3`, `python3-gi`, `python3-pydbus`, `gir1.2-gtk-4.0`, `libayatana-appindicator3-1`, `gir1.2-ayatanaappindicator3-0.1`, `cryptsetup`, `fscrypt`, `meson`, `ninja-build`, `python3-venv`

---

## 🚀 Installationsanleitung

### Schritt 1: Systemabhängigkeiten installieren
> **👤 Als normaler Benutzer ausführen**

* **Arch Linux:**
  ```bash
  pacman -S --needed base-devel python python-gobject python-pydbus gtk4 libayatana-appindicator cryptsetup fscrypt meson ninja gobject-introspection
  ```
* **Fedora Linux:**
  ```bash
  dnf groupinstall "Development Tools"
  dnf install python3 python3-gobject python3-pydbus gtk4 libayatana-appindicator-gtk3 cryptsetup fscrypt meson ninja-build python3-virtualenv
  ```
* **Debian / Ubuntu:**
  ```bash
  apt update
  apt install build-essential python3 python3-gi python3-pydbus gir1.2-gtk-4.0 libayatana-appindicator3-1 gir1.2-ayatanaappindicator3-0.1 cryptsetup fscrypt meson ninja-build python3-venv
  ```

---

### Schritt 2: Python Virtuelle Umgebung einrichten
> **👤 Als normaler Benutzer ausführen**

```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Schritt 3: Projekt kompilieren & installieren
> **🔑 Als Root / Administrator ausführen**

```bash
su -
export GI_TYPELIB_PATH=/usr/lib/girepository-1.0
meson setup builddir --prefix=/usr
ninja -C builddir
ninja -C builddir install
```

---

## 📜 Lizenz
Lizenziert unter der **GNU General Public License v3.0 oder höher (GPLv3+)**. Entwickelt für **NAZY-OS** (v.0.93).

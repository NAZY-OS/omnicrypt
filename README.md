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

## 📖 Table of Contents
- [Features](#-features)
- [Architecture & Tech Stack](#-architecture--tech-stack)
- [Prerequisites & Build Tools](#-prerequisites--build-tools)
- [Installation Guide](#-installation-guide)
- [License](#-license)

---

## ✨ Features (v.0.93)

* **🔐 Secure Password Handling:** Passwords pass through secure stdin pipes and are never stored persistently on disk.
* **🗂️ Classic Windows 7 Aesthetic & Menu Bar:** Classic window style with a native menu bar, tab navigation, and proper UI rendering on startup (eliminating black screens).
* **📁 Image & Folder Management:**
  * **LUKS Containers:** Browse, create new sparse images, format (`mkfs.ext4`), and mount via secure stdin.
  * **fscrypt Folders:** Initialize, add protectors, unlock, and lock encrypted directories.
* **⌨️ Global Shortcuts:** 
  * `Ctrl + Alt + G`: Toggle/Bring window to front.
  * `Ctrl + Shift + L`: Emergency Lockdown (Panic Button: instant `sync`, unmount, and lock all containers/folders).
* **tray System Tray Integration:** Fully interactive status icon menu with dynamic state changing (Locked vs. Unlocked/Active) across XFCE, KDE Plasma, and GNOME.
* **🔊 Audio & Desktop Notifications:** Built-in desktop alerts and terminal bell (`\a`) info sound cues for security events and auto-close warnings.
* **⏱️ Auto-Close Timer & Options:** Configurable inactivity timers to automatically dismount and lock inactive vaults.

---

## 🛠️ Prerequisites & Build Tools

* **Arch Linux:** `base-devel`, `python`, `python-gobject`, `python-pydbus`, `gtk4`, `libayatana-appindicator`, `cryptsetup`, `fscrypt`, `meson`, `ninja`, `gobject-introspection`
* **Fedora Linux:** `Development Tools`, `python3`, `python3-gobject`, `python3-pydbus`, `gtk4`, `libayatana-appindicator-gtk3`, `cryptsetup`, `fscrypt`, `meson`, `ninja-build`, `python3-virtualenv`
* **Debian / Ubuntu:** `build-essential`, `python3`, `python3-gi`, `python3-pydbus`, `gir1.2-gtk-4.0`, `libayatana-appindicator3-1`, `gir1.2-ayatanaappindicator3-0.1`, `cryptsetup`, `fscrypt`, `meson`, `ninja-build`, `python3-venv`

---

## 🚀 Installation Guide

### Step 1: Install System Dependencies
> **👤 Run as Normal User**

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

### Step 2: Setup Python Virtual Environment
> **👤 Run as Normal User**

```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 3: Build & Install Project
> **🔑 Run as Root / Administrator**

```bash
su -
export GI_TYPELIB_PATH=/usr/lib/girepository-1.0
meson setup builddir --prefix=/usr
ninja -C builddir
ninja -C builddir install
```

---

## 📜 License
Licensed under the **GNU General Public License v3.0 or later (GPLv3+)**. Developed for **NAZY-OS** (v.0.93).

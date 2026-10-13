# OmniCrypt (NAZY-OS)

**OmniCrypt** is a modern, secure non-interactive management tool designed for LUKS container images and `fscrypt` folder encryption on Linux. Built with Python, GTK4/Libadwaita, a robust Bash/D-Bus backend, and AppIndicator taskbar integration.

---

## Features

- **Secure Password Handling:** Passwords are passed via secure stdin pipes and are never stored persistently on disk.
- **Modern GTK4/Libadwaita UI:** Clean master-detail layout with real-time status updates, status badges, and an integrated filesystem browser.
- **System Tray (AppIndicator):** Quick access menu for status monitoring, quick locking/unlocking, and emergency triggers under both X11 and Wayland (via SNI support).
- **Admin Security (`pkexec` / Polkit):** Protected configuration changes and system-level operations.
- **Emergency Lockdown ("Panic Button"):** Instant data synchronization (`sync`), unmounting, and locking of all active containers with a single click.
- **Smart Auto-Close & Alerts:** Inactivity timers with pre-lock warnings, interactive desktop prompt dialogs, and audio/visual notifications.

---

## Technology Stack

- **Backend:** Bash script (`cryptsetup`, `fscrypt`, `truncate`, `mkfs.ext4`)
- **Service Layer:** Python D-Bus Service (`org.omnicrypt.Manager`)
- **Frontend:** Python GTK4 / Libadwaita & AppIndicator3
- **Build System:** Meson & Ninja

---

## Installation Guide (Secure Virtual Environment & System Package Workflow)

### Prerequisites (All Distributions)
Ensure your system has the core security utilities installed:
- `cryptsetup`
- `fscrypt`
- `util-linux` (`truncate`, `mount`, `umount`)

### 1. Install System Dependencies

- **Debian / Ubuntu:**
  ```bash
  sudo apt update
  sudo apt install python3 python3-gi python3-pydbus gir1.2-gtk-4.0 libayatana-appindicator3-1 cryptsetup fscrypt meson ninja-build python3-venv
  ```

- **Fedora Linux:**
  ```bash
  sudo dnf install python3 python3-gobject python3-pydbus gtk4 libayatana-appindicator-gtk3 cryptsetup fscrypt meson ninja-build python3-virtualenv
  ```

- **Arch Linux:**
  ```bash
  sudo pacman -S python python-gobject python-pydbus gtk4 libayatana-appindicator cryptsetup fscrypt meson ninja
  ```

### 2. Python Virtual Environment Setup
To keep system packages secure and isolated, set up a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Build & Install via Meson
```bash
meson setup builddir --prefix=/usr
ninja -C builddir
sudo ninja -C builddir install
```

---

## License

Licensed under the **GNU General Public License v3.0 or later (GPLv3+)**. Developed for **NAZY-OS**.

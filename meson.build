project('omnicrypt',
  version: '1.0.0',
  license: 'GPL-3.0-or-later',
  meson_version: '>= 0.56.0'
)

i18n = import('i18n')

# Installation der Backend- und Servicedateien
install_data(
  'omnicrypt.sh',
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

install_data(
  'omnicrypt-service.py',
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

install_data(
  'omnicrypt_gui.py',
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

# Polkit Action Policy
install_data(
  'org.omnicrypt.Manager.policy',
  install_dir: join_paths(get_option('datadir'), 'polkit-1', 'actions')
)

# Konfigurationsvorlage
install_data(
  'config.json',
  install_dir: join_paths(get_option('sysconfdir'), 'omnicrypt')
)

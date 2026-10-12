#!/usr/bin/env bash
#
# OmniCrypt secure backend worker with image creation & fscrypt folder setup
# Developer: NAZY-OS
# License: GNU GPL v3

set -uo pipefail

CONFIG_DIR="/etc/omnicrypt"
RUN_DIR="/run/omnicrypt"
CONFIG_FILE="$CONFIG_DIR/config.json"

init_environment() {
    mkdir -p "$CONFIG_DIR" "$RUN_DIR" 2>/dev/null || true
    chmod 755 "$RUN_DIR" 2>/dev/null || true
    if [[ ! -f "$CONFIG_FILE" ]]; then
        cat << 'EOF' > "$CONFIG_FILE"
{
  "containers": [
    {
      "mapper": "secure_img1",
      "image": "/var/lib/secure1.img",
      "mount_point": "/mnt/secure1",
      "fscrypt_method": "custom",
      "auto_mount_on_start": false,
      "default_autoclose_min": 10
    }
  ]
}
EOF
    fi
}

backend_create_container_image() {
    local mapper="$1"
    local img_path="$2"
    local size_mb="$3"
    local mount_point="$4"
    local method="$5"

    [[ -f "$img_path" ]] && return 1

    # 1. Create sparse image file
    truncate -s "${size_mb}M" "$img_path" || return 1

    # 2. Format ext4 with encryption support enabled
    mkfs.ext4 -O encrypt -F "$img_path" || return 1

    # 3. Register in config.json
    if command -v jq >/dev/null 2>&1; then
        local tmp
        tmp=$(mktemp)
        jq --arg m "$mapper" --arg i "$img_path" --arg mp "$mount_point" --arg met "$method" \
           '.containers += [{"mapper": $m, "image": $i, "mount_point": $mp, "fscrypt_method": $met, "auto_mount_on_start": false, "default_autoclose_min": 10}]' \
           "$CONFIG_FILE" > "$tmp" && mv "$tmp" "$CONFIG_FILE"
    fi
    return 0
}

backend_setup_fscrypt_folder() {
    local target_dir="$1"
    local method="${2:-custom}"

    mkdir -p "$target_dir" || return 1
    local parent_mount
    parent_mount=$(df -P "$target_dir" | awk 'NR==2 {print $6}')
    
    if ! fscrypt status "$parent_mount" 2>&1 | grep -qi "supported: yes"; then
        fscrypt setup "$parent_mount" --force || return 1
    fi

    fscrypt encrypt "$target_dir" --source="$method" --automatic || return 1
    return 0
}

backend_open_luks_with_password() {
    local mapper_name="$1"
    local img_path="$2"
    local mount_point="$3"
    
    cryptsetup status "$mapper_name" >/dev/null 2>&1 && return 0
    [[ ! -f "$img_path" ]] && return 1

    # Pass password via stdin pipe securely without saving to disk
    cryptsetup luksOpen --key-file - "$img_path" "$mapper_name" || return 1
    mkdir -p -- "$mount_point"
    mount "/dev/mapper/$mapper_name" "$mount_point"
}

backend_close_luks() {
    local mapper_name="$1"
    local mount_point="$2"
    mountpoint -q -- "$mount_point" && umount "$mount_point" || true
    cryptsetup status "$mapper_name" >/dev/null 2>&1 && cryptsetup luksClose "$mapper_name" || true
}

backend_unlock_fscrypt() {
    local target_dir="$1"
    local method="$2"
    local key_file="${3:-}"
    local password="${4:-}"
    [[ ! -d "$target_dir" ]] && return 1

    if [[ -d "$target_dir/.fscrypt" ]] && fscrypt status "$target_dir" 2>&1 | grep -qi "unlocked: yes"; then
        return 0
    fi

    case "$method" in
        custom)
            echo "$password" | fscrypt unlock --quiet "$target_dir"
            ;;
        login)
            echo "$password" | fscrypt unlock --quiet --source=login "$target_dir"
            ;;
        raw_key)
            if [[ -n "$key_file" && -f "$key_file" ]]; then
                fscrypt unlock --quiet --key="$key_file" "$target_dir"
            else
                return 1
            fi
            ;;
        *)
            return 1
            ;;
    esac
}

backend_lock_fscrypt() {
    fscrypt lock "$1"
}

main() {
    init_environment
    local action="${1:-}"
    shift || true
    case "$action" in
        create_image) backend_create_container_image "$@" ;;
        setup_folder) backend_setup_fscrypt_folder "$@" ;;
        open_luks) backend_open_luks_with_password "$@" ;;
        close_luks) backend_close_luks "$@" ;;
        unlock_fscrypt) backend_unlock_fscrypt "$@" ;;
        lock_fscrypt) backend_lock_fscrypt "$@" ;;
        *) exit 1 ;;
    esac
}
main "$@"

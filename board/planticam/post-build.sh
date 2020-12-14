#!/bin/bash

set -u
set -e

mkdir -p "${TARGET_DIR}"/etc/systemd/system/getty.target.wants
# Add a console on tty1
#ln -sf /usr/lib/systemd/system/getty@.service "${TARGET_DIR}"/etc/systemd/system/getty.target.wants/getty@tty1.service

# Add a console on ttyAMA0
ln -sf /usr/lib/systemd/system/serial-getty@.service "${TARGET_DIR}"/etc/systemd/system/getty.target.wants/serial-getty@ttyGS0.service

if grep -qE '/var' "${TARGET_DIR}/etc/fstab"; then
	grep -v '/var' "${TARGET_DIR}/etc/fstab" > "${TARGET_DIR}/etc/fstab.new"
	rm "${TARGET_DIR}/etc/fstab"
	mv "${TARGET_DIR}/etc/fstab.new" "${TARGET_DIR}/etc/fstab"
fi
echo 'tmpfs           /var            tmpfs   rw,mode=1777,size=64m' >> "${TARGET_DIR}/etc/fstab"

if grep -qE '/boot' "${TARGET_DIR}/etc/fstab"; then
	grep -v '/boot' "${TARGET_DIR}/etc/fstab" > "${TARGET_DIR}/etc/fstab.new"
	rm "${TARGET_DIR}/etc/fstab"
	mv "${TARGET_DIR}/etc/fstab.new" "${TARGET_DIR}/etc/fstab"
fi
echo '/dev/mmcblk0p1  /boot           vfat    ro,uid=0,gid=0,dmask=0077,fmask=0077' >> "${TARGET_DIR}/etc/fstab"

if grep -qE '/data' "${TARGET_DIR}/etc/fstab"; then
	grep -v '/data' "${TARGET_DIR}/etc/fstab" > "${TARGET_DIR}/etc/fstab.new"
	rm "${TARGET_DIR}/etc/fstab"
	mv "${TARGET_DIR}/etc/fstab.new" "${TARGET_DIR}/etc/fstab"
fi
echo '/dev/mmcblk0p3  /data           vfat    noauto,ro,uid=0,gid=0,dmask=0077,fmask=0077' >> "${TARGET_DIR}/etc/fstab"

# Disable fsck on root
sed -ie '/^\/dev\/root/ s/0 1/0 0/' "${TARGET_DIR}/etc/fstab"

# Disable unused services
ln -sf /dev/null "${TARGET_DIR}"/etc/systemd/system/sys-kernel-debug.mount
ln -sf /dev/null "${TARGET_DIR}"/etc/systemd/system/dev-mqueue.mount
ln -sf /dev/null "${TARGET_DIR}"/etc/systemd/system/systemd-update-utmp.service
ln -sf /dev/null "${TARGET_DIR}"/etc/systemd/system/systemd-update-utmp-runlevel.service

# link wpa_supplicant.conf to boot
rm -f "${TARGET_DIR}"/etc/systemd/system/multi-user.target.wants/wpa_supplicant.service
rm -f "${TARGET_DIR}"/etc/wpa_supplicant.conf
ln -sf /boot/wpa_supplicant.conf "${TARGET_DIR}"/etc/wpa_supplicant.conf


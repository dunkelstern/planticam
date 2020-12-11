#!/bin/bash

set -e

BOARD_DIR="$(dirname $0)"
BOARD_NAME="$(basename ${BOARD_DIR})"
GENIMAGE_CFG="${BOARD_DIR}/genimage-${BOARD_NAME}.cfg"
GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"

for arg in "$@"
do
	case "${arg}" in
		--add-miniuart-bt-overlay)
		if ! grep -qE '^dtoverlay=' "${BINARIES_DIR}/rpi-firmware/config.txt"; then
			echo "Adding 'dtoverlay=miniuart-bt' to config.txt (fixes ttyAMA0 serial console)."
			cat << __EOF__ >> "${BINARIES_DIR}/rpi-firmware/config.txt"

# fixes rpi (3B, 3B+, 3A+, 4B and Zero W) ttyAMA0 serial console
dtoverlay=miniuart-bt
__EOF__
		fi
		;;
		--aarch64)
		# Run a 64bits kernel (armv8)
		sed -e '/^kernel=/s,=.*,=Image,' -i "${BINARIES_DIR}/rpi-firmware/config.txt"
		if ! grep -qE '^arm_64bit=1' "${BINARIES_DIR}/rpi-firmware/config.txt"; then
			cat << __EOF__ >> "${BINARIES_DIR}/rpi-firmware/config.txt"

# enable 64bits support
arm_64bit=1
__EOF__
		fi
		;;
		--gpu_mem_256=*|--gpu_mem_512=*|--gpu_mem_1024=*)
		# Set GPU memory
		gpu_mem="${arg:2}"
		sed -e "/^${gpu_mem%=*}=/s,=.*,=${gpu_mem##*=}," -i "${BINARIES_DIR}/rpi-firmware/config.txt"
		;;
		--configure-planticam)
		# Configure planticam
		if ! grep -qE '^dtoverlay=dwc2,g_ether' "${BINARIES_DIR}/rpi-firmware/config.txt"; then

			cat << __EOF__ >> "${BINARIES_DIR}/rpi-firmware/config.txt"
dtoverlay=dwc2,g_ether
__EOF__
		fi

		# Configure uart on 40-pin header
		if ! grep -qE '^enable_uart=1' "${BINARIES_DIR}/rpi-firmware/config.txt"; then

			cat << __EOF__ >> "${BINARIES_DIR}/rpi-firmware/config.txt"
enable_uart=1
__EOF__
		fi

		# Set the bootloader delay to 0 seconds
		if ! grep -qE '^boot_delay=0' "${BINARIES_DIR}/rpi-firmware/config.txt"; then
			cat << __EOF__ >> "${BINARIES_DIR}/rpi-firmware/config.txt"
boot_delay=0
__EOF__
		fi

		# Set turbo mode for boot
		if ! grep -qE '^initial_turbo' "${BINARIES_DIR}/rpi-firmware/config.txt"; then
			cat << __EOF__ >> "${BINARIES_DIR}/rpi-firmware/config.txt"
initial_turbo=10
__EOF__
		fi

		# Inform the kernel about the filesystem and ro state
		if ! grep -qE 'rootfstype=squashfs ro' "${BINARIES_DIR}/rpi-firmware/cmdline.txt"; then
			sed '/^root=/ s/$/ rootfstype=squashfs ro/' -i "${BINARIES_DIR}/rpi-firmware/cmdline.txt"
		fi

		if ! grep -qE 'modules-load=dwc2,libcomposite' "${BINARIES_DIR}/rpi-firmware/cmdline.txt"; then
			sed '/^root=/ s/$/ modules-load=dwc2,libcomposite/' -i "${BINARIES_DIR}/rpi-firmware/cmdline.txt"
		fi

		# Random seed, else the ssh daemon will block on boot
		RND=`head -c 250 /dev/urandom |base64 -w0 -`
		if ! grep -qE 'systemd.random_seed=' "${BINARIES_DIR}/rpi-firmware/cmdline.txt"; then
			sed '/^root=/ s@$@ systemd.random_seed='$RND'@' -i "${BINARIES_DIR}/rpi-firmware/cmdline.txt"
		else
			sed 's@systemd.random_seed=[^ ]*@systemd.random_seed='$RND'@' -i "${BINARIES_DIR}/rpi-firmware/cmdline.txt"
		fi

		# Suppress kernel output during boot
		if ! grep -qE 'quiet' "${BINARIES_DIR}/rpi-firmware/cmdline.txt"; then
			sed '/^root=/ s/$/ quiet/' -i "${BINARIES_DIR}/rpi-firmware/cmdline.txt"
		fi
		
		# Add example config
		cp "$BR2_EXTERNAL_PLANTICAM_PATH/wpa_supplicant.conf" "${BINARIES_DIR}/rpi-firmware/wpa_supplicant.conf"
		cp "$BR2_EXTERNAL_PLANTICAM_PATH/planticam.conf" "${BINARIES_DIR}/rpi-firmware/planticam.conf"

		# ssh client keys
		if [ ! -e id_ed25519 ] ; then
			ssh-keygen -t ed25519 -f id_ed25519 -q -N ""
			cp id_ed25519* "${BINARIES_DIR}/rpi-firmware/"
		fi

		# ssh host keys
		mkdir -p "${BINARIES_DIR}/rpi-firmware/ssh-keys/"
		if [ ! -f ssh_host_rsa_key ] ; then
			ssh-keygen -t rsa -f ssh_host_rsa_key -C '' -N ''
			cp ssh_host_rsa_key* "${BINARIES_DIR}/rpi-firmware/ssh-keys/"
		fi
		if [ ! -f ssh_host_dsa_key ] ; then
			ssh-keygen -t dsa -f ssh_host_dsa_key -C '' -N ''
			cp ssh_host_dsa_key* "${BINARIES_DIR}/rpi-firmware/ssh-keys/"
		fi
		if [ ! -f ssh_host_ecdsa_key ] ; then
			ssh-keygen -t ecdsa -f ssh_host_ecdsa_key -C '' -N ''
			cp ssh_host_ecdsa_key* "${BINARIES_DIR}/rpi-firmware/ssh-keys/"
		fi
		if [ ! -f ssh_host_ed25519_key ] ; then
			ssh-keygen -t ed25519 -f ssh_host_ed25519_key -C '' -N ''
			cp ssh_host_ed25519_key* "${BINARIES_DIR}/rpi-firmware/ssh-keys/"
		fi
		;;
	esac

done

# Pass an empty rootpath. genimage makes a full copy of the given rootpath to
# ${GENIMAGE_TMP}/root so passing TARGET_DIR would be a waste of time and disk
# space. We don't rely on genimage to build the rootfs image, just to insert a
# pre-built one in the disk image.

trap 'rm -rf "${ROOTPATH_TMP}"' EXIT
ROOTPATH_TMP="$(mktemp -d)"

rm -rf "${GENIMAGE_TMP}"

genimage \
	--rootpath "${ROOTPATH_TMP}"   \
	--tmppath "${GENIMAGE_TMP}"    \
	--inputpath "${BINARIES_DIR}"  \
	--outputpath "${BINARIES_DIR}" \
	--config "${GENIMAGE_CFG}"

exit $?

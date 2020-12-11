PLANTICAM_NETCONFIG_VERSION = 1.0
PLANTICAM_NETCONFIG_SITE = 
PLANTICAM_NETCONFIG_SOURCE = 
PLANTICAM_NETCONFIG_LICENSE = BSD-3-Clause
PLANTICAM_NETCONFIG_LICENSE_FILES = LICENSE
PLANTICAM_NETCONFIG_DEST_DIR = /opt/planticam_netconfig
PLANTICAM_STILLCAPTURE_INIT_SYSTEMD_TARGET = multi-user.target.wants

define PLANTICAM_NETCONFIG_BUILD_CMDS
	# $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D)
endef

define PLANTICAM_NETCONFIG_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)$(PLANTICAM_NETCONFIG_DEST_DIR)
	mkdir -p $(TARGET_DIR)/etc/network/
	mkdir -p $(TARGET_DIR)/etc/ssh/
	mkdir -p $(TARGET_DIR)/usr/lib/tmpfiles.d/
	mkdir -p $(TARGET_DIR)/usr/bin/
	$(INSTALL) -D -m 644 $(PLANTICAM_NETCONFIG_PKGDIR)/sshd_config $(TARGET_DIR)/etc/ssh/
	$(INSTALL) -D -m 644 $(PLANTICAM_NETCONFIG_PKGDIR)/dnsmasq.conf $(TARGET_DIR)/etc/
	$(INSTALL) -D -m 644 $(PLANTICAM_NETCONFIG_PKGDIR)/nsswitch.conf $(TARGET_DIR)/etc/
	$(INSTALL) -D -m 644 $(PLANTICAM_NETCONFIG_PKGDIR)/interfaces $(TARGET_DIR)/etc/network/
	$(INSTALL) -D -m 755 $(PLANTICAM_NETCONFIG_PKGDIR)/ethernet-gadget.sh $(TARGET_DIR)/usr/bin/
	$(INSTALL) -D -m 755 $(PLANTICAM_NETCONFIG_PKGDIR)/var.sh $(TARGET_DIR)/usr/bin/
endef

define PLANTICAM_NETCONFIG_INSTALL_INIT_SYSTEMD
	mkdir -p $(TARGET_DIR)/etc/systemd/system/$(PLANTICAM_NETCONFIG_INIT_SYSTEMD_TARGET)
	mkdir -p $(TARGET_DIR)/usr/lib/systemd/system/
	$(INSTALL) -D -m 644 $(PLANTICAM_NETCONFIG_PKGDIR)/dnsmasq.service $(TARGET_DIR)/usr/lib/systemd/system/
	$(INSTALL) -D -m 644 $(PLANTICAM_NETCONFIG_PKGDIR)/ethernet-gadget.service $(TARGET_DIR)/usr/lib/systemd/system/
	$(INSTALL) -D -m 644 $(PLANTICAM_NETCONFIG_PKGDIR)/sshd.service $(TARGET_DIR)/usr/lib/systemd/system/
	$(INSTALL) -D -m 644 $(PLANTICAM_NETCONFIG_PKGDIR)/wpa_supplicant_wlan0.service $(TARGET_DIR)/usr/lib/systemd/system/
endef

$(eval $(generic-package))

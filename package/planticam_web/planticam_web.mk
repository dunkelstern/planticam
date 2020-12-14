PLANTICAM_WEB_VERSION = 1.0
PLANTICAM_WEB_SITE =
PLANTICAM_WEB_SOURCE =
PLANTICAM_WEB_LICENSE = BSD-3-Clause
PLANTICAM_WEB_LICENSE_FILES = LICENSE
PLANTICAM_WEB_DEST_DIR = /opt/planticam_web
#PLANTICAM_WEB_SITE_METHOD = git
PLANTICAM_WEB_INIT_SYSTEMD_TARGET = multi-user.target.wants

define PLANTICAM_WEB_BUILD_CMDS
	# $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D)
endef

define PLANTICAM_WEB_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)$(PLANTICAM_WEB_DEST_DIR)
	mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -D -m 0755 $(PLANTICAM_WEB_PKGDIR)/main.py $(TARGET_DIR)$(PLANTICAM_WEB_DEST_DIR)
	cp -r $(PLANTICAM_WEB_PKGDIR)/static $(TARGET_DIR)$(PLANTICAM_WEB_DEST_DIR)/static
	cp -r $(PLANTICAM_WEB_PKGDIR)/templates $(TARGET_DIR)$(PLANTICAM_WEB_DEST_DIR)/templates
	cp -r $(PLANTICAM_WEB_PKGDIR)/util $(TARGET_DIR)$(PLANTICAM_WEB_DEST_DIR)/util
	cp -r $(PLANTICAM_WEB_PKGDIR)/views $(TARGET_DIR)$(PLANTICAM_WEB_DEST_DIR)/views
	$(INSTALL) -D -m 0755 $(PLANTICAM_WEB_PKGDIR)/make_data_partition.sh $(TARGET_DIR)/usr/bin/
endef

define PLANTICAM_WEB_INSTALL_INIT_SYSTEMD
	mkdir -p $(TARGET_DIR)/etc/systemd/system/$(PLANTICAM_WEB_INIT_SYSTEMD_TARGET)
	mkdir -p $(TARGET_DIR)/usr/lib/systemd/system
	$(INSTALL) -D -m 644 $(PLANTICAM_WEB_PKGDIR)/planticam_web.service $(TARGET_DIR)/usr/lib/systemd/system/
	ln -sf /usr/lib/systemd/system/planticam_web.service $(TARGET_DIR)/etc/systemd/system/$(PLANTICAM_WEB_INIT_SYSTEMD_TARGET)
endef

$(eval $(generic-package))

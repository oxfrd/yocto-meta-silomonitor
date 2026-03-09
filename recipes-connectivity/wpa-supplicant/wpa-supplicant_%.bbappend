FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI += "file://wpa_supplicant-nl80211-wlan0.conf"
SRC_URI += "file://25-wireless.network"

SYSTEMD_AUTO_ENABLE = "enable"
SYSTEMD_SERVICE:${PN}:append = " wpa_supplicant-nl80211@wlan0.service "

do_install:append() {
    # config install
    install -d ${D}${sysconfdir}/wpa_supplicant
    install -D -m 600 ${WORKDIR}/wpa_supplicant-nl80211-wlan0.conf ${D}${sysconfdir}/wpa_supplicant/wpa_supplicant-nl80211-wlan0.conf

    # DHCP config
    install -d ${D}${sysconfdir}/systemd/network
    install -D -m 0644 ${WORKDIR}/25-wireless.network ${D}${sysconfdir}/systemd/network/25-wireless.network

    # linking service
    install -d ${D}${sysconfdir}/systemd/system/multi-user.target.wants/
    ln -s ${systemd_unitdir}/system/wpa_supplicant@.service ${D}${sysconfdir}/systemd/system/multi-user.target.wants/wpa_supplicant-nl80211@wlan0.service
}

FILES:${PN} += " \
    ${sysconfdir}/wpa_supplicant/wpa_supplicant-nl80211-wlan0.conf \
    ${sysconfdir}/systemd/network/25-wireless.network \
    "
    
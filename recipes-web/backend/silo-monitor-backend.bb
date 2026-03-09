SUMMARY = "Backend in flask REST API for silo monitoring"
PN = "silo-monitor-backend"
LICENSE = "CLOSED"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/CC0-1.0;md5=..."

SRC_URI = "file://flask-main.py \
           file://sensors.py \
           file://silo-monitor-flask.service"

RDEPENDS:${PN} += " python3-core python3-json python3-flask"

inherit systemd

SYSTEMD_SERVICE:${PN} = "silo-monitor-flask.service"
SYSTEMD_AUTO_ENABLE = "enable"

do_install() {
    install -d ${D}${localstatedir}/lib/silo-monitor-flask
    install -m 0644 ${WORKDIR}/flask-main.py ${D}${localstatedir}/lib/silo-monitor-flask/
    install -m 0644 ${WORKDIR}/sensors.py ${D}${localstatedir}/lib/silo-monitor-flask/

    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${WORKDIR}/silo-monitor-flask.service ${D}${systemd_system_unitdir}/
}

FILES:${PN} += " ${localstatedir}/lib/silo-monitor-flask/* \
                 ${systemd_system_unitdir}/silo-monitor-flask.service"

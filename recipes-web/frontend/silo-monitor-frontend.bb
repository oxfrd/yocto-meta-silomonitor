DESCRIPTION = "A simple web frontend for showing silo monitoring data"
PN = "silo-monitor-frontend"
LICENSE = "CLOSED"

SRC_URI = "file://silo-img.png"
SRC_URI += "file://index.html"
SRC_URI += "file://silo-monitor-webserver.service"

inherit systemd

SYSTEMD_SERVICE:${PN} = "silo-monitor-webserver.service"
SYSTEMD_AUTO_ENABLE = "enable"

do_install() {
    install -d ${D}${localstatedir}/www/html
    install -m 0644 ${WORKDIR}/index.html ${D}${localstatedir}/www/html/
    install -m 0644 ${WORKDIR}/silo-img.png ${D}${localstatedir}/www/html/

    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${WORKDIR}/silo-monitor-webserver.service ${D}${systemd_system_unitdir}/
}

FILES:${PN} += "${localstatedir}/www/html/index.html \ 
                ${localstatedir}/www/html/silo-img.png \
                ${systemd_system_unitdir}/silo-monitor-webserver.service"

RDEPENDS:${PN} += "python3-core python3-misc bash"


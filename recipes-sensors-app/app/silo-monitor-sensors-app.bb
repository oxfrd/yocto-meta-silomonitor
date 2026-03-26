PN = "silo-monitor-sensors-app"
SUMMARY = "Silo Monitor Sensors Application"
DESCRIPTION = "Real-time sensors monitoring application for silo-monitor"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

PV = "0.1.0+git"
SRCREV = "master"

SRC_URI = "git://github.com/oxfrd/silo-sensors-app;protocol=https;branch=master \
           file://silo-monitor-sensors-app.service"

S = "${WORKDIR}/git"

# Build dependencies
DEPENDS += " cmake-native jsoncpp"

# Runtime dependencies (if exists)
# RDEPENDS:${PN} += "..."

# CMake options
# EXTRA_OECMAKE = "-DCMAKE_BUILD_TYPE=Release"

# Inherit recipe class dla CMake
inherit cmake systemd

SYSTEMD_SERVICE:${PN} = "silo-monitor-sensors-app.service"
SYSTEMD_AUTO_ENABLE:${PN} = "enable"

do_install() {
    # Install binary
    install -d ${D}${bindir}    
    install -m 0755 ${B}/silo-monitor-sensors-app ${D}${bindir}/
    
    # Install systemd service file
    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${WORKDIR}/silo-monitor-sensors-app.service ${D}${systemd_system_unitdir}/
}
SUMMARY = "1-Wire config for RPi"
LICENSE = "CLOSED"

SRC_URI = "file://config.txt"

RPROVIDES:${PN} += "rpi-config"

do_install() {
    install -d ${D}/boot
    install -m 0644 ${WORKDIR}/config.txt ${D}/boot/99-w1-gpio.txt
}

FILES:${PN} += "/boot/99-w1-gpio.txt"

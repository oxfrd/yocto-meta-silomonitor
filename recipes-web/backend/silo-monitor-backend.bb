SUMMARY = "Backend in flask REST API for silo monitoring"
PN = "silo-monitor-backend"
LICENSE = "CLOSED"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/CC0-1.0;md5=..."

SRC_URI = "file://flask-main.py \
           file://sensors.py \
           file://dataReceiver.py \
           file://silo-monitor-flask.service \
           git://github.com/oxfrd/silo-sensors-proto-msg;protocol=https;branch=master;name=proto;destsuffix=proto-src"

SRCREV_proto = "${AUTOREV}"

DEPENDS += "protobuf-native"
RDEPENDS:${PN} += "python3-core python3-json python3-flask python3-protobuf"

inherit systemd

SYSTEMD_SERVICE:${PN} = "silo-monitor-flask.service"
SYSTEMD_AUTO_ENABLE = "enable"

do_compile() {
    install -d ${B}/proto_out

    proto_src_dir=${WORKDIR}/proto-src
    proto_files=$(find "${proto_src_dir}" -type f -name '*.proto' | sort)

    if [ -z "${proto_files}" ]; then
        bbfatal "Nie znaleziono żadnych plików .proto w repozytorium protobuf"
    fi

    proto_dir=$(dirname $(echo "${proto_files}" | head -n 1))
    for proto_file in ${proto_files}; do
        protoc --proto_path="${proto_dir}" --python_out="${B}/proto_out" "${proto_file}"
    done

    if [ ! -f ${B}/proto_out/snapshot_pb2.py ]; then
        bbfatal "Nie wygenerowano snapshot_pb2.py"
    fi
}

do_install() {
    install -d ${D}${localstatedir}/lib/silo-monitor-flask
    install -m 0644 ${WORKDIR}/flask-main.py ${D}${localstatedir}/lib/silo-monitor-flask/
    install -m 0644 ${WORKDIR}/sensors.py ${D}${localstatedir}/lib/silo-monitor-flask/
    install -m 0644 ${WORKDIR}/dataReceiver.py ${D}${localstatedir}/lib/silo-monitor-flask/
    install -m 0644 ${B}/proto_out/snapshot_pb2.py ${D}${localstatedir}/lib/silo-monitor-flask/

    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${WORKDIR}/silo-monitor-flask.service ${D}${systemd_system_unitdir}/
}

FILES:${PN} += " ${localstatedir}/lib/silo-monitor-flask/* \
                 ${systemd_system_unitdir}/silo-monitor-flask.service"

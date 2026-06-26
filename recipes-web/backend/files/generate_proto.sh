#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROTO_OUT_DIR="${ROOT_DIR}/proto_gen"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

if [ -z "${VIRTUAL_ENV:-}" ]; then
    echo "Uruchom skrypt po aktywacji venv: source .venv/bin/activate" >&2
    exit 1
fi

PYTHON_BIN="${VIRTUAL_ENV}/bin/python"

if ! command -v git >/dev/null 2>&1; then
    echo "Brak git w PATH" >&2
    exit 1
fi

if ! command -v protoc >/dev/null 2>&1; then
    echo "Brak protoc w PATH. Zainstaluj protobuf-compiler." >&2
    exit 1
fi

if ! "${PYTHON_BIN}" -c 'import google.protobuf' >/dev/null 2>&1; then
    echo "Brak google.protobuf w aktywnym venv. Zainstaluj protobuf." >&2
    exit 1
fi

echo "Pobieram definicję protobuf z GitHub..."
REPO_URL="https://github.com/oxfrd/silo-sensors-proto-msg.git"
BRANCH="master"

rm -rf "${PROTO_OUT_DIR}"
mkdir -p "${PROTO_OUT_DIR}"

cd "${TMP_DIR}"
git clone --depth 1 --branch "${BRANCH}" "${REPO_URL}" repo >/dev/null 2>&1

PROTO_FILES="$(find "${TMP_DIR}/repo" -type f -name '*.proto' | sort)"
if [ -z "${PROTO_FILES}" ]; then
    echo "Nie znaleziono żadnych plików .proto w repozytorium" >&2
    exit 1
fi

PROTO_DIR="$(dirname $(echo "${PROTO_FILES}" | head -n 1))"
for proto_file in ${PROTO_FILES}; do
    protoc --proto_path="${PROTO_DIR}" --python_out="${PROTO_OUT_DIR}" "${proto_file}"
done

find "${PROTO_OUT_DIR}" -maxdepth 1 -type f -name '*_pb2.py' -exec cp {} "${ROOT_DIR}/" \;

echo "Gotowe. Wygenerowano:"
find "${ROOT_DIR}" -maxdepth 1 -type f -name '*_pb2.py' | sort

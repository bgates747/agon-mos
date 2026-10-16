PYTHON ?= .venv/bin/python
MOS_AGONDEV_ROOT ?= .local/mos-agondev
AGONDEV_TOOLCHAIN ?= .local/agondev
REFERENCE_BIN ?=
BUILD_DIR ?=

.DEFAULT_GOAL := firmware-check
.PHONY: firmware-check baseline-check test api-check

api-check:
	"$(PYTHON)" "$(MOS_AGONDEV_ROOT)/scripts/generate_api_reservations.py" --source-root . --check

firmware-check: api-check
	"$(PYTHON)" "$(MOS_AGONDEV_ROOT)/projects/native-foundation/build.py" \
		--source-root . --toolchain "$(AGONDEV_TOOLCHAIN)" \
		$(if $(BUILD_DIR),--output "$(BUILD_DIR)")

baseline-check: api-check
	@test -n "$(REFERENCE_BIN)" || { echo 'Supply the pinned translated control as REFERENCE_BIN'; exit 1; }
	"$(PYTHON)" "$(MOS_AGONDEV_ROOT)/projects/native-foundation/build.py" \
		--source-root . --toolchain "$(AGONDEV_TOOLCHAIN)" \
		--reference-bin "$(REFERENCE_BIN)" \
		$(if $(BUILD_DIR),--output "$(BUILD_DIR)")

test:
	"$(PYTHON)" -m unittest discover -s tests -v

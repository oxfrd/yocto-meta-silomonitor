include recipes-core/images/core-image-base.bb

# Machine settings
MACHINE = "raspberrypi4-64"
COMPATIBLE_MACHINE = "raspberrypi4-64"
ENABLE_UART = "1"
RPI_USE_U_BOOT = "1"

# Add primary features
IMAGE_FEATURES:append = " dev-pkgs dbg-pkgs ssh-server-dropbear"
IMAGE_FEATURES:remove = " read-only-rootfs"

# Add packages from recipes
IMAGE_INSTALL:append = " iperf3 htop net-tools"

# Add debug features
IMAGE_FEATURES:append = " debug-tweaks tools-debug"
IMAGE_GEN_DEBUGFS = "1"
IMAGE_FSTYPES_DEBUGFS = "tar.bz2"


################################################################################################
#################### Application specific settings #############################################
################################################################################################ 

# Enable 1-wire support for the DS18B20 temperature sensor
ENABLE_W1 = "1"
IMAGE_INSTALL:append = " kernel-modules"
KERNEL_MODULE_AUTOLOAD += "w1-gpio w1-therm"
RPI_EXTRA_CONFIG:append = " \
dtoverlay=w1-gpio,gpiopin=4 \
"

DISTRO_FEATURES:append = " python3"
IMAGE_INSTALL:append = " python3-core python3-json python3-flask"

IMAGE_INSTALL:append = " silo-monitor-frontend silo-monitor-backend curl"
IMAGE_FEATURES:append = " ssh-server-dropbear"
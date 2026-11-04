"""Install dependencies for Debug and Release and configure the CMake project."""

from common import CONFIGURATIONS, IS_WINDOWS, conan_install, configure

if IS_WINDOWS:
    for configuration in CONFIGURATIONS:
        conan_install(configuration)
    configure("Debug")
else:
    for configuration in CONFIGURATIONS:
        conan_install(configuration)
        configure(configuration)

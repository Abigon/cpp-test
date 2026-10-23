"""Install dependencies for Debug and Release and configure the CMake project."""

from common import CONFIGURATIONS, conan_install, configure

for configuration in CONFIGURATIONS:
    conan_install(configuration)
configure()

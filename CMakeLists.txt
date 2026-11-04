cmake_minimum_required(VERSION 3.25)
project(CppCourse LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(nlohmann_json REQUIRED)

find_package(GTest REQUIRED)

enable_testing()

set_property(GLOBAL PROPERTY USE_FOLDERS ON)

# All binaries in one place regardless of the subproject: build/bin/<Config>/
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

include(cmake/CompilerWarnings.cmake)
include(cmake/Sanitizers.cmake)

add_subdirectory(src/App)

set_property(DIRECTORY PROPERTY VS_STARTUP_PROJECT App)

include(cmake/ClangFormat.cmake)
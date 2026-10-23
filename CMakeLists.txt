cmake_minimum_required(VERSION 3.25)
project(App LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(nlohmann_json REQUIRED)

add_executable(app src/main.cpp)

target_link_libraries(app PRIVATE nlohmann_json::nlohmann_json)

set_property(DIRECTORY PROPERTY VS_STARTUP_PROJECT app)
set_target_properties(app PROPERTIES VS_DEBUGGER_WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")

include(cmake/ClangFormat.cmake)
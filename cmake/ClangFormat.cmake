# Targets format and format-check: single code style via clang-format.
# clang-format ships with Visual Studio and is usually not in PATH,
# so besides PATH we look inside installed Visual Studio directories.

file(GLOB VS_LLVM_DIRS
    "C:/Program Files/Microsoft Visual Studio/*/*/VC/Tools/Llvm/bin"
    "C:/Program Files/Microsoft Visual Studio/*/*/VC/Tools/Llvm/x64/bin")

find_program(CLANG_FORMAT_EXE NAMES clang-format HINTS ${VS_LLVM_DIRS})

if(NOT CLANG_FORMAT_EXE)
    message(WARNING "clang-format not found: targets format and format-check are unavailable")
    return()
endif()

message(STATUS "clang-format: ${CLANG_FORMAT_EXE}")

file(GLOB_RECURSE FORMAT_SOURCES CONFIGURE_DEPENDS
    "${CMAKE_SOURCE_DIR}/src/*.cpp"
    "${CMAKE_SOURCE_DIR}/src/*.h")

add_custom_target(format
    COMMAND ${CLANG_FORMAT_EXE} -i ${FORMAT_SOURCES}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "clang-format: formatting sources")

add_custom_target(format-check
    COMMAND ${CLANG_FORMAT_EXE} --dry-run --Werror ${FORMAT_SOURCES}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "clang-format: checking style")
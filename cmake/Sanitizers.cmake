# AddressSanitizer support. Off by default: an instrumented build is slower
# and lives in its own build directory (see automation/run_asan.py).

option(ENABLE_ASAN "Build with AddressSanitizer (plus UBSan on GCC/Clang)" OFF)

if(ENABLE_ASAN AND MSVC)
    # CMake's default Debug flags include /RTC1 (runtime checks), which is
    # incompatible with ASan: the compiler refuses both at once.
    string(REPLACE "/RTC1" "" CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG}")
    # The ASan runtime is a DLL next to the compiler, not on PATH. Copy it
    # next to each instrumented executable so it runs from any console.
    get_filename_component(compiler_dir "${CMAKE_CXX_COMPILER}" DIRECTORY)
    set(ASAN_RUNTIME_DLL "${compiler_dir}/clang_rt.asan_dynamic-x86_64.dll")
    if(NOT EXISTS "${ASAN_RUNTIME_DLL}")
        message(FATAL_ERROR "AddressSanitizer runtime not found: ${ASAN_RUNTIME_DLL}. "
                            "Install the 'C++ AddressSanitizer' component in Visual Studio Installer.")
    endif()
endif()

function(enable_sanitizers target)
    if(NOT ENABLE_ASAN)
        return()
    endif()
    if(MSVC)
        target_compile_options(${target} PRIVATE /fsanitize=address)
        # gtest from Conan is built without ASan; the STL refuses to link
        # objects with different container-annotation settings (LNK2038),
        # so annotations are disabled to match the prebuilt libraries.
        target_compile_definitions(${target} PRIVATE _DISABLE_STL_ANNOTATION)
        # Incremental linking is not supported with ASan.
        target_link_options(${target} PRIVATE /INCREMENTAL:NO)

        get_target_property(type ${target} TYPE)
        if(type STREQUAL "EXECUTABLE")
            add_custom_command(TARGET ${target} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy_if_different
                        "${ASAN_RUNTIME_DLL}" "$<TARGET_FILE_DIR:${target}>"
                COMMENT "Copying AddressSanitizer runtime next to ${target}")
        endif()
    else()
        # UBSan reports and continues by default; make every finding fatal,
        # otherwise a test with undefined behaviour still passes.
        target_compile_options(${target} PRIVATE -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer)
        # GCC needs the flag at link time too: it pulls in the libasan/libubsan runtimes.
        target_link_options(${target} PRIVATE -fsanitize=address,undefined)
    endif()
endfunction()

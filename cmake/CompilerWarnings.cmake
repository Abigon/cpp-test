# set_project_warnings(<target>): strict warnings, treated as errors.
# A warning is the compiler finding a probable bug without being sure;
# with /WX (-Werror) it cannot be ignored and cannot pile up.

function(set_project_warnings target)
    if(MSVC)
        target_compile_options(${target} PRIVATE
            /W4            # warning level 4: everything reasonable
            /WX            # warnings are errors
            /permissive-   # standard-conforming mode: no MSVC-specific leniency
        )
    else()
        target_compile_options(${target} PRIVATE
            -Wall -Wextra -Wpedantic
            -Werror
        )
    endif()
endfunction()

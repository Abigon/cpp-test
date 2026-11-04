project(App LANGUAGES CXX)

# Application logic: a static library. Everything that can be tested lives here.
add_library(${PROJECT_NAME}Lib STATIC
    Config.cpp
    Config.h)
target_include_directories(${PROJECT_NAME}Lib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(${PROJECT_NAME}Lib PRIVATE nlohmann_json::nlohmann_json)

# Executable: only main.cpp, everything else comes from the library.
add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ${PROJECT_NAME}Lib)

set_target_properties(${PROJECT_NAME} ${PROJECT_NAME}Lib PROPERTIES FOLDER ${PROJECT_NAME})
set_target_properties(${PROJECT_NAME} PROPERTIES VS_DEBUGGER_WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")

# Tests: link the same library the app uses; gtest_main provides main().
add_executable(${PROJECT_NAME}TestRunner Tests/ConfigTest.cpp)
target_link_libraries(${PROJECT_NAME}TestRunner PRIVATE ${PROJECT_NAME}Lib GTest::gtest_main)
set_target_properties(${PROJECT_NAME}TestRunner PROPERTIES FOLDER ${PROJECT_NAME})

include(GoogleTest)
gtest_discover_tests(${PROJECT_NAME}TestRunner DISCOVERY_TIMEOUT 30)

set_project_warnings(${PROJECT_NAME}Lib)
set_project_warnings(${PROJECT_NAME})
set_project_warnings(${PROJECT_NAME}TestRunner)

enable_sanitizers(${PROJECT_NAME}Lib)
enable_sanitizers(${PROJECT_NAME})
enable_sanitizers(${PROJECT_NAME}TestRunner)
cmake_minimum_required(VERSION 3.25)
project(App LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(app src/main.cpp)
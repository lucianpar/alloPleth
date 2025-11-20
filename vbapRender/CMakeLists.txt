cmake_minimum_required(VERSION 3.12)
project(sonoPleth_vbap_render)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Disable unnecessary AlloLib features
set(ALLOLIB_BUILD_EXAMPLES OFF CACHE BOOL "Don't build AlloLib examples")
set(ALLOLIB_BUILD_TESTS OFF CACHE BOOL "Don't build AlloLib tests")
set(AL_VERBOSE_OUTPUT OFF CACHE BOOL "Disable verbose output")

add_subdirectory(
    ${CMAKE_CURRENT_SOURCE_DIR}/../thirdparty/allolib
    ${CMAKE_CURRENT_BINARY_DIR}/allolib-build
)

add_executable(sonoPleth_vbap_render
    src/main.cpp
    src/VBAPRenderer.cpp
    src/JSONLoader.cpp
    src/LayoutLoader.cpp
    src/WavUtils.cpp
)

# ONLY include the AlloLib "include" folder — NOT the root
target_include_directories(sonoPleth_vbap_render PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../thirdparty/allolib/include
)

target_link_libraries(sonoPleth_vbap_render
    al
    Gamma
)

cmake_minimum_required(VERSION 3.12)
project(sonoPleth_vbap_render)

# Add AlloLib (path relative to this CMakeLists)
add_subdirectory(
    ${CMAKE_CURRENT_SOURCE_DIR}/../thirdparty/allolib
    ${CMAKE_CURRENT_BINARY_DIR}/allolib-build
)

add_executable(sonoPleth_vbap_render
    src/main.cpp
    src/VBAPRenderer.cpp
    src/JSONLoader.cpp
)

target_include_directories(sonoPleth_vbap_render PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}../../thirdparty/allolib
    ${CMAKE_CURRENT_SOURCE_DIR}/../thirdparty/allolib/include
)

target_link_libraries(sonoPleth_vbap_render
    al
    Gamma
)

cmake_minimum_required(VERSION 3.12)
project(sonoPleth-vbap-render)

# Add AlloLib
add_subdirectory(../thirdparty/allolib ${CMAKE_BINARY_DIR}/allolib-build)

add_executable(sonoPleth-vbap-render
    src/main.cpp
    src/VBAPRenderer.cpp
    src/JSONLoader.cpp
)

target_include_directories(sonoPleth-vbapRender PRIVATE
    ../thirdparty/allolib
    ../thirdparty/allolib/include
)

target_link_libraries(sonoPleth-vbapRender
    allo
    Gamma
)

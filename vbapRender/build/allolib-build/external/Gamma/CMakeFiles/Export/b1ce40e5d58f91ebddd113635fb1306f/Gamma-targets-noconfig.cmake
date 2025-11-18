#----------------------------------------------------------------
# Generated CMake target import file.
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "Gamma" for configuration ""
set_property(TARGET Gamma APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(Gamma PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_NOCONFIG "CXX"
  IMPORTED_LINK_INTERFACE_LIBRARIES_NOCONFIG "/opt/homebrew/lib/libsndfile.dylib"
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/libGamma.a"
  )

list(APPEND _cmake_import_check_targets Gamma )
list(APPEND _cmake_import_check_files_for_Gamma "${_IMPORT_PREFIX}/lib/libGamma.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)

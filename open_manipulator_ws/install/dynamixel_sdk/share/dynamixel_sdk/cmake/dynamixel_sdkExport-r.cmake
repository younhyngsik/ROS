#----------------------------------------------------------------
# Generated CMake target import file for configuration "R".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "dynamixel_sdk::dynamixel_sdk" for configuration "R"
set_property(TARGET dynamixel_sdk::dynamixel_sdk APPEND PROPERTY IMPORTED_CONFIGURATIONS R)
set_target_properties(dynamixel_sdk::dynamixel_sdk PROPERTIES
  IMPORTED_LOCATION_R "${_IMPORT_PREFIX}/lib/libdynamixel_sdk.so"
  IMPORTED_SONAME_R "libdynamixel_sdk.so"
  )

list(APPEND _cmake_import_check_targets dynamixel_sdk::dynamixel_sdk )
list(APPEND _cmake_import_check_files_for_dynamixel_sdk::dynamixel_sdk "${_IMPORT_PREFIX}/lib/libdynamixel_sdk.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)

# CMakeList.txt : Top-level CMake project file, do global configuration
# and include sub-projects here.
#
cmake_minimum_required (VERSION 3.20)
# cmake_policy(SET CMP0144 NEW)
# cmake_policy(SET CMP0167 OLD)  # <-- Use OLD to enable FindBoost.cmake

# Enable Hot Reload for MSVC compilers if supported.
if (POLICY CMP0141)
  cmake_policy(SET CMP0141 NEW)
  set(CMAKE_MSVC_DEBUG_INFORMATION_FORMAT "$<IF:$<AND:$<C_COMPILER_ID:MSVC>,$<CXX_COMPILER_ID:MSVC>>,$<$<CONFIG:Debug,RelWithDebInfo>:EditAndContinue>,$<$<CONFIG:Debug,RelWithDebInfo>:ProgramDatabase>>")
endif()


project ("NumSimSolver" VERSION 0.0.1)

# Find MPI package
find_package(MPI REQUIRED)

# check if MPI was found
if(NOT MPI_FOUND)
  message(FATAL_ERROR "MPI not found!")
endif()

# Boost configuration
set(BOOST_ROOT "C:\\boost_1_89_0")
set(Boost_LIBRARYDIR_DIR "C:\\boost_1_89_0\\lib64-msvc-14.3")
set(Boost_NO_WARN_NEW_VERSIONS 1)
find_package(Boost 1.89.0 REQUIRED COMPONENTS context thread date_time program_options filesystem coroutine log_setup log)

# Check if Boost was found
if(NOT Boost_FOUND)
  message(FATAL_ERROR "Boost not found!")
endif()

# Link MPI libraries
link_libraries(MPI::MPI_CXX)

# Link Boost libraries
link_directories(${Boost_LIBRARY_DIRS})

# Include MPI headers
include_directories(${MPI_CXX_INCLUDE_DIRS})

# Include Boost headers
include_directories(${Boost_INCLUDE_DIRS})


set(CMAKE_INSTALL_PREFIX "${CMAKE_CURRENT_SOURCE_DIR}/../install" CACHE PATH "path to install NumSimSolver")
message(STATUS "CMAKE_INSTALL_PREFIX: ${CMAKE_INSTALL_PREFIX}")

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG "${CMAKE_CURRENT_SOURCE_DIR}/../install/Debug")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_DEBUG "${CMAKE_CURRENT_SOURCE_DIR}/../install/Debug")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_CURRENT_SOURCE_DIR}/../install/Release")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_RELEASE "${CMAKE_CURRENT_SOURCE_DIR}/../install/Release")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${CMAKE_CURRENT_SOURCE_DIR}/../install/RelWithDebInfo>")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_RELWITHDEBINFO "${CMAKE_CURRENT_SOURCE_DIR}/../install/RelWithDebInfo>")

# Include sub-projects.
add_subdirectory ("NumSimCore")
add_subdirectory ("NumSimMeshImport")
add_subdirectory ("NumSimMeshExport")
add_subdirectory ("NumSimSolver")
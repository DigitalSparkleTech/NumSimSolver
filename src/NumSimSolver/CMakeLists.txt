cmake_minimum_required(VERSION 3.20)
# cmake_policy(SET CMP0144 NEW)
# cmake_policy(SET CMP0167 OLD)  # <-- Use OLD to enable FindBoost.cmake

project(NumSimSolver)

# set(EXECUTABLE_OUTPUT_PATH ${CMAKE_CURRENT_SOURCE_DIR}/../install)

include_directories (
"${CMAKE_CURRENT_SOURCE_DIR}/../NumSimCore"
)

# Add source to this project's executable.
add_executable (NumSimSolver "main.cpp")

target_link_libraries(${PROJECT_NAME}
  NumSimCore
)

# TODO: Add tests and install targets if needed.
project(NumSimCore)

set(NUMSIMCORE_HEADER_FILES
"NumSimObject.h"
"NumSimFramework.h"
"NumSimComm.h"
"NumSimSimulation.h"
)

set(NUMSIMCORE_CPP_FILES
"NumSimObject.cpp"
"NumSimFramework.cpp"
"NumSimComm.cpp"
"NumSimSimulation.cpp"
)

set(EXECUTABLE_OUTPUT_PATH ${CMAKE_CURRENT_SOURCE_DIR}/../../install)

add_library(${PROJECT_NAME} SHARED
${NUMSIMCORE_HEADER_FILES}
${NUMSIMCORE_CPP_FILES}
README.md
)
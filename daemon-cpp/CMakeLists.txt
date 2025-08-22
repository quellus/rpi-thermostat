cmake_minimum_required(VERSION 3.20)

set(CMAKE_BUILD_TYPE Debug)

project(crow-restapi VERSION 0.0.1 LANGUAGES CXX)

enable_language(C)
enable_language(CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include(${CMAKE_SOURCE_DIR}/cmake/CPM.cmake)

option(${PROJECT_NAME}_ENABLE_TESTS "enable testing" OFF)

CPMAddPackage(Crow
  VERSION 1.2.0
  GITHUB_REPOSITORY CrowCpp/Crow
  OPTIONS
  "CROW_BUILD_EXAMPLES Off"
  "CROW_BUILD_TOOLS Off"
  "CROW_BUILD_TESTS Off"
  "CROW_BUILD_DOCS Off"
  "CROW_ENABLE_COMPRESSION On"
  "CROW_ENABLE_SSL On"
)

file(GLOB SOURCES "src/*.cpp")
add_executable(${PROJECT_NAME} ${SOURCES})
target_link_libraries(${PROJECT_NAME} PRIVATE Crow::Crow)


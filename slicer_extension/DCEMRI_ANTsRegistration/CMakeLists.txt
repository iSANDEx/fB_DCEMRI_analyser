cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(DCEMRI_ANTsRegistration)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/DCEMRI_ANTsRegistration")
set(EXTENSION_CATEGORY "Example")
set(EXTENSION_CONTRIBUTORS "Jose L. Ulloa (iSANDEx)")
set(EXTENSION_DESCRIPTION "Example of how to interact with other modules. This  simple" extension will register a pre-contrast image to a post-contrast phase from a single scan. Although both images can be from different folders, the idea is that both were acquired on a single session (i.e. re-position movement is minimum)""simple" extension will register a pre-contrast image to a post-contrast phase from a single scan. Although both images can be from different folders, the idea is that both were acquired on a single session (i.e. re-position movement is minimum)")
set(EXTENSION_ICONURL "https://www.example.com/Slicer/Extensions/DCEMRI_ANTsRegistration.png")
set(EXTENSION_SCREENSHOTURLS "https://www.example.com/Slicer/Extensions/DCEMRI_ANTsRegistration/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(DataLoader)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})

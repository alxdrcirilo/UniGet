# Creates a .qr file with the icons and converts it to a .py file which can be imported in the main .py program/script
# Then use, e.g. ":/Icons/sample.png"

# <RCC>
#   <qresource prefix="/" >
#     <file>img/image1.png</file>
#     <file>img/image2.png</file>
#     <file>img/image3.png</file>
#   </qresource>
# </RCC>

import os

file = open("imgs.qrc", "w")
path = "imgs"

to_write = "<RCC>\n"
to_write += """  <qresource prefix="/" >\n"""
for root, dirs, files in os.walk(path):
    for filename in files:
        print(root, filename, "... added!")
        to_write += "    <file>" + root + "/" + filename + "</file>\n"

# for root, dirs, files in os.walk("Data"):
#     for filename in files:
#         print(root, filename, "... added!")
#         to_write += "    <file>" + root + "/" + filename + "</file>\n"

to_write += "  </qresource>\n"
to_write += "</RCC>"

print(to_write)

file.write(to_write)
file.close()

import subprocess
subprocess.call("pyrcc5 {}.qrc -o {}.py".format(path, path))
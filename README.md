a simple command line tool to build your website

it minifies your files, compresses images and processes server-side includes

## usage

`>> froyo path/to/src/folder [path/to/dest/folder] [--watch]`

### arguments

postional

`source` - path to source folder
`dest` - path to destination folder, if blank it will default to `[source\]_dist` and it will be created if it does not exist

optional

`--watch` - will watch the source for changes

###configuration file
froyo now supports the use of config files that reduce the need for typing out command line arguments

create a file named `froyo.ini` in the source folder and copy these contents:
``` .ini
[SETTINGS]
destination=../[YOUR DESTINATION HERE]

[MINIFY]
js=False
html=True
css=True

[IMAGE]
compress=True
#maximum width and height default to 10000
max_width=10000
max_width=10000
```
####[SETTINGS]
`destination`: sets the outpt directory relative to the source
####[MINIFY]
`js`: set to `True` to minify js files but ending semicolons are necessary
`html`: set to `True` to minify html files
`css`: set to `True` to minify css files
####[IMAGE]
`compress`: set to `True` to compress
`max_width`: set the maximum with of output images in pixels
`max_height`: set the maximum height of output images in pixels
resized images maintain aspect ratio

### installation

#### PyPi

`pip install froyo`

#### GitHub

clone from github
`>> git clone https://github.com/kartikye/froyo.git`

navigate to the directory
`>> cd froyo`

run the install command
`>> python setup.py install`
Platform: UNKNOWN
Requires-Python: >=3 
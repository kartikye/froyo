import sys
import os
import shutil
import time 
from PIL import Image
from css_html_js_minify import html_minify, js_minify, css_minify
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

source_global = ''
dest_global = ''

debug = False
print_original = print
def print_new(*stuff, sep=' ', end='\n', file=sys.stdout, flush=False, override=False):
    if debug or override:
        print_original(*stuff, sep=sep, end=end, file=file, flush=flush)
print = print_new

class DirectoryUpdate(FileSystemEventHandler):
    def on_any_event(thing, event):
        print(event.event_type)
        print("working:", event.src_path, override=True)
        if event.event_type == 'deleted':
            print(event, dest_global)
            file = event.src_path[event.src_path.index(os.sep)+1:]
            if event.is_directory:
                try:
                    shutil.rmtree(os.path.join(dest_global,file))
                except Exception as e:
                    print(e)
            else:
                try:
                    os.remove(os.path.join(dest_global,file))
                except Exception as e:
                    print(e)
        else:
            try:
                process(source_global, dest_global)
            except Exception as e:
                print(e)


def process(source, dest, filetype='all'):

    html = True
    css = True
    js = True
    images = True
    other = True

    if filetype == 'html':
        css = False
        js = False
        images = False
        other = False

    if filetype == 'js':
        html = False
        css = False
        images = False
        other = False

    if filetype == 'css':
        html = False
        js = False
        images = False
        other = False

    if filetype == 'images':
        html = False
        css = False
        js = False
        other = False       

    for subdirs, dirs, files in os.walk(source):
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for file in files:
            filepath = os.path.join(subdirs, file)
            if file.endswith('html'):
                process_html(filepath, source, dest)
            elif not file.startswith('.'):
                cp_dest = os.path.join(dest, filepath[len(source)+1:])
                copy_file(filepath, cp_dest)
    print("done")

def process_html(filepath, source, dest):
    with open(filepath, 'r+', encoding="utf-8") as file:
        changes = []
        lines = file.readlines()
        for line in range(len(lines)):
            if '<!--#include' in lines[line]:
                line_to_replace = line
                replacewith = lines[line].split(' ')[1].split('"')[1]
                changes.append((line_to_replace, replacewith))
        for line, change in changes[::-1]:
            with open(os.path.join(source,change), 'r', encoding="utf-8") as change:
                change = change.readlines()
                lines = lines[0: line] + change + lines[line+1:]
        
        dest = os.path.join(dest, filepath[len(source)+1:])
        new_file = html_minify(''.join(lines))
        save_file(new_file, dest)

def process_css(filepath, source, dest):
    with open(filepath, 'r+', encoding='utf-8') as css:
        lines = css.readlines()
        dest = os.path.join(dest, filepath[len(source)+1:])
        new_file = css_minify(''.join(lines))
        save_file(new_file, dest)

def process_js(filepath, source, dest):
    with open(filepath, 'r+', encoding='utf-8') as js:
        lines = js.readlines()
        dest = os.path.join(dest, filepath[len(source)+1:])
        new_file = js_minify(''.join(lines))
        save_file(new_file, dest)

def process_image(filepath, source, dest):
    image = Image.open(filepath)
    dest = os.path.join(dest, filepath[len(source)+1:])
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    image.save(dest, optimize=True, quality=90)

def copy_file(file, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    shutil.copyfile(file, path)

def save_file(file, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w+', encoding='utf-8') as dest_file:
        dest_file.write(file)

def main():
    print("froyo is starting", override=True)
    global source_global, dest_global
    if len(sys.argv) < 3:
        print("please run the following: froyo <SOURCE DIR> <DEST DIR>", override=True)
        exit()
    source = sys.argv[1]
    if len(sys.argv) > 2:
        dest = sys.argv[2]
    else:
        dest = None

    cwd = os.getcwd()

    source_global = os.path.join(cwd, source)

    if not os.path.isdir(source_global):
        print('source dir does not exist', override=True)
        exit()

    dest_global = os.path.join(cwd, dest)
    
    if not os.path.isdir(dest_global):    
        print('dest dir does not exist', override=True)
        exit()

    process(source_global, dest_global)

    event_handler = DirectoryUpdate()

    observer = Observer()
    observer.schedule(event_handler, source, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
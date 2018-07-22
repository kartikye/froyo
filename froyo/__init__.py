import sys
import os
import shutil
import time 
from PIL import Image
from css_html_js_minify import html_minify, js_minify, css_minify
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import argparse
import configparser

source_global = ''
dest_global = ''

debug = True
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


def process(source, dest, config):

    for subdirs, dirs, files in os.walk(source):
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for file in files:
            filepath = os.path.join(subdirs, file)
            if file.endswith('.html'):
                process_html(filepath, source, dest, config)
            elif file.endswith('.css') and not file.endswith('.scss'):
                process_css(filepath, source, dest, config)
            elif file.endswith('.js'):
                process_js(filepath, source, dest, config)
            elif file.endswith(('.jpg', '.png', '.gif', '.bmp', '.tiff', '.jpeg')):
                process_image(filepath, source, dest, config)
            elif file.startswith('.') or file.endswith(('.scss', '.psd')):
                pass
            else:
                cp_dest = os.path.join(dest, filepath[len(source)+1:])
                copy_file(filepath, cp_dest)
                print(filepath)
    print("done")

def process_html(filepath, source, dest, config):
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

        new_file = '\n'.join(lines)
        if config['MINIFY']['html'] == 'True':
            new_file = html_minify(new_file)
        save_file(new_file, dest)

def process_css(filepath, source, dest, config):
    with open(filepath, 'r+', encoding='utf-8') as css:
        lines = css.readlines()
        dest = os.path.join(dest, filepath[len(source)+1:])
        new_file = '\n'.join(lines)
        if config['MINIFY']['css'] == 'True':
            new_file = css_minify(new_file)
        save_file(new_file, dest)

def process_js(filepath, source, dest, config):
    with open(filepath, 'r+', encoding='utf-8') as js:
        lines = js.readlines()
        dest = os.path.join(dest, filepath[len(source)+1:])
        new_file = '\n'.join(lines)
        if config['MINIFY']['js'] == 'True':
            new_file = js_minify(new_file)
        save_file(new_file, dest)

def process_image(filepath, source, dest, config):
    image = Image.open(filepath)
    dest = os.path.join(dest, filepath[len(source)+1:])
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if 'max_width' or 'max_height' in config['IMAGE']:
        if 'max_width' in config['IMAGE']:
            max_width = int(config['IMAGE']['max_width'])
        else:
            max_width = 10000
        if 'max_height' in config['IMAGE']:
            max_height = int(config['IMAGE']['max_height'])
        else:
            max_height = 10000
        image.thumbnail((max_width, max_height), Image.ANTIALIAS)
    if config['IMAGE']['compress'] == 'True':
        image.save(dest, optimize=True, quality=80)
    else:
        image.save(dest)

def copy_file(file, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    shutil.copyfile(file, path)

def save_file(file, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w+', encoding='utf-8') as dest_file:
        dest_file.write(file)

def clean_directory_name(directory):
    if directory.endswith('\\') or directory.endswith('/'):
        directory = directory[:-1]
    if directory.startswith('./') or directory.startswith('.\\'):
        directory = directory[2:]
    return directory

def main():    
    parser = argparse.ArgumentParser(description='froyo - site distributor')

    parser.add_argument('source', action="store")
    parser.add_argument('dest', action="store", nargs='?')
    parser.add_argument('--watch', action="store_true", dest="watch", default=False)

    args = parser.parse_args()

    print(args.dest)

    source = clean_directory_name(args.source)
    
    if args.dest:
        dest = clean_directory_name(args.dest)
    else:
        dest = source + '_dist'

    cwd = os.getcwd()

    global source_global, dest_global, config

    source_global = os.path.join(cwd, source)

    if not os.path.isdir(source_global):
        print('source dir does not exist', override=True)
        exit()

    config = False

    if os.path.isfile(source_global+'/froyo.ini'):
        config = configparser.ConfigParser()
        config.read(source_global+'/froyo.ini')

    if config:
        if 'destination' in config['SETTINGS']:
            dest_global = os.path.join(source_global, config['SETTINGS']['destination'])
    else:
        dest_global = os.path.join(cwd, dest)
    
    if not os.path.isdir(dest_global):    
        os.makedirs(dest_global)

    process(source_global, dest_global, config)

    if args.watch:
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
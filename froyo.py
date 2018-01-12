import sys
import os
import shutil
from PIL import Image

def process(source, dest):
    cwd = os.getcwd()

    source = os.path.join(cwd, source)

    assert os.path.isdir(source)

    if not dest:
        #create destination
        pass
    else:
        dest = os.path.join(cwd, dest)
        assert os.path.isdir(dest) 

    for subdirs, dirs, files in os.walk(source):
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for file in files:
            print(file)
            filepath = os.path.join(subdirs, file)
            if file.endswith('html'):
                process_html(filepath, source, dest)
            elif file.endswith('.css'):
                process_css(filepath, source, dest)
            elif file.endswith('.js'):
                process_js(filepath, source, dest)
            elif file.endswith('.png') or file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.JPG') or file.endswith('JPEG'):
                process_image(filepath, source, dest) 
            elif not file.startswith('.'):
                cp_dest = os.path.join(dest, filepath[len(source)+1:])
                copy_file(filepath, cp_dest)

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
        new_file = minify_file(lines)
        save_file(new_file, dest)

def process_css(filepath, source, dest):
    with open(filepath, 'r+', encoding='utf-8') as css:
        lines = css.readlines()
        dest = os.path.join(dest, filepath[len(source)+1:])
        new_file = minify_file(lines, True)
        save_file(new_file, dest)

def process_js(filepath, source, dest):
    with open(filepath, 'r+', encoding='utf-8') as js:
        lines = js.readlines()
        dest = os.path.join(dest, filepath[len(source)+1:])
        new_file = minify_file(lines)
        save_file(new_file, dest)

def process_image(filepath, source, dest):
    image = Image.open(filepath)
    dest = os.path.join(dest, filepath[len(source)+1:])
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    image.save(dest, optimize=True, quality=90)

def minify_file(file, remove_spaces=False):
    file = ''.join(file).replace('\t','').replace('\n', '') 
    if remove_spaces:
        file = file.replace(' ', '')
    return file

def copy_file(file, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    shutil.copyfile(file, path)

def save_file(file, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w+', encoding='utf-8') as dest_file:
        dest_file.write(file)


if __name__ == '__main__':
    assert len(sys.argv) > 1
    source = sys.argv[1]
    if len(sys.argv) > 2:
        dest = sys.argv[2]
    else:
        dest = None

    process(source, dest)
import sys
import os
import shutil

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
        for file in files:
            filepath = os.path.join(subdirs, file)
            if file.endswith('html'):
                process_file(filepath, source, dest)
            else:
                cp_dest = os.path.join(dest, filepath[len(source)+1:])
                os.makedirs(os.path.dirname(cp_dest), exist_ok=True)
                shutil.copyfile(filepath, cp_dest)


def process_file(filepath, source, dest):
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
        
        print("####################################################")
        print(dest)
        print("####################################################")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, 'w+', encoding='utf-8') as dest_file:
            dest_file.writelines(lines)



if __name__ == '__main__':
    assert len(sys.argv) > 1
    source = sys.argv[1]
    if len(sys.argv) > 2:
        dest = sys.argv[2]
    else:
        dest = None

    process(source, dest)
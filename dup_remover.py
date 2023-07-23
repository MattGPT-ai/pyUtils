# dup_remover.py
import os
import sys
import hashlib
from collections import defaultdict


del_json = False  # was for pdf / json LabelImg stuff

# human-readable format
def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def walklevel(some_dir, level=1):
    """like walk with maximum level of recursion to walk. 
    set level=None for full recursion"""
    if level is None:
        return os.walk(some_dir)
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]

            
def findDup(parentFolder, level=1):
    # Dups in format {hash:[names]}
    dups = {}
    for dirName, subdirs, fileList in walklevel(parentFolder, level): ## for restricting level
        
        print('Scanning %s...' % dirName)
        for filename in fileList:
            # Get the path to the file
            path = os.path.join(dirName, filename)
            # Calculate hash
            #if os.splitext(path)[1] == '.pdf':
            try:
                file_hash = hashfile(path)
            except IOError:
                print("No permission for ", path)
                continue
            # Add or append the file path
            if file_hash in dups:
                dups[file_hash].append(path)
            else:
                dups[file_hash] = [path]
    
    return dups
 
 
# Joins two dictionaries
def joinDicts(dict1, dict2):
    for key in dict2.keys():
        if key in dict1:
            dict1[key] = dict1[key] + dict2[key]
        else:
            dict1[key] = dict2[key]
 
 
def hashfile(path, blocksize=65536):
    afile = open(path, 'rb')
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()
 
 
def printResults(dict1, prompt=False):
    results = list(filter(lambda x: len(x) > 1, dict1.values()))
    if len(results) > 0:
        print('Duplicates Found:')
        print('The following files are identical. The name could differ, but the content is identical')
        print('___________________')
        for result in results:
            for i, subresult in enumerate(result):
                print('{0}\t\t{1}'.format(i+1,subresult))
            print(sizeof_fmt(os.path.getsize(result[0])))
            print('___________________')
            if prompt:
                num = input('which copy to keep?  press 0 to keep all  ')
                if num != "" and num.isdigit() and int(num) != 0:
                    for i, subresult in enumerate(result):
                        print(i+1, num)
                        if i+1 != int(num):
                            print('deleting ', subresult)
                            os.remove(subresult)
                            if del_json:
                                json_file = subresult.replace('input_image', 'ocr_output').replace('.pdf', '.json')
                                if os.path.isfile(json_file):
                                    print('also deleting', json_file)
                                    os.remove(json_file)
                                else:
                                    print('missing json file', json_file)
                                print()
            
    else:
        print('No duplicate files found.')
 

def compare_contents(dir1, dir2, direction='both'):
    """find files present in one directory but not the other"""

    file_hashes1 = defaultdict()
    file_hashes2 = defaultdict()

        
    
 
if __name__ == '__main__':
    # check for options
    prompt = False
    for arg in sys.argv:
        if arg == '-p':
            prompt = True
            sys.argv.remove(arg)
    if len(sys.argv) > 1:
        dups = {}
        folders = sys.argv[1:]
        for i in folders:
            # Iterate the folders given
            if os.path.exists(i):
                # Find the duplicated files and append them to the dups
                joinDicts(dups, findDup(i, level=3))
            else:
                print('%s is not a valid path, please verify' % i)
                sys.exit()
        printResults(dups, prompt)
    else:
        print('Usage: python dupFinder.py folder or python dupFinder.py folder1 folder2 folder3')
        

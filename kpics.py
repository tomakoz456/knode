# -*- coding: utf-8 -*-
import cv2
import os
import glob
import pathlib
import hashlib
import numpy as np
import sys
# import matplotlib.pyplot as plt


_max_width = 1200
_max_height = 900

def show(title, image):
    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def resize(image):
    image_width, image_height = image.shape[:2]

    if image_width > _max_width or image_height > _max_height:
        proportion = image_width / image_height
        return cv2.resize(image, (_max_width, _max_height))

def md5(str):
    return hashlib.md5(str).hexdigest()

def scan_dir(_photos_dir_path):
    _photos = []
    _photo_list = {}
    try:
    # if not os.path.isdir(_photos_dir_path):
        
        print("Star scanning photos directory in: %s" % _photos_dir_path)
        for root, sub_folder, files in os.walk(_photos_dir_path):
            
            if '_files' not in root:

                print("root: %s" % root)
                
                # if len(sub_folder) > 0:
                #     for folder in sub_folder:
                #         folder_full_path = os.path.join(root, folder)
                #         print("fullpath: %s" % folder_full_path)
                
                if len(files) > 0:
                    for _file in files:
                        _file_name = _file.endswith(_file)
                        _extension = pathlib.Path(_file).suffix
                        if(_extension in ('.jpg', '.jpeg', '.png')):
                            _full_path = os.path.join(root, _file)
                            print("Full path: %s" % _full_path)
                            _photos.append(_full_path)
                            _photo_list[len(_photo_list)] = _full_path

        return _photo_list
    except IOError:
        print('IO Error')
    except:
        print("Unexpected error:", sys.exc_info()[0])


def thumb(_photo_path):
    _thumb_dir = r'C:\Users\kogut\Documents\.kpics'
    


if __name__ == '__main__':
    _photos_dir_path = r'K:\trainman\fb'
    # _photos_dir_path = r'C:\Users\kogut\Desktop\piec'
    _thumb_dir = r'C:\Users\kogut\Documents\.kpics'
    _thumb_height = 153
    _photos = scan_dir(_photos_dir_path)
    # print("md5: %s is a %s" % (hashlib.md5("%s" % _photos[len(_photos)-1].encode()).hexdigest(), _photos[len(_photos)-1]))
    # _path = _photos[len(_photos)-1]
    # print(_path)
    _html = ''
    _thumb_dir_name = hashlib.md5(_photos_dir_path.encode()).hexdigest()
    _thumb_dir_path = os.path.join(_thumb_dir, _thumb_dir_name)
    id = 0
    if not os.path.isdir(_thumb_dir_path):
        os.mkdir(_thumb_dir_path)
        print("Create dir for thumb files in: %s" % _thumb_dir_path)

    for _photo_id in _photos:
        # if _photo_id is 10:
            # break
        _path = _photos[_photo_id]
        _thumb_name = "%s.%s" % (hashlib.md5(_path.encode()).hexdigest(), _path.split('.')[-1])
        # _thumb_path = os.path.join(_thumb_dir_path, _thumb_name)
        _thumb_full_path = os.path.join(_thumb_dir_path, _thumb_name)
        if os.path.isfile(_path): # and not os.path.isfile(_thumb_full_path):
            if not os.path.isfile(_thumb_full_path): # check if 
                photo = cv2.imread(_path)
                if photo is None:
                    print("Ignoring wrong photo file: %s" % _path)
                    continue
                print("photo shape for: %s" % _path)
                photo_height, photo_width = photo.shape[:2]

                # proportion = photo_width / photo_height
                thumb_height = _thumb_height

                # scale = photo_height / thumb_height
                # thumb_width = int(photo_width / scale) 
                # if photo_height > photo_width:
                #     thumb_width = photo_width / scale
                # elif photo_height < photo_width:
                #     thumb_width = photo_width / scale
                # else:
                #     thumb_width = photo_width / scale
                thumb_width = int((thumb_height * photo_width) / photo_height)
                # if (thumb_width / thumb_height) is not proportion:
                    # print("wrong photo dimmension for file: %s => %s" % (_path, proportion))
                _thumb = cv2.resize(photo, (int(thumb_width), int(thumb_height)), thumb_width/photo_width, thumb_height/photo_height)
                cv2.imwrite(_thumb_full_path, _thumb)
            else:
                print("Thumb file already exists: %s" % _thumb_full_path)
                thumb = cv2.imread(_thumb_full_path)
                thumb_height, thumb_width = thumb.shape[:2]
            _html += '<a id="photo-' + str(id) + '" href="' + _path + '" class="thumb" title="' + os.path.basename(_path) + ' in ' + os.path.dirname(_path) + '">'
            _html += '<img src="' + _thumb_full_path + '" alt="'+ os.path.basename(_thumb_full_path) + '" width="'+ str(thumb_width) +'" height="'+ str(thumb_height) + '"/>'
            _html += '</a>'
            id += 1
            # print(_thumb_full_path)

_html_name = 'index.html'
_html_path = os.path.join(_thumb_dir_path, _html_name)

_template_head_path = r'Y:\dev\topik-1\template\kpics\head_index.html'
_template_end_path = r'Y:\dev\topik-1\template\kpics\end_index.html'
_css = r'Y:\dev\topik-1\template\kpics\index.css'
html = ''

_template = ''
with open(_template_head_path) as f:
    lines = f.readlines()
    for line in lines:
        _template += line
    # html += lines.splitlines()

_template_footer = ''
with open(_template_end_path) as f:
    lines = f.readlines()
    for line in lines:
        _template_footer += line
    
with open(_html_path, 'w') as f:
    f.writelines(_template)
    f.writelines(_html)
    f.writelines(_template_footer)
# print(_template)
# html += _html


# html += _template.splitlines()
# _html = html
# with open(_html_path, 'w') as f:
#     f.writelines(_html)

import shutil
css_path = os.path.join(_thumb_dir_path, os.path.basename(_css))
if not os.path.isfile(css_path) or os.path.getsize(css_path) != os.path.getsize(_css):
    shutil.copy2(_css, css_path)
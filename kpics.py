# -*- coding: utf-8 -*-
import cv2
import os
import glob
import pathlib
import hashlib
import numpy as np
import sys
import shutil
# import time
# import datetime
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
    print(_photos_dir_path)
    try:
    # if not os.path.isdir(_photos_dir_path):
        if type(_photos_dir_path) is not dict:
            _photos_dir_path = [_photos_dir_path]
        for _photos_dir in _photos_dir_path.values():
            print("Star scanning photos directory in: %s" % _photos_dir)
            for root, sub_folder, files in os.walk(_photos_dir):        
                if '_files' not in root:
                    print("root: %s" % root)
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
    

class KpicsProcessor:
    def __init__(self, photos_dir_path, thumb_dir, thumb_height=153):
        self.init_dir = os.getcwd()
        # if type(photos_dir_path) is not dict:
        #     raise ValueError("photos_dir_path must be a dictionary with photo dir IDs as keys and paths as values.")
        self.photos_dir_path = photos_dir_path
        self.thumb_dir = thumb_dir
        self.thumb_height = thumb_height
        self.photos = scan_dir(self.photos_dir_path)
        self.thumb_dir_name = hashlib.md5(list(self.photos_dir_path.values())[0].encode()).hexdigest()
        self.thumb_dir_path = os.path.join(self.thumb_dir, self.thumb_dir_name)
        self.html = ''
        self.ensure_thumb_dir()

    def ensure_thumb_dir(self):
        if not os.path.isdir(self.thumb_dir_path):
            os.mkdir(self.thumb_dir_path)
            print("Create dir for thumb files in: %s" % self.thumb_dir_path)

    def process_photos(self):
        id = 0
        for photo_id in self.photos:
            path = self.photos[photo_id]
            thumb_name = "%s.%s" % (hashlib.md5(path.encode()).hexdigest(), path.split('.')[-1])
            thumb_full_path = os.path.join(self.thumb_dir_path, thumb_name)
            if os.path.isfile(path):
                if not os.path.isfile(thumb_full_path):
                    os.chdir(os.path.dirname(path))
                    photo = cv2.imread(os.path.basename(path))
                    if photo is None:
                        print("Ignoring wrong photo file: %s" % path)
                        continue
                    print("photo shape for: %s" % path)
                    photo_height, photo_width = photo.shape[:2]
                    thumb_height = self.thumb_height
                    thumb_width = int((thumb_height * photo_width) / photo_height)
                    thumb = cv2.resize(photo, (int(thumb_width), int(thumb_height)), thumb_width/photo_width, thumb_height/photo_height)
                    cv2.imwrite(thumb_full_path, thumb)
                else:
                    print("Thumb file already exists: %s" % thumb_full_path)
                    os.chdir(os.path.dirname(thumb_full_path))
                    thumb = cv2.imread(os.path.basename(thumb_full_path))
                    thumb_height, thumb_width = thumb.shape[:2]
                self.html += '<a id="photo-' + str(id) + '" href="' + path + '" class="thumb" title="' + os.path.basename(path) + ' in ' + os.path.dirname(path) + '">'
                self.html += '<img src="' + thumb_full_path + '" alt="'+ os.path.basename(thumb_full_path) + '" width="'+ str(thumb_width) +'" height="'+ str(thumb_height) + '"/>'
                self.html += '</a>'
                id += 1
                os.chdir(self.init_dir)

    def generate_html(self, html_name='index.html'):
        html_path = os.path.join(self.thumb_dir_path, html_name)
        # template_dir = os.path.dirname(html_path)
        template_dir = r'Y:\dev\kpics\template\kpics'
        if not os.path.isdir(template_dir):
            template_head_path = r'Y:\dev\topik-1\template\kpics\head_index.html'
            template_end_path = r'Y:\dev\topik-1\template\kpics\end_index.html'
            css = r'Y:\dev\topik-1\template\kpics\index.css'
        else:
            template_head_path = os.path.join(template_dir, 'head_index.html')
            template_end_path = os.path.join(template_dir, 'end_index.html')
            css = os.path.join(template_dir, 'index.css')
        if not os.path.isfile(template_head_path) or not os.path.isfile(template_end_path):
            raise FileNotFoundError("Template files not found in: %s" % template_dir)
        
        template = ''
        with open(template_head_path) as f:
            lines = f.readlines()
            for line in lines:
                template += line

        template_footer = ''
        with open(template_end_path) as f:
            lines = f.readlines()
            for line in lines:
                template_footer += line

        with open(html_path, 'w') as f:
            f.writelines(template)
            f.writelines(self.html)
            f.writelines(template_footer)

        css_path = os.path.join(self.thumb_dir_path, os.path.basename(css))
        if not os.path.isfile(css_path) or os.path.getsize(css_path) != os.path.getsize(css):
            shutil.copy2(css, css_path)


if __name__ == '__main__':
    photos_dir_dict = {0: r'K:\trainman\fb'}
    photos_dir_dict[1] = r'Y:\Pictures\instagram'
    processor = KpicsProcessor(
        photos_dir_path=photos_dir_dict,
        thumb_dir=r'C:\Users\kogut\Documents\.kpics',
        thumb_height=153
    )
    processor.process_photos()
    _html = processor.html
    _thumb_dir_path = processor.thumb_dir_path

    processor.generate_html()
    print("HTML generated in: %s" % _thumb_dir_path)
    # show("Thumb", thumb)
    # print(_html)
    # print(_thumb_dir_path)
    print("Photos processed: %d" % len(processor.photos))
    print("Thumbs generated: %d" % len(processor.html))
    # print("Thumbs dir: %s" % processor.thumb_dir_path)
    # print("Thumbs dir name: %s" % processor.thumb_dir_name)
    # print("Photos dir path: %s" % processor.photos_dir_path)
    # print("Photos dir: %s" % photos_dir_dict)


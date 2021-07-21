"""
Copyright (C) 2021 Abraham George Smith

This file contains code modified from RootPainter (C) Abraham George Smith
See modified/copied code in:
https://github.com/Abe404/root_painter/blob/db6dd3ec80a251903b7c2c2b68498e9e5cd128ac/painter/src/main/python/create_dataset.py

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow

import sys
import os
import argparse
import numpy as np
from skimage.io import imread, imsave
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import random
from pathlib import Path
import glob


def all_image_paths_in_dir(dir_path):
    root_dir = os.path.abspath(dir_path)
    all_paths = glob.iglob(root_dir + '/**/*', recursive=True)
    image_paths = []
    for p in all_paths:
        name = os.path.basename(p)
        if name[0] != '.':
            ext = os.path.splitext(name)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.tif', '.tiff']:
                image_paths.append(p)
    return image_paths
    
def get_dupes(a):
    seen = {}
    dupes = []
    for x in a:
        if x not in seen:
            seen[x] = 1
        else:
            if seen[x] == 1:
                dupes.append(x)
            seen[x] += 1
    return dupes, seen



def get_file_pieces(im, horizontal_tiles, vertical_tiles):
    im_h = im.shape[0]
    im_w = im.shape[1]

    # get the width and height of the proposed piece
    piece_w = im_w // horizontal_tiles
    piece_h = im_h // vertical_tiles
    postfixes = []
    pieces = []
    for hi in range(vertical_tiles):
        for wi in range(horizontal_tiles):
            h_start = hi * piece_h
            h_end = h_start + piece_h
            w_start = wi * piece_w
            w_end = w_start + piece_w
            pieces.append(im[h_start:h_end, w_start:w_end])
            postfixes.append(f'_{hi}_{wi}.png')
    return pieces, postfixes


def save_im_pieces(im_path, target_dir, v_count, h_count):
    im = imread(im_path)
    pieces, postfixes = get_file_pieces(im, h_count, v_count)
    fname = os.path.basename(im_path)
    fname = os.path.splitext(fname)[0]
    for p, postfix in zip(pieces, postfixes):
        piece_fname = f"{fname}{postfix}.png"
        imsave(os.path.join(target_dir, piece_fname), p, check_contrast=False)


class BaseProgressWidget(QtWidgets.QWidget):
    """
    Once a process starts this widget displays progress
    """
    def __init__(self, task):
        super().__init__()
        self.task = task
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        self.layout = layout # to add progress bar later.
        self.setLayout(layout)
        # info label for user feedback
        info_label = QtWidgets.QLabel()
        info_label.setText("")
        layout.addWidget(info_label)
        self.info_label = info_label
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.layout.addWidget(self.progress_bar)
        self.setWindowTitle(self.task)

    def onCountChanged(self, value, total):
        self.info_label.setText(f'{self.task} {value}/{total}')
        self.progress_bar.setValue(value)

    def done(self):
        QtWidgets.QMessageBox.about(self, self.task,
                                    f'{self.task} complete')
        self.close()

class CreationThread(QtCore.QThread):
    """
    Runs another thread.
    """
    progress_change = QtCore.pyqtSignal(int, int)
    done = QtCore.pyqtSignal()

    def __init__(self, images_for_dataset, output_dir,
                 h_pieces_from_each_image, v_pieces_from_each_image):
        super().__init__()
        self.images_for_dataset = images_for_dataset
        self.output_dir = output_dir
        self.h_count = h_pieces_from_each_image
        self.v_count = v_pieces_from_each_image
  
    def run(self):
        for i, fpath in enumerate(self.images_for_dataset):
            save_im_pieces(fpath, self.output_dir, self.v_count, self.h_count)
            self.progress_change.emit(i+1, len(self.images_for_dataset))
        self.done.emit()



class CreationProgressWidget(BaseProgressWidget):
    """
    Once the dataset creation process starts the CreateDatasetWidget
    is closed and the CreationProgressWidget will display the progress.
    """
    def __init__(self):
        super().__init__('Creating tiles')

    def run(self, ims_to_sample_from, output_dir,
            h_tiles_per_image, v_tiles_per_image):

        self.progress_bar.setMaximum(len(ims_to_sample_from))
        self.creation_thread = CreationThread(ims_to_sample_from, output_dir,
                                              h_tiles_per_image, v_tiles_per_image)
        self.creation_thread.progress_change.connect(self.onCountChanged)
        self.creation_thread.done.connect(self.done)
        self.creation_thread.start()

class CreateImageTiles(QMainWindow):
    def __init__(self):
        super().__init__()
        self.input_dir = None
        self.output_dir = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Create Image Tiles")

        # Main window needs a layout button
        container_widget = QtWidgets.QWidget()
        self.setCentralWidget(container_widget)
        layout = QtWidgets.QVBoxLayout()
        container_widget.setLayout(layout)

        # Add specify image directory button
        in_directory_label = QtWidgets.QLabel()
        in_directory_label.setText("Input directory: Not yet specified")
        layout.addWidget(in_directory_label)
        self.in_directory_label = in_directory_label
        
        specify_image_dir_btn = QtWidgets.QPushButton('Specify input image directory')
        specify_image_dir_btn.clicked.connect(self.select_input_dir)
        layout.addWidget(specify_image_dir_btn)


        # Add specify image directory button
        out_directory_label = QtWidgets.QLabel()
        out_directory_label.setText("Output directory: Not yet specified")
        layout.addWidget(out_directory_label)
        self.out_directory_label = out_directory_label
        
        specify_out_dir_btn = QtWidgets.QPushButton('Specify output directory')
        specify_out_dir_btn.clicked.connect(self.select_output_dir)
        layout.addWidget(specify_out_dir_btn)


         # max tiles per image input
        h_tiles_per_im_widget = QtWidgets.QWidget()
        layout.addWidget(h_tiles_per_im_widget)
        h_tiles_per_im_widget_layout = QtWidgets.QHBoxLayout()
        h_tiles_per_im_widget.setLayout(h_tiles_per_im_widget_layout)
        h_edit_tiles_per_im_label = QtWidgets.QLabel()

        h_edit_tiles_per_im_label.setText("number of horizontal tiles (evenly sized):")
        h_tiles_per_im_widget_layout.addWidget(h_edit_tiles_per_im_label)
        h_tiles_per_im_edit_widget = QtWidgets.QSpinBox()
        h_tiles_per_im_edit_widget.setMaximum(999999)
        h_tiles_per_im_edit_widget.setMinimum(1)
        h_tiles_per_im_edit_widget.valueChanged.connect(self.validate)
        self.h_tiles_per_im_edit_widget = h_tiles_per_im_edit_widget
        h_tiles_per_im_widget_layout.addWidget(h_tiles_per_im_edit_widget)

        # max tiles per image input (vertical)
        v_tiles_per_im_widget = QtWidgets.QWidget()
        layout.addWidget(v_tiles_per_im_widget)
        v_tiles_per_im_widget_layout = QtWidgets.QHBoxLayout()
        v_tiles_per_im_widget.setLayout(v_tiles_per_im_widget_layout)
        v_edit_tiles_per_im_label = QtWidgets.QLabel()

        v_edit_tiles_per_im_label.setText("number of vertical tiles (evenly sized):")
        v_tiles_per_im_widget_layout.addWidget(v_edit_tiles_per_im_label)
        v_tiles_per_im_edit_widget = QtWidgets.QSpinBox()
        v_tiles_per_im_edit_widget.setMaximum(999999)
        v_tiles_per_im_edit_widget.setMinimum(1)
        v_tiles_per_im_edit_widget.valueChanged.connect(self.validate)
        self.v_tiles_per_im_edit_widget = v_tiles_per_im_edit_widget
        v_tiles_per_im_widget_layout.addWidget(v_tiles_per_im_edit_widget)

        # info label for user feedback
        info_label = QtWidgets.QLabel()
        info_label.setText("Input directory, output directory, horizontal tiles and vertical tiles"
                           " be specified in order to create a dataset.")
        layout.addWidget(info_label)
        self.info_label = info_label

        # Add create button
        create_btn = QtWidgets.QPushButton('Create tiles')
        create_btn.clicked.connect(self.try_submit)
        layout.addWidget(create_btn)
        create_btn.setEnabled(False)
        self.create_btn = create_btn


    def select_input_dir(self):
        self.image_dialog = QtWidgets.QFileDialog(self)
        self.image_dialog.setFileMode(QtWidgets.QFileDialog.Directory)

        def in_dir_selected():
            self.input_dir = self.image_dialog.selectedFiles()[0]
            self.in_directory_label.setText('Image directory: ' + self.input_dir)
            self.image_paths = all_image_paths_in_dir(self.input_dir)
            self.validate()

        self.image_dialog.fileSelected.connect(in_dir_selected)
        self.image_dialog.open()


    def select_output_dir(self):
        self.out_dir_dialog = QtWidgets.QFileDialog(self)
        self.out_dir_dialog.setFileMode(QtWidgets.QFileDialog.Directory)

        def out_dir_selected():
            self.output_dir = self.out_dir_dialog.selectedFiles()[0]
            self.out_directory_label.setText('Output directory: ' + self.output_dir)
            self.validate()

        self.out_dir_dialog.fileSelected.connect(out_dir_selected)
        self.out_dir_dialog.open()


    def validate(self):

        if not self.input_dir:
            self.info_label.setText("Input must be specified to create tiles")
            self.create_btn.setEnabled(False)
            return

        if not self.output_dir:
            self.info_label.setText("Output must be specified to create tiles")
            self.create_btn.setEnabled(False)
            return

        if not self.v_tiles_per_im_edit_widget.value():
            self.info_label.setText("Vertical tiles per image must be "
                                    "specified to create tiles")
            self.create_btn.setEnabled(False)
            return

        if not self.h_tiles_per_im_edit_widget.value():
            self.info_label.setText("Horizontal tiles per image must be "
                                    "specified to create tiles")
            self.create_btn.setEnabled(False)
            return

        if not self.image_paths:
            message = ('Input image directory must contain image files '
                       ' with png, jpg, jpeg, tif'
                       'or tiff extension.')
            self.info_label.setText(message)
            self.create_btn.setEnabled(False)
            return

        # check no duplicates (based on file name)
        fnames = [os.path.basename(i) for i in self.image_paths]
        if len(set(fnames)) != len(fnames):
            dupes, seen = get_dupes(fnames)
            self.info_label.setText(f"{len(dupes)} duplicates found including "
                                    f"{dupes[0]} which was found {seen[dupes[0]]} times.")
            self.create_btn.setEnabled(False)
            return

        # Sucess!
        self.info_label.setText("")
        self.create_btn.setEnabled(True)


    def try_submit(self):
        output_dir = Path(self.output_dir)
        h_tiles_per_image = self.h_tiles_per_im_edit_widget.value()
        v_tiles_per_image = self.v_tiles_per_im_edit_widget.value()
        all_images = self.image_paths
        ims_to_sample_from = all_images
        self.progress_widget = CreationProgressWidget()
        self.progress_widget.run(ims_to_sample_from, output_dir,
                                 h_tiles_per_image, v_tiles_per_image)
        self.close()
        self.progress_widget.show()

if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = CreateImageTiles()
    window.resize(500, 400)
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
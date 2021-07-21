"""
Copyright (C) 2020 Abraham George Smith

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
import os
import argparse
import numpy as np
from skimage.io import imread, imsave

parser = argparse.ArgumentParser()
parser.add_argument('--inputdir',
                    help=('location of directory containing images to extract tiles from'), required=True)
parser.add_argument('--outputdir',
                    help=('location of directory where tiles will be extracted'), required=True)
parser.add_argument('--horizontal',
                    help=('number of horizontal tiles (evenly sized)'), type=int, required=True)
parser.add_argument('--vertical',
                    help=('number of vertical tiles (evenly sized)'), type=int, required=True)


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

def process_images(images_for_dataset, output_dir, vert_tiles, hor_tiles):
    for i, fpath in enumerate(images_for_dataset):
        print('Processing image', i, 'of', len(images_for_dataset), fpath)
        save_im_pieces(fpath, output_dir, vert_tiles, hor_tiles)

if __name__ == '__main__':
    args = parser.parse_args()
    input_dir = args.inputdir
    output_dir = args.outputdir
    v_tiles = args.horizontal
    h_tiles = args.vertical
    fnames = os.listdir(input_dir)
    print('fnames in inputdir count', len(fnames))
    fpaths = [os.path.join(input_dir, f) for f in fnames]
    # exclude hidden files like .DS_Store
    fpaths = [f for f in fpaths if os.path.basename(f)[0] != '.']
    
    print('fpaths for data', fpaths)
    process_images(fpaths, output_dir, v_tiles, h_tiles)

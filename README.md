Create evenly sized image tiles from a folder of images

# GUI:
There is a windows GUI installer available from https://github.com/Abe404/create_image_tiles/releases/tag/v1.0.2

If you need a GUI for Mac or Linux please create an issue. They don't exist due to lack of demand.

# Command line usage:

Make sure you have python3 and pip installed (or conda etc)

## To install the dependencies (if you use pip)
> pip install -r requirements.txt

## how to run (example)
> python cmd.py --inputdir ./input_images --outputdir ./output_tiles --horizontal 10 --vertical 10

## Extra information
> 
> usage: cmd.py [-h] --inputdir INPUTDIR --outputdir OUTPUTDIR --horizontal HORIZONTAL --vertical VERTICAL
> 
> optional arguments:
> 
>   -h, --help            show this help message and exit
> 
>   --inputdir INPUTDIR   location of directory containing images to extract tiles from
> 
>   --outputdir OUTPUTDIR
>                         location of directory where tiles will be extracted
> 
>   --horizontal HORIZONTAL
>                         number of horizontal tiles (evenly sized)
> 
>   --vertical VERTICAL   number of vertical tiles (evenly sized)
> 

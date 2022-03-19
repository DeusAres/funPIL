# funPIL

A collection of PIL, Numpy and OpenCV functions to manipulate images

(Previously drawerFunctions, changed the name because `yes`)

Requirements: python3+, pillow, numpy, opencv

I've coded this because I'm lazy, and since I've found myself writing always the same sets of instructions, I've decided to wrap them up in this collection of little functions.  
It's filled with common operations, from stroking PNGs to drawing Text, conversions between color spaces, or manipulating images.  
Should be intuitive but don't forget to read the little docstrings I've provided.  

An Image object is required for most common operations of image manipulation, it's a plain matrix of pixels.  
An ImageDraw object is required for drawing text and polygons. Operating on an ImageDraw object will have effects on Image object.  

I don't expect to update this very often, but if you find a bug let me know and don't esitate to make pull requests to extend the scripts

# Installation
`pip install funPIL`  

# Usage
I'ts a very simple module to use.
Just write this on top of your code

`from funPIL import df`

Why `df` and not `fp`?
> "fp" is an old C moniker for "file pointer"  
> –LSerni, stackoverflow  

`df` also stands for drawerFunctions, the old name.  
And the keys are near on keyboard.  

But you can use any alias you want:  
`from funPIL import df as sadPIL`  
`from funPIL import df as helloWorld`  

Most of the functions are supposed to speed up your work with less code. It's only based on my experience and needs tho. Say you need a method to resize an image within a size but keeping the ratio, I got you.  
You want to invert the colors of the whole canvas? Hold up chief.  
If someone needs it, just ask it in the issue tab and I'll try to add it, hopefully my skills and enough google will bring it to you. 

# Troubleshooting

### Tuple error
I've made changes to the code. Some functions return an Image and ImageDraw object. If the code give you this error, put a `[0]` to the function returned

`Example: canvas = df.backgroundPNG(200, 200)[0].convert('RGBA')`

# Is the name a joke?
[Maybe it was intended](https://www.urbandictionary.com/define.php?term=fun%20pills)
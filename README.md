# funPIL  

[![PyPI version](https://badge.fury.io/py/funPIL.svg)](https://badge.fury.io/py/funPIL)  

## 🎈 A collection of PIL, Numpy and OpenCV functions to manipulate images


(Previously drawerFunctions, changed the name because `yes`)

Requirements: python3+, pillow, numpy, opencv

I've coded this because I'm lazy, and since I've found myself writing always the same sets of instructions, I've decided to wrap them up in this collection of little functions.  
It's filled with common operations, from stroking PNGs to drawing Text, conversions between color spaces, or manipulating images.  
Should be intuitive but don't forget to read the little docstrings I've provided.  

An Image object is required for most common operations of image manipulation, it's a plain matrix of pixels.  
An ImageDraw object is required for drawing text and polygons. Operating on an ImageDraw object will have effects on Image object.  

I don't expect to update this very often, but if you find a bug let me know and don't esitate to make pull requests to extend the scripts

## 🔧 Installation
Open up your terminal and install the pypi package with:
> `pip install funPIL`  

This package requires `pillow` and `numpy` too.  
> `pip install Pillow`
> `pip install numpy`

And you're good to go.

## 🎨 Usage

I'ts a very simple module to use.
Just write this on top of your code:
> `from funPIL import df`  

Why `df` and not `fp`?
> `"fp" is an old C moniker for "file pointer"`  
> `–LSerni, stackoverflow `  

`df` also stands for drawerFunctions, the old name.  
And the keys are near on keyboard.  

But you can use any alias you want:  
>`from funPIL import df as sadPIL`    
>`from funPIL import df as helloWorld`  

Most of the functions are supposed to speed up your work with less code. It's only based on my experience and needs tho. Say you need a method to resize an image within a size but keeping the ratio, I got you.  
You want to invert the colors of the whole canvas? Hold up chief.  
If someone needs it, just ask it in the issue tab and I'll try to add it, hopefully my skills and enough google will bring it to you. 

## 👷 Troubleshooting and version control

I'm still learning how to mantain a package correctly, while still updating github repo and pypi package.
If you encounter an error don't esitate to hit the issue tab and report.
I will try to fix it ASAP


## 💊 Is the name a joke?

[Maybe it was intended](https://www.urbandictionary.com/define.php?term=fun%20pills)
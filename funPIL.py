from PIL import (Image,
                 ImageDraw,
                 ImageFont,
                 ImageOps,
                 ImageFilter,
                 ImageEnhance
                 )
import numpy as np
from io import BytesIO


def openImage(image):
    """
    Open image
    image: str path to image
    return Image, ImageDraw
    """
    image = Image.open(image)
    draw = ImageDraw.Draw(image)
    return image, draw


def openImageAsJPG(image):
    return Image.open(image).convert("RGB")


def openImageAsPNG(image):
    return Image.open(image).convert("RGBA")


def backgroundPNG(MAX_W, MAX_H, backgroundColor=None):
    """
    A new canvas in RGBA mode
    MAX_W: int, width of canvas
    MAX_H: int, height of canvas
    backgroundColor: None, str (name, #hexcode), tuple (r,g,b,a) # a=255 if not included in tuple
    return Image, ImageDraw
    """
    background = Image.new("RGBA", (MAX_W, MAX_H), color=backgroundColor)
    draw = ImageDraw.Draw(background)

    return [background, draw]


def backgroundJPG(MAX_W, MAX_H, backgroundColor):
    """
    A new canvas in RGBA mode
    MAX_W: int, width of canvas
    MAX_H: int, height of canvas
    backgroundColor: None, str (name, #hexcode), tuple (r,g,b) 
    return Image, ImageDraw
    """
    background = Image.new("RGB", (MAX_W, MAX_H), backgroundColor)
    draw = ImageDraw.Draw(background)

    return background, draw


# -------------------------------- #
# CANVAS MANAGING

def convert(image, mode):
    """
    Conver a canvas from one mode to another
    image: Image object
    mode: str ("RGBA", "RGB", "L", "LA", "P")

    return Image, ImageDraw
    """
    image = image.convert(mode)
    return image, ImageDraw.Draw(image)


def resize(image, W, H, resample=None):
    """
    Resize Image to given size

    image: Image object
    W: int, width of canvas
    H: int, height of canvas
    resample: Image methods of resampling (Image.ANTIALIAS, Image.BICUBIC...)

    return Image, ImageDraw
    """
    image = image.resize((W, H), resample=resample)
    return image, ImageDraw.Draw(image)


def resizeToFit(image, sizeToFit, smaller=False, resample=None):
    """
    Resize to given size mantaining aspect ratio
    If smaller is False, resize the longest side to the given size
    Otherwise True, the shortest side to the given size

    image: Image object
    sizeToFit: int (size to fit)
    smaller: bool () define which side should be fitted to sizeToFit
    resample: Image methods of resampling (Image.ANTIALIAS, Image.BICUBIC...)

    return Image, ImageDraw
    """
    x, y = image.width, image.height

    if smaller:
        if x > y:
            x = int(x * sizeToFit / y)
            y = sizeToFit
        else:
            y = int(y * sizeToFit / x)
            x = sizeToFit
    elif x > y:
        y = int(y * sizeToFit / x)
        x = sizeToFit
    else:
        x = int(x * sizeToFit / y)
        y = sizeToFit

    
    return resize(image, x, y, resample=resample)


def resizeToFitSpace(image, sizesToFit, resample=None):
    """
    Nicely keeps ratio while not exceding the canvas

    image: Image object
    sizeToFit: list of ints (image size to fit)
    resample: Image methods of resampling (Image.ANTIALIAS, Image.BICUBIC...)

    return Image, ImageDraw

    """
    x, y = image.size
    ratio = min(sizesToFit[0] / x, sizesToFit[1] / y)
    x, y = int(x * ratio), int(y * ratio)

    return resize(image, x, y, resample)


def clearCanvas(draw):
    """
    Clear an RGBA image with fresh transparent pixels
    draw: ImageDraw object

    return Draw
    """
    w, h = draw.im.size
    draw.rectangle([0, 0, w, h], fill=(0, 0, 0, 0))

    return draw


def expand(image, x, y):
    """
    Expand the image canvas while keeping the image centered

    image: Image object
    x: width to add
    y: height to add

    return Image, ImageDraw
    """

    w, h = image.size
    exp_image = backgroundPNG(w + x, h + y)[0]
    exp_image = pasteItem(exp_image, image, x // 2, y // 2)

    return exp_image, ImageDraw.Draw(exp_image)


# -------------------------------- #


def cutWithMask(background, item, mask):
    background = Image.composite(background, item, mask)
    return background


def cropImage(image, tupla):
    image = image.crop(tupla)
    return image, ImageDraw.Draw(image)


def cropToRealSize(image):
    """
    Crop the image to real size, useful to crop PNGs
    """
    tupla = image.getbbox()
    image, draw = cropImage(image, tupla)
    return image, draw


def pasteItem(background, item, x, y):
    """
    If any problem is given, convert both images in RGBA
    Example: image.convert("RGBA")
    """
    background.paste(item, (x, y), item)

    return background


def centerItem(background, item):
    """
    Compute the coordinates to center an image on a canvas
    """
    MAX_W, MAX_H = background.width, background.height
    x, y = int((MAX_W - item.width) / 2), int((MAX_H - item.height) / 2)

    return x, y


# -------------------------------- #
# TEXT SECTION


def fontDefiner(fontPath, fontSize):
    """
    Initialize a font object
    """
    path = fontPath
    font = ImageFont.truetype(str(path), size=fontSize)
    return font


def drawText(x, y, draw, message, fontColor, font, anchor = 'lt'):
    """
    Simple method to draw text
    x: int (coordinates for anchor point)
    y: int (coordinates for anchor point)
    draw: ImageDraw object
    message: str (text)
    fontColor: color
    font: ImageFont object
    anchor: starting point
    - #https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html#text-anchors
    reference to this for anchor points

    return ImageDraw
    """
    if type(message) == str:
        draw.text((x, y), message, fill=fontColor, anchor=anchor, font=font, )
    elif type(message) in [list, tuple]:
        draw.multiline_text((x, y), "\n".join(message), fill=fontColor, anchor=anchor, font=font, )


    return draw


def drawTextInsideWidth(
    x1, x2, y, draw, message, font_name, font_size, font_color, justify=None
):
    font = fontDefiner(font_name, font_size)
    while getSize(message, font)[0] > x2 - x1:
        font_size -= 5
        font = fontDefiner(font_name, font_size)

    if justify == "center":
        x1 = int((draw.im.size[0] - getSize(message, font)[0]) / 2)
    draw = drawText(x1, y, draw, message, font_color, font)

    return draw


def centerSingleLineText(MAX_H, MAX_W, font, fontColor, message, draw):
    x, y = font.getsize(message)
    x = (MAX_H - x) / 2
    y = (MAX_W - y) / 2
    draw = draw.text((x, y), message, fill=fontColor, font=font)
    return draw


def drawMultiLine(
    left,
    right,
    y,
    phrase_wrapped,
    font,
    font_color,
    justify="center",
    image=None,
    draw=None,
    stroke=False,
    stroke_size=10,
    stroke_color="black",
    space=0,
):
    """
    This function is a little mess
    left and right: x coordinates and bounding boxes
    y: y coodinate at which height the text should start
    phrase_wrapped: list of strings
    font: font object
    font_color: color of the text
    justify: center, left, right

    !choose only one between image and draw!
    image: image object where text will be pasted in order to stroke the text only
    draw: draw object to write text directly

    stroke: add stroke to text
    stroke_size: size of stroking
    stroke_color: color of stroke
    space: add more space between each line of text
    """
    print('This method will be deprecated, use drawMultiline instead')
    values = getMultipleSize(phrase_wrapped, font)
    height, _, spaces = values[1], values[2], values[3]

    if stroke and image is not None:
        image_stroke, draw = backgroundPNG(*image.size)

    for line in phrase_wrapped:
        if justify == "center":
            x = int((right - left) / 2) - int((getSize(line, font)[0]) / 2) + left

        elif justify == "right":
            x = right - int(getSize(line, font)[0])

        elif justify == "left":
            x = left

        draw = drawText(x, y, draw, line, font_color, font)
        y = y + height + spaces + space

    if stroke:
        image_stroke = strokeImage(image_stroke, stroke, stroke_color)
        image = pasteItem(image, image_stroke, 0, 0)
        return image
    else:
        return draw


def drawMultiline(x, y, draw, text, font, color, anchor='la', spacing=0, align='left'):
    """
    Draws multiple line of text
    x : int coordinate
    y : int coordinate
    draw : ImageDraw object
    text : str with \n or list[str]
    font : ImageFont object
    anchor : str
        - #https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html#text-anchors
        - reference to this for anchor points
        - avoid top, use ascent, broken because Pillow????
    spacing : int space between text
    align : str (left, center, right)

    return ImageDraw object
    """
    if type(text) in [list, tuple]:
        text = "\n".join(text)
    return draw.multiline_text((x,y), text, fill=color, font=font, anchor=anchor, spacing=spacing, align=align)


def fitSize(fontPath, message, canvasW):
    """
    return (int) optimal size of font inside a canvas
    fontPath : str path to font
    message : str or list of str
    canvasW : int width of canvas

    return (int) optimal size of font inside a canvas
    """
    font = fontDefiner(fontPath, 100)
    if type(message) in [list, tuple]:
        w, h = getSizeMultiline(message, font)
    else:
        w, h = getSize(message, font)
    return 100 * canvasW // max(w, h)


def fitFontInCanvas(fontPath, message, WH):
    """
    Fit the text inside the whole canvas
    fontPath : str path to font
    message : str or list/tuple of str
    WH : list/tuple of sizes of canvas

    return ImageFont
    """

    font = fontDefiner(fontPath, 100)

    W, H = WH

    if type(message) in [list, tuple]:
        w, _, h, _ = getMultipleSize(message, font)
    else:
        w, h = getSize(message, font)

    ratio = min(W / w, H / h)
    size = int(100*ratio)

    return fontDefiner(fontPath, size)

def wrapToCanvas(text, width, font):
    text = [each + ' ' for each in text.split(' ')]
    total = []
    i = 0
    while i <= len(text):
        if getSize("".join(text[:i]), font)[0] > width:
            total.append("".join(text[:i-1]).strip(' '))
            text = text[i:]
            i = 0
        i += 1
    if len(text) > 0:
        if getSize(total[-1]+' '+"".join(text).strip(' '), font)[0] < width:
            total[-1] = total[-1]+' '+"".join(text).strip(' ')
        else:
            total.append("".join(text).strip(' '))
    return total
""" 
def wrapToCanvas(text, width, font):
    try:
        i = 0 
        total = []
        while True:
            j = i
            while text[i+1] not in ['\n', ' '] or i+2==len(text):
                i += 1
            if getSize(text[:i+1], font)[0] >= width:
                total.append(text[:j+1].strip(' '))
                text = text[j+1:]
                i = 0
                j = 0
            else:
                i += 1
            if i+2 == len(text):
                total.append(text.strip(' '))

    except:
        total.append(text[:j+1].strip(' '))
        total.append(text[j+1:i+1])
    
    return total

"""


def getSize(text_string, font):
    """
    Get size of single line text
    text_string: string
    font: font object
    # https://stackoverflow.com/a/46220683/9263761

    return text_width, text_height
    """
    """
    ascent, descent = font.getmetrics()
    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] - ascent - descent
    """
    text_width, text_height = font.getsize(text_string)

    #return (text_width, text_height-descent)
    return (text_width, text_height)


def getSizeMultiline(text, font, spacing=0):
    """
    Get sizes of a multiline text
    Substitute to getMultipleSize

    text : str with \n or list[str]
    font : ImageFont

    return width, height
    """
    if type(text) in [list, tuple]:
        text = "\n".join(text)
    return font.getsize_multiline(text=text, spacing=spacing)


def getMultipleSize(text_wrapped, font):
    """
    Get multiline text sizes
    text_wrapped: list of strings
    font: font object

    return max_width, max_height of one line,
    total max_height, total spaces
    """
    print('This method will be deprecated, use getSizeMultiline instead')

    max_width, max_height = 0, 0
    for i in range(len(text_wrapped)):
        try:
            width, height = getSize(text_wrapped[i], font)
        except Exception:
            width, height = 0, 0
        if width > max_width:
            max_width = width
        if height > max_height:
            max_height = height

    ascent, descent = font.getmetrics()
    spaces = descent + ascent
    max_single_height = getSize('M', font)[1]
    #max_single_height = max_height
    max_height = max_height * len(text_wrapped) + spaces * (len(text_wrapped) - 1)

    return max_width, max_single_height, max_height, spaces


# ---------------------------------------------------------------------------------------------------------------------------#
# IMAGE MANIPULATION SECTION


def rotate(img, angle, expand=True, pivot=None):
    """
    rotates an image of a given angle
    img: image object
    angle: degrees (not radians) of rotation
    expand: make canvas of image to fit the rotation
    pivot: define in a tuple the center of the rotation, if None is centered
    """
    img = img.rotate(angle, resample=Image.BICUBIC, center=pivot, expand=expand)
    return img, ImageDraw.Draw(img)

""" # Defeating the requirement of cv2
def rotateCV(image, angle):
"""
"""
    a slightly better algorithm of image rotation
"""
"""
    import numpy as np
    import cv2
    import math

    image = np.array(image)
    h, w = image.shape[:2]
    img_c = (w / 2, h / 2)

    rot = cv2.getRotationMatrix2D(img_c, angle, 1)

    rad = math.radians(angle)
    sin = math.sin(rad)
    cos = math.cos(rad)
    b_w = int((h * abs(sin)) + (w * abs(cos)))
    b_h = int((h * abs(cos)) + (w * abs(sin)))

    rot[0, 2] += (b_w / 2) - img_c[0]
    rot[1, 2] += (b_h / 2) - img_c[1]

    outImg = cv2.warpAffine(image, rot, (b_w, b_h), flags=cv2.INTER_NEAREST)
    return Image.fromarray(outImg)
"""

def flip(image):
    image = ImageOps.flip(image)

    return image


def mirror(image):
    image = ImageOps.mirror(image)

    return image


def strokeImage(original, stroke=1, stroke_color="#FFFFFF", smoother=1):
    """
    Stroke the image with a color

    original : Image
    stroke : width of stroke, int
    stroke_color : color of the stroke, str of hex color
    smoother : increment to have a smoother contour (more time needed), int

    return Image
    """

    if smoother:
        stroke /= smoother
    original = original.convert("RGBA")
    contour = fillWithColor(original, stroke_color)
    for i in range(smoother):
        contour = contour.filter(ImageFilter.GaussianBlur(radius=stroke))

    contour = fillOpaque(contour)
    contour = blurImage(contour, 1)
    original = pasteItem(contour, original, 0, 0)

    return original


def blurImage(image, radius):
    """
    Blur image with given radius
    image: img object
    radius: quantity of blur
    """
    image = image.filter(ImageFilter.GaussianBlur(radius=radius))
    return image, ImageDraw.Draw(image)


def roundCorners(image, rad):
    """
    Rounds the corners of an image to given radius
    im: Image object
    rad: radius of edges

    return Image
    """
    sampling = 4
    rad*=sampling
    im = image.copy().resize((each*sampling for each in image.size))
    mask = Image.new("L", im.size)
    if rad > min(*im.size) // 2:
        rad = min(*im.size) // 2
    draw = ImageDraw.Draw(mask)

    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    draw.ellipse((0, im.height - rad * 2 -2, rad * 2, im.height-1) , fill=255)
    draw.ellipse((im.width - rad * 2, 1, im.width, rad * 2), fill=255)
    draw.ellipse(
        (im.width - rad * 2, im.height - rad * 2, im.width-1, im.height-1), fill=255
    )
    draw.rectangle([rad, 0, im.width - rad, im.height], fill=255)
    draw.rectangle([0, rad, im.width, im.height - rad], fill=255)
    
    mask = mask.resize(image.size, resample=Image.ANTIALIAS)
    image.putalpha(mask)

    return image


def roundCornersAngles(im, rad, angles):
    """
    Rounds only specific corners of the image
    im: Image object
    rad: radius
    angles: list of numbers from 1 to 4, clockwise, starting from the upper left
    just pass the corners you want to be rounded

    return Image
    """
    circle = Image.new("L", (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new("L", im.size, 255)
    w, h = im.size

    if 1 in angles:
        alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))  # upper left
    if 2 in angles:
        alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))  # upper right
    if 3 in angles:
        alpha.paste(
            circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad)
        )  # bottom right
    if 4 in angles:
        alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))  # bottom left
    im.putalpha(alpha)
    return im


def fillWithColor(image, color):
    """
    Fill the entire canvas or png with one color
    img: Image object
    color: color to use

    return Image
    """
    image = image.convert("RGBA")
    alpha = image.getchannel("A")

    image = Image.new("RGBA", image.size, color=color)
    image.putalpha(alpha)

    return image


def replaceColor(image, colorToReplace, replaceColor):
    """
    Replace a present color with another, applied on all image
    This method is extremely precise, only corrisponding pixels
    will be replaced with no threshold
    """
    image = image.convert('RGBA')
    import numpy as np

    if type(colorToReplace) in [list, tuple] and type(colorToReplace[0]) in [list,tuple]:
        if type(replaceColor) in [list, tuple] and type(replaceColor[0]) in [list,tuple]:
            
            if len(colorToReplace) == len(replaceColor):
                colorToReplace = [[*hexToRgb(each), 255] if "#" in each else [*each,255] for each in colorToReplace]
                replaceColor = [[*hexToRgb(each), 255] if "#" in each else [*each,255] for each in replaceColor]
            else:
                raise TypeError

    else:
        colorToReplace = [[*hexToRgb(colorToReplace), 255]] if "#" in colorToReplace else [[*colorToReplace, 255]]

        replaceColor = [[*hexToRgb(replaceColor), 255]] if "#" in replaceColor else [[*replaceColor, 255]]
    
    def parser(color):
        color = str(color)
        rgbNumber = ""
        rgb = []
        for char in color:
            if char.isdigit():
                rgbNumber += char
            if char == "," or char == ")":
                rgb.append(int(rgbNumber))
                rgbNumber = ""
        r, g, b = rgb[0], rgb[1], rgb[2]
        return r,g,b

    data = np.array(image)
    r, g, b, a = data.T
    if colorToReplace is None:  # replace all pixels
        data[..., :-1] = parser(replaceColor)
        image = Image.fromarray(data)
    else:  # replace single color
        for i in range(len(colorToReplace)):
            rr, gg, bb = parser(colorToReplace[i])#colorToReplace[i]
            colorToReplace[i] = (r == rr) & (g == gg) & (b == bb)# & (a == aa)
            data[..., :-1][colorToReplace[i].T] = replaceColor[i][:-1]#parser(replaceColor[i])
        image = Image.fromarray(data)

    return image



def setOpacity(image, opacity):
    """
    Set the opacity of all pixels (not alpha 0)
    Applied to all pixels, even semi transparent
    image: image object
    opacity: percentage from 0 to 100
    """
    import numpy as np

    image = np.array(image)
    alpha = image[:, :, 3]
    mask = alpha > 0
    image[mask, 3] = int(255 * opacity / 100)

    """
    #CHANGED?
    opacity = int(255 * opacity / 100)
    image.putalpha(opacity)
    return image
    """
    return Image.fromarray(image)


def deleteOpaque(image):
    """
    Turns semi-transparent pixel (not alpha 0) in transparent pixels
    image: img object
    """
    import numpy as np

    image = np.array(image)
    alpha = image[:, :, 3]
    mask = alpha < 255
    image[mask] = 0
    return Image.fromarray(image)


def fillOpaque(image):
    """
    Turns semi-transparent pixel (not alpha 0) in solid pixels
    image: image object
    """
    import numpy as np

    image = np.array(image)
    a = image[:, :, 3]
    mask = a > 0
    image[mask, 3] = 255
    return Image.fromarray(image)


def fillTransparent(image, color):
    """
    Fill transparent pixels (alpha 0) with specific color
    image: image object
    color: HEX string, RGB/RGBA tuple
    """
    import numpy as np

    if color[0] == "#":
        rgba = *hexToRgb(color), 255
    elif len(color) == 3:
        rgba = *color, 255
    else:
        rgba = color
        
    image = np.array(image)
    a = image[:, :, 3]
    mask = a == 0
    image[:, :, :4][mask] = [*rgba]
    return Image.fromarray(image)


def modifyBrightness(image, brightness):
    """
    Increase or decrease the brightness of an image
    image: img object
    brightness: int or float between 0 and infinity
        numbers between 0 and 1 decrease brightness
        numbers above 1 increase brightness
    """
    image = ImageEnhance.Brightness(image)

    return image.enhance(brightness)


def superSample(image, sample):
    """
    Supersample an image for better edges
    image: image object
    sample: sampling multiplicator int(suggested: 2, 4, 8)
    """
    w, h = image.size

    image = image.resize((int(w * sample), int(h * sample)), resample=Image.LANCZOS)
    image = image.resize((image.width // sample, image.height // sample), resample=Image.ANTIALIAS)

    
    return image, ImageDraw.Draw(image)



# ---------------------------------------------------------------------------------------------------------------------------#
# CONVERSION SECTIONS

# Trigonometry in case you need it
def cart2Pol(x, y, centerW=0, centerH=0):
    """
    Catersian to Polar
    centerW, centerH: to define a center point
    """
    x, y = x - centerW, y - centerH
    import math

    r = math.sqrt(x ** 2 + y ** 2)
    teta = math.atan2(y, x) * 180 / math.pi
    return r, teta


def pol2Cart(r, degrees, centerW=0, centerH=0):
    """
    Polar to Cartesian
    centerW, centerH: to define a center point
    """
    import math

    x = int(r * math.cos(math.radians(degrees)) + centerW)
    y = int(r * math.sin(math.radians(degrees)) + centerH)

    return x, y

# Conversion between color spaces
def hexToRgb(hex):
    """
    hex: hex string
    """
    hex = hex.replace("#", "")
    r, g, b = [int(hex[i: i + 2], 16) for i in range(0, len(hex), 2)]

    return r, g, b


def rgbToHex(r, g, b):
    """
    r, g, b: int(s)
    """
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def hslToRgb(H, S, L):
    """
    H, S, L: ints(s)
    """
    S, L = S / 100, L / 100
    C = (1.0 - abs(2.0 * L - 1.0)) * S
    X = C * (1 - abs((H / 60) % 2 - 1.0))
    M = L - C / 2

    if H >= 0 and H < 60:
        rgb = [C, X, 0]
    if H >= 60 and H < 120:
        rgb = [X, C, 0]
    if H >= 120 and H < 180:
        rgb = [0, C, X]
    if H >= 180 and H < 240:
        rgb = [0, X, C]
    if H >= 240 and H < 300:
        rgb = [X, 0, C]
    if H >= 300 and H <= 360:
        rgb = [C, 0, X]
    try:
        r, g, b = rgb[0] + M, rgb[1] + M, rgb[2] + M
    except Exception:
        print("error " + str(H) + " " + str(S) + " " + str(L))
    return (int(r * 255), int(g * 255), int(b * 255))


def rgbToHsl(R, G, B):
    """
    R, G, B: ints
    """
    R = R / 255
    G = G / 255
    B = B / 255
    Cmax = max(R, G, B)
    Cmin = min(R, G, B)
    delta = Cmax - Cmin
    if delta == 0:
        H = 0
        S = 0
    elif Cmax == R:
        H = 60 * (((G - B) / delta) % 6)
    elif Cmax == G:
        H = 60 * (((B - R) / delta) + 2)
    elif Cmax == B:
        H = 60 * (((R - G) / delta) + 4)

    L = (Cmax + Cmin) / 2

    if delta != 0:
        S = delta / (1 - abs(2 * L - 1))

    return (int(H), int(S * 100), int(L * 100))


# ---------------------------------------------------------------------------------------------------------------------------#
# COMPUTETIONAL METHODS
def calculateLuminance(image):
    """
    compute the overall luminance on an image
    """

    image = image.resize((100, 100), resample=Image.BICUBIC)
    arr = np.array(image)

    R, G, B = 0.2126, 0.7152, 0.0722

    np.set_printoptions(threshold=False)
    arr = arr[arr[:, :, 3] > 0]

    luminance_total = 0
    total_num_sum = 0

    for x in arr:
        luminance_total += int(x[0] * R + x[1] * G + x[2] * B)
        total_num_sum += 1

    luminance = int(luminance_total / total_num_sum / 255 * 100)
    return luminance


def computeDominant(a):
    """
    return rgb color dominant on RGBA image
    """
    import numpy as np

    a, _ = resizeToFit(a, 200)
    a = np.array(a)
    a = a[a[:, :, 3] > 0]
    colors, count = np.unique(a.reshape(-1, a.shape[-1]), axis=0, return_counts=True)
    rgb = list(colors[count.argmax()])[:-1]
    return rgb

def computeDominant2(img):
    """
    a secondary method to get dominant color of image
    """
    img = img.resize((1,1)).convert("RGB")
    return img.getpixel((0,0))


def complementary(color):
    if '#' in color:
        color = hexToRgb(color)

    color = rgbToHsl(*color)

    color = addColor(color, [180,0,0])

    return rgbToHsl(*color)

    

def randomColorExclusion(color, difference, color_range=360):
    """
    I can't remember why I wrote this
    """
    import random

    exclude = []
    exclude.append(color)
    for i in range(1, difference + 1, 1):
        exclude.append(checkColor(color + i, 360))
        exclude.append(checkColor(color - i, 360))

    num_colors = []
    for i in range(color_range + 1):
        if i not in exclude:
            num_colors.append(i)

    return random.choice(num_colors)


def checkColor(num, rule):
    """
    Don't mind about this, it's used by addColor and something else
    """
    while num > rule:
        num -= rule
        if num < rule:
            return abs(num - 1)
    while num < 0:
        num = abs(num)
        num = rule - num
        if num > 0:
            return abs(num + 1)
    return num


def addColor(color, adding, rule="hsl"):
    """
    Add or subtract values to color
    color: list of RGB or HSL values
    adding: list of values to add relative to color index, negative numbers to subtract
    rule: 'hsl' or 'rgb'


    """
    new_color = []
    if rule == "hsl":
        rule = [360, 100, 100]
    elif rule == "rgb":
        rule = [255, 255, 255]
    for i in range(3):
        if adding != 0:
            new_color.append(checkColor(color[i] + adding[i], rule[i]))
    return new_color


def inverseColor(color):
    """
    Get the inverse RGB color
    color: rgb tuple
    """
    rgbNumber = ""
    rgb = []
    for char in color:
        if char.isdigit():
            rgbNumber += char
        if char == "," or char == ")":
            rgb.append(int(rgbNumber))
            rgbNumber = ""
    r, g, b = rgb[0], rgb[1], rgb[2]
    inverseRGB = "rgb(" + str(255 - r) + "," + str(255 - g) + "," + str(255 - b) + ")"
    return inverseRGB


# ---------------------------------------------------------------------------------------------------------------------------#
# MISC SECTION


def drawShadow(image, background=0xFFFFFF, color="rgb(0,0,0)", offset=20, radius=30):
    canvasB, canvasD = backgroundPNG(
        image.size[0] + offset * 20, image.size[1] + offset * 20
    )
    alpha = image.getchannel("A")
    shadow = Image.new("RGBA", image.size, color=color)
    shadow.putalpha(alpha)

    shadow = resize(
        shadow, shadow.size[0] + int(offset / 2), shadow.size[1] + int(offset / 2)
    )

    x, y = centerItem(canvasB, shadow)
    x, y = x + 25, y + 30
    canvasB = pasteItem(canvasB, shadow, x, y)
    canvasB = canvasB.filter(ImageFilter.GaussianBlur(radius=radius))

    return canvasB


def spreadPattern(canvas, pattern):
    """
    Spread an image on a canvas like a seamless pattern
    canvas: image object
    pattern: image to spread
    """

    w, h = pattern.size

    canvas = pasteItem(canvas, pattern, 0, 0)
    while w < canvas.width or h < canvas.height:

        if h < canvas.height:
            canvas = pasteItem(canvas, cropToRealSize(canvas)[0], 0, h)
        if w < canvas.width:
            canvas = pasteItem(canvas, cropToRealSize(canvas)[0], w, 0)
        w *= 2
        h *= 2

    return canvas
    
def spreadPatternOffset(canvas, pattern):
    """
    Spread an image on a canvas like a seamless pattern but with offset
    canvas: image object
    pattern: image to spread
    """
    tempPattern = backgroundPNG(pattern.width, canvas.height+pattern.height*2)[0]
    for h in range(0, tempPattern.height, pattern.height):
        tempPattern = pasteItem(tempPattern, pattern, 0, h)

    alternate = pattern.height//4
    start = -alternate
    for x in range(0, canvas.width, pattern.width):
        canvas = pasteItem(canvas, tempPattern, x, start-alternate)
        alternate *= -1

    return canvas


def image_to_data(im):
    """
    This is for Pysimplegui library
    Converts image into data to be used inside GUIs
    """

    with BytesIO() as output:
        im.save(output, format="PNG")
        return output.getvalue()


""" DEPRECATED THINGS OR NOT USED ANYMORE, PROBABLY PERFORMANCE ISSUES
KEEPING THEM FOR FUTURE REFERENCES


import numpy as np
import colorsys

rgb_to_hsv = np.vectorize(colorsys.rgb_to_hsv)
hsv_to_rgb = np.vectorize(colorsys.hsv_to_rgb)

def shift_hue(arr, hout):
    r, g, b, a = np.rollaxis(arr, axis=-1)
    h, s, v = rgb_to_hsv(r, g, b)
    h = hout
    r, g, b = hsv_to_rgb(h, s, v)
    arr = np.dstack((r, g, b, a))
    return arr

def shiftColors(image, hue):

    #Colorize PIL image `original` with the given

    img = image.convert('RGBA')
    arr = np.array(np.asarray(img).astype('float'))
    new_img = Image.fromarray(shift_hue(arr, hue/360.).astype('uint8'), 'RGBA')

    return new_img


def blurEdges(image, radius):
    import cv2
    import numpy as np
    import skimage.exposure

    img = np.array(image)

    # extract only bgr channels
    #bgr = img[:, :, 0:3]

    # extract alpha channel
    a = img[:, :, 3]

    # blur alpha channel
    ab = cv2.GaussianBlur(a, (0,0), sigmaX=1, sigmaY=1, borderType = cv2.BORDER_DEFAULT)

    # stretch so that 255 -> 255 and 127.5 -> 0
    aa = skimage.exposure.rescale_intensity(ab, in_range=(127.5,255), out_range=(0,255))

    # replace alpha channel in input with new alpha channel
    out = img.copy()
    out[:, :, 3] = aa

    return Image.fromarray(out)

def roundCorners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)

    return im

    """



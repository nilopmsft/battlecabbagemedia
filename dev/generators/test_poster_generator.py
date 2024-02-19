# Purpose: This script is used to test the poster generator by creating a poster for each media object in the media_objects folder.
# The primary focus is on the text layout, font coloring and font sizing. Thus a lot of hard coded values for paths and therfore
# not a good example of a production script. One of the major reasons is that I need to provide template media objects and images
# that are otherwise not generated at runtime. Massively reducing time to run and cost of testing. i.e. does not follow
# standard dev testing practices.

import os
from PIL import Image, ImageDraw, ImageFont
from matplotlib import font_manager
import json
import random
from fontTools.ttLib import TTFont, TTCollection
import numpy as np

def processImage(font_name, media_object, image_path):

    # Get a list of all font files
    font_files = font_manager.findSystemFonts(fontpaths=None, fontext='ttf')

    # The name of the font you're looking for
    font_name_to_find = font_name

    # Get the path of the font
    font_path = None
    for font_file in font_files:
        try:
            # Try to open as a single font file
            font = TTFont(font_file)
            if font['name'].getDebugName(1) == font_name_to_find:
                font_path = font_file
                break
        except:
            # If that fails, try to open as a font collection file
            font_collection = TTCollection(font_file)
            for font in font_collection.fonts:
                if font['name'].getDebugName(1) == font_name_to_find:
                    font_path = font_file
                    break

    if font_path is None:
        print(f"Font {font_name_to_find} not found, defaulting to arial.ttf")
        font_path="arial.ttf"

    # Open an image file for manipulation
    with Image.open(image_path) as img:
        
        img_w, img_h = img.size

        # Get a random layout from posters.json
        with open(templates_base + "posters.json") as json_file:
            poster_json=json.load(json_file)
            poster_layout=random.choice(poster_json["layouts"])


        # for text_type in poster_layout:
        #     layout = poster_layout[text_type]
            
        #     # Build out a cast layout if the text_type is cast from the template
        #     if text_type == "cast":
        #         #Randomly pull from list of 3 items
        #         #cast_type = random.choice(['actors','directors','full'])
        #         cast_type = layout[0]["cast_type"]
        #         text_string = ""
        #         if cast_type == "directors":
        #             text_string += "Directed By "
        #             for director in media_object["prompt_list"]["directors"]:
        #                 text_string += director + "   "
        #         elif cast_type == "actors":
        #             actor_count=0
        #             for actor in media_object["prompt_list"]["actors"]:
        #                 text_string += actor + "   "
        #                 actor_count += 1
        #             if actor_count == 1:
        #                 text_string = "Starring: " + text_string
        #         else:
        #             for actor in media_object["prompt_list"]["actors"]:
        #                 text_string += actor + "   "
        #             text_string += ":: Directed By "
        #             for director in media_object["prompt_list"]["directors"]:
        #                 text_string += director + "   "
        #     else:
        #         text_string = media_object[text_type]
            
            text_string = media_object["title"]
            # Randomly choose to uppercase the text
            uppercase_chance = random.randint(1, 10)
            if uppercase_chance == 1:
                text_string = text_string.upper()

            #writeText(img, img_w, img_h, text_string, layout[0], font_path, text_type)
            writeText(img, img_w, img_h, text_string, poster_layout, font_path)


        img = img.resize((724, 1267))
        img = img.convert('RGB')
        img.save(image_path.replace('png', 'jpg'), 'JPEG', quality=75)
        img.show()


    return True

def writeText(img, img_w, img_h, text_string, layout, font_path): 
    
    draw = ImageDraw.Draw(img)

    # split the string on a delimeter into a list and find the biggest portion, keep the delimiter
    text_list = text_string.split(layout["delimiter"])
    max_text = max(text_list, key=len)
    
    # If the count of the delimiter in the string is 1 then add the delimtier back to the string
    if text_string.count(layout["delimiter"]) == 1:
        text_list[0] += layout["delimiter"]

    fontsize = 1  # starting font size
    font = ImageFont.truetype(font_path, fontsize)

    # Find  font size to fit the text based upon fraction of the image width and biggest string section
    while font.getlength(max_text) < layout["scale"]*img_w:
        # iterate until the text size is just larger than the criteria
        fontsize += 1
        font = ImageFont.truetype(font_path, fontsize)
    
    # Decrement to be sure it is less than criteria and styled
    fontsize -= layout["decrement"]
    font = ImageFont.truetype(font_path, fontsize)

    ascent, descent = font.getmetrics()
    # The height of the font is the delta of its ascent and descent
    font_height = ascent - descent

    section_top = 25 # Pad off the top of the image
    section_middle = (img_h / 2) - (font_height * len(text_list) + (layout["line_padding"] * len(text_list))) # Center of the image but offset by font and line count
    #section_bottom = img_h - (img_h / 8)
    section_bottom = img_h - (img_h / 8) - (font_height * len(text_list) + (layout["line_padding"] * len(text_list)) + 60) # Bottom of the image but offset by font and line count
    y_placements = {"top": section_top, "middle": section_middle, "bottom": section_bottom}

    w = font.getlength(max_text)
    w_placement=(img_w-w)/2
    # Get the font's ascent and descent

    text_count = 1
    for text_line in text_list:

        # remove proceeding and trailing spaces
        text_line = text_line.strip()
        
        # Get the starting location for the text based upon the layout
        y_start = y_placements[layout["y_placement"]]
        
        y_placement = y_start + ((font_height) * (text_count - 1))
        if text_count > 1:
            y_placement = y_placement + (layout["line_padding"] * (text_count - 1))

        sample_box = (w_placement, y_placement, w_placement + w, y_placement + font_height)
        crop = img.crop(sample_box)
        pixels = np.array(crop)
        average_color = pixels.mean(axis=(0, 1))
        average_color = tuple(map(int, average_color))
        average_color_grayscale = int(0.2989 * average_color[0] + 0.5870 * average_color[1] + 0.1140 * average_color[2])
        complimentary_color = (255 - average_color_grayscale, 255 - average_color_grayscale, 255 - average_color_grayscale)

        # #complimentary_color = tuple(255 - x for x in average_color)
        # color_average = sum(average_color) / len(average_color)
        # if text_type == "title":
        #     case = {
        #         color_average < 60: "#9A9A9A",
        #         color_average > 200: "#101010",
        #         True: "#CDCDCD"

        #     }
        #     stroke_color = case.get(True)

        #     denominator = 275 if color_average > 160 else 235
        #     complimentary_color = (denominator - average_color[0]), (denominator - average_color[1]), (denominator - average_color[2])

        #     #hex_color = '#{:02x}{:02x}{:02x}'.format(complimentary_color[0], complimentary_color[1], complimentary_color[2])
        # else:
        #     opacity = 10
        #     stroke_color=(210, 210, 210, opacity)

        #     if color_average < 60:
        #         r_comp, g_comp, b_comp = 245, 245, 245
        #     elif color_average > 200:
        #         r_comp, g_comp, b_comp = 125, 125, 125
        #         stroke_color=(30, 30, 30, opacity)
        #     else:
        #         r_comp, g_comp, b_comp = 30, 30, 30

        #     complimentary_color = (r_comp, g_comp, b_comp, 100) #opacity as a 4th value (alpha channel)
        #     #hex_color = '#{:02x}{:02x}{:02x}'.format(r_comp, g_comp, b_comp)

        if sum(complimentary_color) / len(complimentary_color) > 127:
            stroke_color = (40, 40, 40)
        else:
            stroke_color = (215, 215, 215)

        draw.text((w_placement, y_placement), text_line, fill="#00FFFF", font=font, stroke_width=layout["stroke_width"], stroke_fill=stroke_color, align='center') # put the text on the image
        
        text_count += 1

        # Find the most common color in the image and use that as the font color
        # color = img.getpixel((0, 0))
        # draw.text((w_placement, y_placement), text_line, fill=color, font=font, stroke_width=layout["stroke_width"], stroke_fill=stroke_color, align='center') # put the text on the image


    return img

templates_base = os.getcwd() + "/library-management/templates/"
example_base = os.getcwd() + "/dev/examples/"
objects_base = example_base + "media_objects"
images_base = example_base + "images"

# loop through the objects in objects_base
for object in os.listdir(objects_base):
    media_object_path = objects_base + "/" + object
    with open(media_object_path) as json_file:
        media_object = json.load(json_file)
        processImage(media_object["image_font"], media_object, images_base + "/" + media_object["id"] + ".png")
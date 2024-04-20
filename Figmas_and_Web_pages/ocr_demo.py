import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
import copy

from PIL import Image,ImageDraw
import os
from font_detector import detect_designer_developer_fonts

# Set the values of your computer vision endpoint and computer vision key
# as environment variables:
try:
    endpoint = os.environ["VISION_ENDPOINT"]
    key = os.environ["VISION_KEY"]
except KeyError:
    print("Missing environment variable 'VISION_ENDPOINT' or 'VISION_KEY'")
    print("Set them before running this sample.")
    exit()

# Create an Image Analysis client for synchronous operations
client = ImageAnalysisClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)

def get_points(polygon_points):
    min_x = float('inf')
    min_y = float('inf')
    max_x = float('-inf')
    max_y = float('-inf')

    for point in polygon_points:
        x, y = point.x, point.y
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        max_x = max(max_x, x)
        max_y = max(max_y, y)

    top_left = (min_x, min_y)
    bottom_right = (max_x, max_y)

    return top_left, bottom_right

def crop_image(path_to_png,box,new_img_name):
    image = Image.open(path_to_png)
    cropped_image = image.crop(box)
    cropped_image.save(new_img_name)
    #print(f'Crop {new_img_name}')

FIGMA_WIDTH=0
FIGMA_HEIGHT=0
WEB_WIDTH=0
WEB_HEIGHT=0
def analyze_image(path_to_img,path_to_crops,path_to_res,designer=True,conf_thresh=0.8):
    global FIGMA_HEIGHT
    global FIGMA_WIDTH
    global WEB_HEIGHT
    global WEB_WIDTH

    with open(path_to_img, "rb") as f:
        web_page_data = f.read()
    with Image.open(path_to_img) as img:
        # Get the dimensions (width and height) of the image
        if designer:
            FIGMA_WIDTH, FIGMA_HEIGHT = img.size
        else:
            WEB_WIDTH, WEB_HEIGHT = img.size

    READ_results = client.analyze(
        image_data=web_page_data,
        visual_features=[VisualFeatures.READ]
    )
    
    if READ_results.read is not None:
        res_file = open(path_to_res,'w',encoding="utf-8")
        results = []
        idx = 0
        for line in READ_results.read.blocks[0].lines:
            for word in line.words:
                if word.confidence < conf_thresh:
                    continue
                else:
                    top_left, bottom_right = get_points(word.bounding_polygon)
                    box = (top_left[0],top_left[1],
                        bottom_right[0],bottom_right[1])
                    #print(box)
                    path_to_crop = f"{path_to_crops}//{idx}.png"
                    #crop_image(path_to_img,box,path_to_crop)

                    data = {'text':word.text, 'box':box, 'crop_path':path_to_crop}
                    results.append(data)
                    idx+=1
                    print(f"Text: '{word.text}', Bounding box: {box}\n")
                    res_file.write(f"Text: '{word.text}', Bounding box: {box}, Conf: {word.confidence}\n")
    return results

def concat_json(image_results, font_results):
    final = {}
    for res1 in image_results:
        for res2 in font_results:
            if res1['crop_path'] == res2['crop_path']:
                final = {'text':res1['text'],
                         'box':res1['box'],
                         'crop_path':res1['crop_path'],
                         'fonts':res2['fonts']}
    return final

def draw_boxes(path_to_png:str,errors:list):
    page = Image.open(path_to_png)
    draw = ImageDraw.Draw(page)
    for error in errors:
        draw.rectangle(error['box'],outline="red")
        top_left = (error['box'][0], error['box'][3])
        draw.text(top_left, error['type'], fill="red", align="left")
    page.save(f"{path_to_png.split('.')[0]}_with_errors.png")

def close_pos(web_pos,figma_pos,thresh=100):
    web_x0, web_y0, web_x1, web_y1 = web_pos
    figma_x0, figma_y0, figma_x1, figma_y1 = figma_pos
    return (abs(web_x0-figma_x0)<thresh) and (abs(web_y0-figma_y0)<thresh)


def compare_results(web_final, figma_final, rel_thres_x=0.1, rel_thres_y=0.01):
    errors = []
    text_errors = 0
    pos_error = 0
    no_cor_error = 0
    #for web_line, figma_line in zip(web_final, figma_final):
    for web_line in web_final:
        found = False
        found_correct = False
        temp_figma_final = copy.deepcopy(figma_final)
        for i in range(len(figma_final)):
            figma_line = figma_final[i]
            figma_box = figma_line["box"]
            web_box = web_line["box"]

            if (abs(figma_box[0]/FIGMA_WIDTH - web_box[0]/WEB_WIDTH) < rel_thres_x) and (abs(figma_box[1]/FIGMA_HEIGHT - web_box[1]/WEB_HEIGHT) < rel_thres_y):
                found = True
                #if close_pos(web_line['box'],figma_line['box'],thresh=10):
                if web_line['text'] == figma_line['text']:
                    found_correct = True
                    del temp_figma_final[i]
                    break
                '''else:
                    #print(web_line['text'])
                    pos_error += 1
                    error = {'box':web_line['box'],'type':'pos error'}
                    errors.append(error)'''
        figma_final = temp_figma_final
        
        errorFound = False
        if found == False:
            no_cor_error += 1
            error = {'box':web_line['box'],'type':'no correlation'}
            errors.append(error)
        elif found_correct == False:
            text_errors += 1
            error = {'box':web_line['box'],'type':'text error'}
            errors.append(error)
        
    print(f'Total errors per lines: {text_errors}/{len(web_final)} text errors, {pos_error}/{len(web_final)} pos errors.')
    return errors

path_to_dir = "C:\\Users\\munro\\OneDrive\\Υπολογιστής\\makeathon\\Makeathon\\Figmas_and_Web_pages"
web_img_results = analyze_image(f"{path_to_dir}\\Web_page.png",f"{path_to_dir}\\web_crops",f"{path_to_dir}\\web_res.txt", False, conf_thresh=0.9)
figma_img_result = analyze_image(f"{path_to_dir}\\Figma_design.png",f"{path_to_dir}\\figma_crops",f"{path_to_dir}\\figma_res.txt", True, conf_thresh=0.9)

print(web_img_results)

errors = compare_results(web_img_results,figma_img_result)

boxes = [d['box'] for d in errors]

draw_boxes(f"{path_to_dir}\\Web_page.png",errors)

print('Done!')


"""
web_crops = 'C:\\Users\\munro\\OneDrive\\Υπολογιστής\\makeathon\\Makeathon\\Figmas_and_Web_pages\\web_crops'
font_crops = 'C:\\Users\\munro\\OneDrive\\Υπολογιστής\\makeathon\\Makeathon\\Figmas_and_Web_pages\\font_crops'
web_font_results = detect_designer_developer_fonts(web_crops)
figma_font_results = detect_designer_developer_fonts(font_crops)

web_final_res = concat_json(image_results=web_img_results,
                            font_results=web_font_results)

figma_final_res = concat_json(image_results=figma_img_result,
                            font_results=figma_font_results)
"""
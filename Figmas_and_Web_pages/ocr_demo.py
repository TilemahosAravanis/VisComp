import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

from PIL import Image,ImageDraw

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

def analyze_image(path_to_img,path_to_crops,path_to_res):
    with open(path_to_img, "rb") as f:
        web_page_data = f.read()
    READ_results = client.analyze(
        image_data=web_page_data,
        visual_features=[VisualFeatures.READ]
    )
    if READ_results.read is not None:
        res_file = open(path_to_res,'w')
        results = []
        idx = 0
        for line in READ_results.read.blocks[0].lines:
            top_left, bottom_right = get_points(line.bounding_polygon)
            box = (top_left[0],top_left[1],
                   bottom_right[0],bottom_right[1])
            #print(box)
            path_to_crop = f"{path_to_crops}//{idx}.png"
            crop_image(path_to_img,box,path_to_crop)

            data = {'text':line.text, 'box':box, 'crop_path':path_to_crop}
            results.append(data)
            idx+=1
            res_file.write(f"Text: '{line.text}', Bounding box: {box}\n")
    return results

def concat_json(image_results, font_results):
    final = {}
    for res1 in image_results:
        for res2 in font_results:
            if res1['crop_path'] == res2['crop_path']:
                final = {'text':res1['text'],'box':res1['box'],'crop_path':res1['crop_path'],
                         'fonts':res2['fonts'],'type':res2['type']}

# path_to_dir = ".\\Figmas_and_Web_pages\\"
# results = analyze_image(f"{path_to_dir}\\Web_page.png",f"{path_to_dir}\\web_crops",f"{path_to_dir}\\web_res.txt")
##text,pos,both = compare_pages(f"{path_to_dir}Web_page.png",f"{path_to_dir}Figma_design.png")
## draw_boxes("Web_page.png",text,pos,both)

dict1 = {'a': 1, 'b': 2, 'c': 3}
dict2 = {'b': 4, 'c': 5, 'd': 6}

common_key = 'c'

dict1.update((key, (dict1.get(key), dict2.get(key))) for key in dict1 if key in dict2)

print(dict1)


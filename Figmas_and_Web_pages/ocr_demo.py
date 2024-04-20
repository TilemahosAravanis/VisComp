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

def compare_pages(path_to_web:str,path_to_figma:str):
    ### open web
    with open(path_to_web, "rb") as f:
        web_page_data = f.read()
    WEB_READ_results = client.analyze(
        image_data=web_page_data,
        visual_features=[VisualFeatures.READ]
    )

    ### open figma
    with open(path_to_figma, "rb") as f:
        web_page_data = f.read()
    FIGMA_READ_results = client.analyze(
        image_data=web_page_data,
        visual_features=[VisualFeatures.READ]
    )
    error_boxes = []
    error_file = open(f'error.txt','w')
    web_file = open('web_res.txt','w')
    figma_file = open('figma_res.txt','w')
    error_file.write('ERRORS FOUND IN WEB: \n')
    if WEB_READ_results.read is not None and FIGMA_READ_results.read is not None:
        for web_line,figma_line in zip(WEB_READ_results.read.blocks[0].lines,FIGMA_READ_results.read.blocks[0].lines):
            # box = [  ## (x0,y0)(x1,y1) are the [0],[2] elements of the list
            #         (line.bounding_polygon[0]['x'],line.bounding_polygon[0]['y']),
            #         (line.bounding_polygon[2]['x'],line.bounding_polygon[2]['y'])
            #         ]
            # text = line.text
            # line_bounding_boxes.append(box) 


            web_file.write(f"   Line: '{web_line.text}', Bounding box {web_line.bounding_polygon}\n")
            figma_file.write(f"   Line: '{figma_line.text}', Bounding box {figma_line.bounding_polygon}\n")
            ### check for any different result
            if web_line.text != figma_line.text or web_line.bounding_polygon != figma_line.bounding_polygon:
                print( "ERROR",web_line.text)
                error_file.write(f"   Line: '{web_line.text}', Bounding box {web_line.bounding_polygon}\n")
                box = [  ## (x0,y0)(x1,y1) are the [0],[2] elements of the list
                        (web_line.bounding_polygon[0]['x'],web_line.bounding_polygon[0]['y']),
                        (web_line.bounding_polygon[2]['x'],web_line.bounding_polygon[2]['y'])
                    ]
                error_boxes.append(box)
            # for word in line.words:
            #     res_file.write(f"     Word: '{word.text}', Bounding polygon {word.bounding_polygon}, Confidence {word.confidence:.4f}\n")
    return error_boxes

def draw_boxes(path_to_png:str,box_list:list):
    page = Image.open(path_to_png)
    draw = ImageDraw.Draw(page)
    for box in box_list:
        draw.rectangle(box,outline="red")
    page.save(f"{path_to_png.split('.')[0]}_with_errors.png")

            

errors = compare_pages("Web_page.png","Figma_design.png")
print(errors)
draw_boxes("Web_page.png",errors)
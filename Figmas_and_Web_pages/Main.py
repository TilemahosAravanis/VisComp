from Image_Similarity import Compute_cosine
from Claude_3_Sonnet import find_differences
from Object_det import Object_detection
from OCR import analyze_image, compare_results, get_client, draw_boxes

import os
from PIL import Image 
import numpy as np

if __name__ == "__main__":

    pages = ['Hau'] # 'DEH' 'Hau',
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for page in pages:
        ### OCR ANALYSIS ###
        ## TODO: incorporate font analysis
        ### get files location
        web_png = os.path.join(script_dir,page,"Web_page.png")
        figma_png = os.path.join(script_dir,page,"Figma_design.png")

        ### get OCR client
        client = get_client()

        ### get Web and Figma OCR results in JSON format
        web_results = analyze_image(client,web_png,None,os.path.join(script_dir,page,"web_res.txt"),False)
        figma_results = analyze_image(client,figma_png,None,os.path.join(script_dir,page,"figma_res.txt"),True)

        ### compare results and get errors JSON
        ocr_errors = compare_results(web_results,figma_results)

        ### draw errors to 'Web_page_with_errors.png'
        draw_boxes(web_png,ocr_errors)

        ### NLP ANALYSIS
        # open method used to open different extension image file 
        im1 = Image.open(figma_png).convert('RGB')
        im2 = Image.open(web_png).convert('RGB')

        print(f"The figma and the web page of {page} match {Compute_cosine(im1,im2)*100}%")


        '''
         Here I am returning Image errors as a list of ('Image error', box)
        '''
        list = Object_detection(im1, im2)

        print(list)


        '''
         Here I am returning detecting backround color mismatch in text response from the LLM
        '''
        png1 = os.path.join(script_dir,page,"Segmented_Figma_design.png")      #f"./{str(page)}/Segmented_Figma_design.png"
        png2 = os.path.join(script_dir,page,"Segmented_Web_design.png")         #f"./{str(page)}/Segmented_Web_page.png"
        prompt = 'I provide two images. Please list any differences in the color of the two images. Ignore any noise in the background.'
        differences = find_differences(png1, png2, prompt)

        print(differences)
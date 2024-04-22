from Image_Similarity import Compute_cosine
from Claude_3_Sonnet import find_differences
from Object_det import Object_detection
from OCR import analyze_image, compare_results, get_client, draw_boxes

import os
from PIL import Image 
import numpy as np

if __name__ == "__main__":

    pages = ['Hellenic_Cyprus_Bank'] # 'DEH' 'Hau',
    
    # scrip dir on mac format
    # script_dir = '/Users/John/Makeathon/Figmas_and_Web_pages/UI_test/public/images'
    script_dir = os.getcwd()
    for page in pages:
        script_dir = os.path.join(script_dir, page)
        ### OCR ANALYSIS ###
        ## TODO: incorporate font analysis
        ### get files location
        web_png = os.path.join(script_dir,"Web_page.png")
        figma_png = os.path.join(script_dir,"Figma_design.png")

        ### get OCR client
        client = get_client()

        ### get Web and Figma OCR results in JSON format
        web_results = analyze_image(client,web_png,None,os.path.join(script_dir,"web_res.txt"),False)
        figma_results = analyze_image(client,figma_png,None,os.path.join(script_dir,"figma_res.txt"),True)

        ### compare results and get errors JSON
        ocr_errors = compare_results(web_results,figma_results)

        ### GLOBAL SIMILARITY SCORE
        # open method used to open different extension image file
        im1 = Image.open(figma_png).convert('RGB')
        im2 = Image.open(web_png).convert('RGB')

        print(f"The figma and the web page of {page} match {Compute_cosine(im1,im2)*100}%")


        '''
         Here I am returning Image errors as a list of ('Image error', box)
        '''
        ### Object Detection
        image_errors = Object_detection(im1, im2, web_png, figma_png)

        errors = ocr_errors + image_errors
        ### draw errors to 'Web_page_with_errors.png'
        draw_boxes(web_png,errors)

        
        '''
         Here I am detecting global differences in text response from the LLM
        '''
        ### NLP ANALYSIS
        png1 = os.path.join(script_dir,"Figma_design.png")     
        png2 = os.path.join(script_dir,"Web_page.png")
        prompt = 'I provide two images. The first image is the Design of a website. The second image is the implementation of the website. Please list any differences of the two images.'
        differences = find_differences(png1, png2, prompt)


        # save diffrerences to a  txt file
        with open(os.path.join(script_dir,"differences.txt"), 'w') as f:
            f.write(f"Images Similarity Score: {Compute_cosine(im1,im2)*100}%")
            f.write(str(differences['content'][0]['text']))


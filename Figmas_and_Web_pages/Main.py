from Image_Similarity import Compute_cosine
from Claude_3_Sonnet import find_differences
from Object_det import Object_detection
# Imports PIL module  
from PIL import Image 
import numpy as np

if __name__ == "__main__":

    pages = ['Hellenic Cyprus Bank'] # 'DEH' 'Hau',

    for page in pages:

        '''
        Valte edw to kommati tou text error klp.
        '''

        '''
        Here I am printing a global similarity percentage
        '''
        # open method used to open different extension image file 
        im1 = Image.open(f"./{str(page)}/Figma_design.png").convert('RGB')
        im2 = Image.open(f"./{str(page)}/Web_page.png").convert('RGB')

        print(f"The figma and the web page of {page} match {Compute_cosine(im1,im2)*100}%")


        '''
        Here I am returning Image errors as a list of ('Image error', box)
        '''
        list = Object_detection(im1, im2)

        print(list)


        '''
        Here I am returning detecting backround color mismatch in text response from the LLM
        '''
        png1 = f"./{str(page)}/Segmented_Figma_design.png"
        png2 = f"./{str(page)}/Segmented_Web_page.png"
        prompt = 'I provide two images. Please list any differences in the color of the two images. Ignore any noise in the background.'
        differences = find_differences(png1, png2, prompt)

        print(differences)
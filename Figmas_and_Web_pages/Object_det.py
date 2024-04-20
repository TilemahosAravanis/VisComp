import os 
from transformers import AutoImageProcessor, DetrForObjectDetection
import torch
from PIL import Image
from Image_Similarity import Compute_cosine
### Transformers Library needed

def crop_image(image_path, bounding_box):
    # Open the image
    image = Image.open(image_path)    # Crop the image using the bounding box coordinates
    cropped_image = image.crop(bounding_box)    # Save the cropped image
    
    return cropped_image

def Object_detection(im1, im2):
    image_processor = AutoImageProcessor.from_pretrained('facebook/detr-resnet-101-dc5')
    model = DetrForObjectDetection.from_pretrained('facebook/detr-resnet-101-dc5')

    inputs1 = image_processor(images=im1, return_tensors="pt")
    outputs1 = model(**inputs1)

    # convert outputs (bounding boxes and class logits) to Pascal VOC format (xmin, ymin, xmax, ymax)

    target_sizes = torch.tensor([im1.size[::-1]])
    results1 = image_processor.post_process_object_detection(outputs1, threshold=0.9, target_sizes=target_sizes)[0]

    inputs2 = image_processor(images=im2, return_tensors="pt")
    outputs2 = model(**inputs2)

    # convert outputs (bounding boxes and class logits) to Pascal VOC format (xmin, ymin, xmax, ymax)

    target_sizes = torch.tensor([im2.size[::-1]])
    results2 = image_processor.post_process_object_detection(outputs2, threshold=0.9, target_sizes=target_sizes)[0]

    res = []
    for score, label, box2 in zip(results2["scores"], results2["labels"], results2["boxes"]):
        
        box2 = [round(i, 2) for i in box2.tolist()]
        im2 = crop_image('./Hellenic Cyprus Bank/Web_page.png', tuple(box2))
        
        flag = True
        for score, label, box1 in zip(results1["scores"], results1["labels"], results1["boxes"]):

            box1 = [round(i, 2) for i in box1.tolist()]
            im2 = crop_image('./Hellenic Cyprus Bank/Figma_design.png', tuple(box1))

            if (Compute_cosine(im1,im2) > 0.6):
                flag = False
                break
        
        if (flag):        
            res.append("Image error", box2)

    return res

import torch
import torch.nn as nn
from torch.nn import functional as nnf
import numpy as np
import matplotlib.pyplot as plt
import os 
from PIL import Image
from sentence_transformers import util
from transformers import ViTImageProcessor, ViTModel

### Transformers Library needed

def Compute_cosine(im1, im2):
    ### Dino image-image similarity calculation for Image Consistency

    processor = ViTImageProcessor.from_pretrained('facebook/dino-vitb8')
    model = ViTModel.from_pretrained('facebook/dino-vitb8')

    inputs = processor(images=[im1, im2], return_tensors="pt")
    outputs = model(**inputs)
    last_hidden_states = outputs.last_hidden_state

    im1_emb = last_hidden_states[0].mean(dim=1)
    im2_emb = last_hidden_states[1].mean(dim=1)

    #Compute cosine similarity
    cos_scores = util.cos_sim(im1_emb, im2_emb)
    
    sim = cos_scores.item()

    return sim


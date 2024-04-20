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
    text_error = []
    position_error = []
    error_file = open(f'error.txt','w')
    web_file = open('web_res.txt','w')
    figma_file = open('figma_res.txt','w')
    error_file.write('ERRORS FOUND IN WEB: \n')
    if WEB_READ_results.read is not None and FIGMA_READ_results.read is not None:
        idx = 0
        for web_line,figma_line in zip(WEB_READ_results.read.blocks[0].lines,FIGMA_READ_results.read.blocks[0].lines):
            
            top_left, bottom_right = get_points(web_line.bounding_polygon)
            box = (top_left[0],top_left[1],
                   bottom_right[0],bottom_right[1])
            print(box)
            crop_image(path_to_web,box,f"web_crops//{idx}.png")
            
            idx+=1
            web_file.write(f"   Line: '{web_line.text}', Bounding box {web_line.bounding_polygon}\n")
            figma_file.write(f"   Line: '{figma_line.text}', Bounding box {figma_line.bounding_polygon}\n")

            ### check for any different result
            # for web_word, figma_word in zip(web_line.words,figma_line.words):
            #     if web_word.text != figma_word.text or web_word.bounding_polygon != figma_word.bounding_polygon:
            #         #print( "ERROR",web_word.text)
            #         error_file.write(f"   Line: '{web_word.text}', Bounding box {web_word.bounding_polygon}\n")
            #         box = [  ## (x0,y0)(x1,y1) are the [0],[2] elements of the list
            #                 (web_word.bounding_polygon[0]['x'],web_word.bounding_polygon[0]['y']),
            #                 (web_word.bounding_polygon[2]['x'],web_word.bounding_polygon[2]['y'])
            #             ]
            #         text_error.append(box)
            #     if web_word.bounding_polygon != figma_word.bounding_polygon:
            #         #print( "ERROR",web_word.text)
            #         error_file.write(f"   Line: '{web_word.text}', Bounding box {web_word.bounding_polygon}\n")
            #         box = [  ## (x0,y0)(x1,y1) are the [0],[2] elements of the list
            #                 (web_word.bounding_polygon[0]['x'],web_word.bounding_polygon[0]['y']),
            #                 (web_word.bounding_polygon[2]['x'],web_word.bounding_polygon[2]['y'])
            #             ]
            #         position_error.append(box)
            # for word in line.words:
            #     res_file.write(f"     Word: '{word.text}', Bounding polygon {word.bounding_polygon}, Confidence {word.confidence:.4f}\n")
            both_error = [x for x in position_error if x in text_error]
    return text_error, position_error, both_error

def draw_boxes(path_to_png:str,text_error:list,pos_error:list,both_error:list):
    page = Image.open(path_to_png)
    draw = ImageDraw.Draw(page)
    for text,pos,both in zip(text_error,pos_error,both_error):
        draw.rectangle(text,outline="red")
        draw.rectangle(pos,outline="blue")
        draw.rectangle(both,outline="green")
    page.save(f"{path_to_png.split('.')[0]}_with_errors.png")

          
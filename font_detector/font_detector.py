import requests
import base64
import os


URL="https://www.whatfontis.com/api2/"


def detect_font_style(filename):
    image = open(filename, "rb").read()
    base64_encoded = base64.b64encode(image).decode('utf-8')

    PARAMETERS ={
        "API_KEY": "YOUR_API_KEY_HERE',
        "IMAGEBASE64": 1,
        "NOTTEXTBOXDETECTION": 0,
        "urlimagebase64": "",
        "limit": 5
    }

    PARAMETERS["urlimagebase64"] = base64_encoded

    # Send POST request and get response
    response = requests.post(
        URL,
        data = PARAMETERS
    )

    response = response.json()

    # Manipulate JSON file
    fonts = []
    for possible_font in response:
        fonts.append(possible_font["title"])
    
    return fonts 


def detect_designer_developer_fonts(designer_img_dir, developer_img_dir):
    ret = []

    # For each image of the designer cropped imgs...
    imgs_filename = os.listdir(designer_img_dir)
    for imgs in imgs_filename:
        filename = designer_img_dir + "/" + imgs
        fonts = detect_font_style(filename)
        dict = {
            "crop_path":filename,
            "fonts":fonts,
            "type":"designer"
        }
        ret.append(dict)

    # For each image of the developer imgs...
    imgs_filename = os.listdir(developer_img_dir)
    for imgs in imgs_filename:
        filename = developer_img_dir + "/" + imgs
        fonts = detect_font_style(filename)
        dict = {
            "crop_path":filename,
            "fonts":fonts,
            "type":"developer"
        }
        ret.append(dict)

    return ret







if __name__ == "__main__":
    cur_file_path = os.path.abspath(__file__)
    work_dir = os.path.dirname(cur_file_path)
    #detect_font_style(work_dir+"/unitt/test.png")
    ret = detect_designer_developer_fonts(work_dir+"/unitt", work_dir+"/unitt")
    print(ret)
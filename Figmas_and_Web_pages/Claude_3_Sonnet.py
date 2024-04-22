import boto3

import base64
import json

def find_differences(png1, png2, prompt):

    runtime = boto3.client("bedrock-runtime", region_name='your_region_here', aws_access_key_id='YOUR_ACCESS_KEY_HERE', 
                           aws_secret_access_key='YOUR_SECRET_KEY_HERE')

    with open(png1, "rb") as im1:
        im1_bytes = im1.read()

    im1 = base64.b64encode(im1_bytes).decode("utf-8")

    with open(png2, "rb") as im2:
        im2_bytes = im2.read()

    im2 = base64.b64encode(im2_bytes).decode("utf-8")

    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": im1,
                            },
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": im2,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        }
    )

    response = runtime.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=body
    )


    response_body = json.loads(response.get("body").read())


    return response_body
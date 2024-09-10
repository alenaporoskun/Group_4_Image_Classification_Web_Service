import os
from django.http import JsonResponse
from django.views.generic import TemplateView
import cloudinary.uploader
import cloudinary
import cloudinary.api
import numpy as np
from PIL import Image
from tensorflow import keras
import logging
import aiohttp
from io import BytesIO
import asyncio

# Set up logging
logger = logging.getLogger(__name__)

# Load the model once when the application starts
MODEL_PATH = 'model/cifar-10.keras'
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
model = keras.models.load_model(MODEL_PATH)

# Image classes
images_classes = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

# Define the asynchronous function for image classification
async def image_classification(image_url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                img_data = await response.read()
                img = Image.open(BytesIO(img_data))
                img = img.convert('RGB')  # Convert the image to RGB
                img = img.resize((32, 32))  # Resize the image to 32x32
                img_array = np.expand_dims(np.array(img) / 255.0, axis=0)  # Add batch dimension and normalize

                # Predict the image class
                predictions = model.predict(img_array)
                predicted_class = np.argmax(predictions, axis=-1)

                return images_classes[predicted_class[0]]
    except Exception as e:
        logger.error(f"Error during image classification: {e}")
        return str(e)

# Define the asynchronous IndexView class
class IndexView(TemplateView):
    template_name = 'main/index.html'

    async def post(self, request, *args, **kwargs):
        if request.FILES.get('image'):
            try:
                # Get the uploaded file
                uploaded_file = request.FILES['image']

                # Upload the file to Cloudinary
                upload_result = cloudinary.uploader.upload(uploaded_file)
                image_url = upload_result['url']  # Get the URL of the uploaded image

                # Classify the image
                result = await image_classification(image_url)

                # Return the result
                return JsonResponse({'result': result})
            except Exception as e:
                # Log and return the error in JSON format
                logger.error(f"Error uploading or processing the file: {e}")
                return JsonResponse({'error': str(e)}, status=500)
        # If no image is uploaded
        return JsonResponse({'result': None})

    async def get(self, request, *args, **kwargs):
        return self.render_to_response({})




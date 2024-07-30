# A Simple technique to resize images with bounding boxes

## Part 1: the challenge
I'm currently working on a project with the Egyptology department at the Sorbonne. The goal is to identify which scribe wrote a papyrus based on their calligraphy.

Their initial idea was to focus on the characters that appear most frequently in the papyrus. The reasoning is that these frequently written characters would best capture a scribe's personal style, as they are likely written more quickly and consistently.

This approach necessitated a double classification system: first to classify the characters, and then to identify the scribe. For scribes not in our database, we planned to develop a clustering algorithm.

### the previous work and the downside
Previous research by Vinci achieved a __top-1 accuracy of 28%__ and __top-5 accuracy at 50%__ for the first classification task. Which, let's be honest, is not crazy.Furthermore, this work had limitations. The papyrus images were typically 3000x3000 pixels in resolution, which Vinci could process due to their powerful GPUs and ample RAM. This is, according me, where the problem lies: The dataset with images was ridiculy small. In contrast, my resources were limited to a free Google Colab account with much less computing power and memory.

## The preprocessing:
My initial idea was to split the large images into smaller 300x300 pixel segments to fit within my RAM constraints, and fit into my model ( which was a VGG16 slightly modified ). However, this posed a risk of cutting through characters and therefore disrupting the model's learning process.

After further reflection, I decided to map the entire image into 300x300 segments. In each segment, I would check for the presence of any part of a bounding box. If a segment contained no bounding box, I would generate an "empty" image. If it did, I would generate an image that includes the bounding box, but with the bounding box randomly shifted left or right. You can see it in cutting_images.py 

I wrote a function that scans through the large image in 300x300 segments. For each segment, it checks if any part of a bounding box is present. If a segment is empty, it generates an empty image. If a bounding box is detected, it generates an image around the bounding box with a randomly shifted location, ensuring a balanced dataset of empty and filled images. This approach helps maintain the integrity of character shapes and ensures the model learns effectively from the data.



### The problems:
I faced issues with generating random frames surrounding the bounding boxes. The random number generation needed to respect the image boundaries. If a bounding box was close to the image border, the random number could result in an out-of-frame image, causing errors.

To solve this, I created minimum and maximum bounds for the random numbers, ensuring they stayed within the image frame (see the get_left_and_top_pad function). Despite this, the minimum value was often 0, and sometimes the maximum was smaller than the minimum. To handle this, I added a condition to default to (0,0) if the situation arose.

Filename Uniqueness
Another issue was the duplication of filenames. To ensure uniqueness, I generated long and complex filenames for each image. However, duplicates still occurred. This was addressed by adding more unique elements to the filenames, though it remained a challenging aspect of the preprocessing.

By addressing these issues, I was able to generate a balanced dataset of empty and filled images, preserving the integrity of character shapes and ensuring effective model learning.


## Part 2: The model:
After preprocessing the images, we developed a model based on a simplified version of VGG, consisting of only 10 layers as our Convolutional Neural Network (CNN). We trained the model for 30 epochs (though more epochs could potentially enhance performance) and achieved impressive results, with high accuracy and a notably low bounding box loss.

To validate the model's performance, we compared the predicted bounding boxes to the target bounding boxes. Ensuring the results were acceptable was crucial because a difference of just 10 pixels could obscure the character in the image. Therefore, we aimed for the model to have less than a 10-pixel difference to be deemed accurate.

Regarding classification, there were no issues, indicating that the model effectively distinguished between different categories as intended.










Downside with working with polars: No integration with Cv2 and with Tensorflow.

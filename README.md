# This Guitar Does Not Exist

## Data preprocessing

Each image is first cropped to its content. Fortunately, the background is totally white for each image, thus, segmentation is very simple.

The data have an average ratio of 3 to 1 (height vs width). The typical input shape for a VQ-GAN is 256 x 256. Using
a width of 148 ensures that the number of pixels stays the same. I.e., each image needs to be downsampled (pyramid downsampling, 2 or 3 times) and the reshaped to 444 x 148. This is all done with skimage's resize function.

Each image should be downsampled $n$ times with a stride of 2. $n$ is the number that yields the smallest difference between the downsampled shape and the desired shape.

Original image shape: (1920, 1920, 3)

## Training VQ-GAN
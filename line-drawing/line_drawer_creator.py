import cv2
import numpy as np

class liner:
    '''draw an image using a string from point to point on a circle

    draw lines from point to point
    compute difference from original, use as loss
    either
        * add another point at the end
        * move a point
    '''
    def __init__(self,
            path_input,
            path_output='out_img.jpg',
            num_corners=100,
            output_size=200,
            ):

        self.path_input = path_input
        self.path_output = path_output

        self.num_corners = num_corners
        self.output_size = output_size

        self.line = []

        self.img = cv2.imread(self.path_input,
                cv2.IMREAD_GRAYSCALE)

        if self.img is None:
            print(f'Empty {self.path_input}')

        #  print(f'Shape of img {self.img.shape}')
        print(f'In img[100][100] {self.img[100][100]} type {type(self.img[100][100])}')

        # some say dtype should be img.dtype stackoverflow.com/a/25075301
        self.circle_mask = np.zeros( (output_size, output_size),
                dtype=self.img.dtype )

        cv2.circle(self.circle_mask,
                center=(output_size//2, output_size//2),
                radius=output_size//2,
                #  color = 1,
                color = 255,
                thickness = -1,
                )

        #  cv2.imshow('mask circle', self.circle_mask)
        #  cv2.waitKey(0)

        x = 200
        y = 200
        self.img_crop = self.img[x+0:x+output_size, y+0:y+output_size]

        self.img_masked = cv2.bitwise_and(self.img_crop, self.img_crop,
                mask=self.circle_mask)
        cv2.imshow('masked image', self.img_masked)
        cv2.waitKey(0)





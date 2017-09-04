from __future__ import print_function, division
import torch
import os
from skimage import io
import pandas as pd
import numpy as np
from torch.utils.data import Dataset

class SynthDataset(Dataset):
    """
    
    Synthetically transformed pairs dataset for training with strong supervision
    
    Args:
            csv_file (string): Path to the csv file with image names and transformations.
            training_image_path (string): Directory with all the images.
            transform (callable): Transformation for post-processing the training pair (eg. image normalization)
            
    Returns:
            Dict: {'image': full dataset image, 'theta': desired transformation}
            
    """

    def __init__(self, csv_file, training_image_path, geometric_model='affine', use_cuda=True, transform=None):
        self.use_cuda = use_cuda
        # read csv file
        self.train_data = pd.read_csv(csv_file)
        self.img_names = self.train_data.iloc[:,0]
        self.theta_array = self.train_data.iloc[:, 1:].as_matrix().astype('float')
        # copy arguments
        self.training_image_path = training_image_path
        self.transform = transform
        self.geometric_model = geometric_model
        
    def __len__(self):
        return len(self.train_data)

    def __getitem__(self, idx):
        # read image
        img_name = os.path.join(self.training_image_path, self.img_names[idx])
        image = io.imread(img_name)
        
        # read theta
        theta = self.theta_array[idx, :]
        
        if self.geometric_model=='affine':
            # reshape theta to 2x3 matrix [A|t] where 
            # first row corresponds to X and second to Y
#            theta = theta[[0,1,4,2,3,5]].reshape(2,3)
            theta = theta[[3,2,5,1,0,4]].reshape(2,3)
        elif self.geometric_model=='tps':
            theta = np.expand_dims(np.expand_dims(theta,1),2)
        
        # make arrays float tensor for subsequent processing
        image = torch.Tensor(image.astype(np.float32))
        theta = torch.Tensor(theta.astype(np.float32))
        
        # permute order of image to CHW
        image = image.transpose(1,2).transpose(0,1)
                
        sample = {'image': image, 'theta': theta}
        
        if self.transform:
            sample = self.transform(sample)

        return sample
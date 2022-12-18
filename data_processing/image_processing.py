import numpy as np
from scipy import ndimage

'''
A small collection of helper functions for image processing
'''

def determine_tumor_crop(pred):
    masks = pred!=0
    #make it a bit bigger
    masks = ndimage.binary_dilation(masks)
    #if no tumor is predicted by GNN (should happen extremely rarely with a trained GNN), then return whole uncropped image
    if(np.all(~masks)):
        print("No GNN predicted tumor, not cropping image")
        mask = ~masks
    ix = np.ix_(masks.any(axis=(1,2)),masks.any(axis=(0,2)),masks.any(axis=(0,1)))
    return ix


#uncrops image back to full size (fills space around with healthy preds)
def uncrop_to_brats_size(crops,voxel_pred):
    #in the case that the size isnt standard you can also read in the original image again and extract the size from there, or just alter the preprocessor to also save the original size.
    brats_size_pred = np.zeros((240,240,155),dtype=np.int16)
    brats_size_pred[crops]=voxel_pred
    return brats_size_pred


#Creates closest crop possible by discarding all planes that are entirely black
#Note returns boolean array, does NOT actually perform crop
#this is so you can also crop the labels
def determine_brain_crop(multi_modal_dataset):
    if(len(multi_modal_dataset.shape)==4):
        max_intensity_val = np.amax(multi_modal_dataset,axis=3)
    elif(len(multi_modal_dataset.shape)==3):
        max_intensity_val = multi_modal_dataset
    else:
        raise Exception(f"Expected input shape of either nxmxr or nxmxrxC. Instead got {multi_modal_dataset.shape}")
    masks = max_intensity_val>0.01
    ix = np.ix_(masks.any(axis=(1,2)),masks.any(axis=(0,2)),masks.any(axis=(0,1)))

    return ix


#put each modality in approx 0,1 range. not sure what the brats units are but they dont seem to have a cap
def normalize_img(image_array,is_flat=False):
    if(is_flat):
        max_vals = np.quantile(image_array,0.995,axis=0).astype(np.float32)
    else:
        max_vals = np.quantile(image_array,0.995,axis=(0,1,2)).astype(np.float32)
    #print("Max value for each modality", maxes)
    return image_array/max_vals

def standardize_img(img_array,mean,std):
    centered = img_array-mean
    standardized = centered/std
    return standardized
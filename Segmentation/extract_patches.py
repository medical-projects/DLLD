﻿#tast 1 a : Generate Bounding Box on Images

import pandas as pd
import numpy as np
import cv2
import imageio as io
import random
import pickle
import os
from random import shuffle

# Specify size of patch
cons_size=13

# Specify location for lesion, normal, normal output and lesion output 
lesion_folder='' 
normal_folder=''
normal_patches=''
lesion_patches=''
base=''
meta_file=''

info=pd.read_csv(meta_file)
lung_info=info[info.Coarse_lesion_type == 5] # 5 for lung lesions
# Generating lesion like bbox from random normal part of the image.

normal_pics=os.listdir(normal_folder)
number=0
top_count=0
patches=[]
for ind,lesion in lung_info.iterrows():
	print(ind)
	number += 1
	p_index='%06d' %(lesion['Patient_index'])
	s_index='%02d' %lesion['Study_index']
	s_id='%02d' %lesion['Series_ID']
	ksa='%03d' %lesion['Key_slice_index']


	f_name=p_index+'_'+s_index+'_'+s_id+'_'+ksa+'.png'
	if(f_name in normal_pics):
		output_path=1
	else:
		continue

	# load image and convert to np_mat, normalise over image
  	img=io.imread(base+f_name)
	data=np.mat(img).astype(np.uint8)
	mean=data.mean()	
	sd=data.std()
	data=(data-mean)/sd
	b_box=np.array(lesion['Bounding_boxes'].split(',')).astype(np.float)
	b_box=b_box.astype(np.int)
	b_box[0]+=5
	b_box[1]+=5
	b_box[2]-=5
	b_box[3]-=5
  	#extract patch and save	
	
	mid=int(cons_size/2)
	for i in range(b_box[1],b_box[3]):
		for j in range(b_box[0],b_box[2]):
			patch=data[i-mid:i+mid+1,j-mid:j+mid+1]
			patch_img={}
			patch_img['data']=patch
			patch_img['type']='L'
			patch_img['file']=f_name
			patches.append(patch_img)
			top_count+=1

	normal=io.imread(normal_folder+f_name)
	normal=np.mat(normal).astype(np.uint8)
	normal=(normal-mean)/sd
	for i in range(mid,normal.shape[0]-mid):
		for j in range(mid,normal.shape[1]-mid):
			patch=normal[i-mid:i+mid+1,j-mid:j+mid+1]
			if(patch.shape[0]!=cons_size or patch.shape[1]!=cons_size):
				continue
			patch_img={}
			patch_img['data']=patch
			patch_img['type']='N'
			patch_img['file']=f_name
			patches.append(patch_img)
			top_count+=1
print(top_count)
data_list={}
data_list['x']=[]
data_list['y']=[]
print(len(patches)) 
for ind,image in enumerate(patches):
	data_list['x'].append(image['data'])
	data_list['y'].append(image['type'])

# Sorting into train and test set
train_images=0
test_images=0
new={}
new['train_x']=[]
new['test_x']=[]
new['train_y']=[]
new['test_y']=[]
for ind,image in enumerate(data_list['x']):
	if(random.random()<0.7):
		image=np.array(image.flatten())
		image=np.squeeze(image)
		new['train_x'].append(image)
		new['train_y'].append(data_list['y'][ind])
		train_images+=1
	else:
		image=np.array(image.flatten())
		image=np.squeeze(image)
		print(image.shape)
		new['test_x'].append(image)
		new['test_y'].append(data_list['y'][ind])
		test_images+=1

print('train_images',train_images)
print('test_images',test_images)

# Set the file name for file output here
f=open('data_all_normalised_13.pickle','wb')
pickle.dump(new,f)

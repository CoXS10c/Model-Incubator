#!/usr/bin/env python3

import os
import tensorflow as tf
import cv2
from deepgaze.head_pose_estimation import CnnHeadPoseEstimator
from pathlib import Path
import json
import argparse
import tqdm
from scipy.spatial.distance import cosine as cosineDS
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
PARSER = argparse.ArgumentParser(description='Search picture with the most similar angle')
PARSER.add_argument('-f', '--folder', required=True, dest='folder',
                    help='text input to search for')
PARSER.add_argument('-i', '--img', required=False, dest='img',
                    help='the image which would be used to calculate similarity between other images')
ARGS = PARSER.parse_args()

sess = tf.Session() #Launch the graph in a session.
my_head_pose_estimator = CnnHeadPoseEstimator(sess) #Head pose estimation object

# Load the weights from the configuration folders
my_head_pose_estimator.load_roll_variables(os.path.realpath("deepgaze/etc/tensorflow/head_pose/roll/cnn_cccdd_30k.tf"))
my_head_pose_estimator.load_pitch_variables(os.path.realpath("deepgaze/etc/tensorflow/head_pose/pitch/cnn_cccdd_30k.tf"))
my_head_pose_estimator.load_yaw_variables(os.path.realpath("deepgaze/etc/tensorflow/head_pose/yaw/cnn_cccdd_30k.tf"))

angle_dict = {}
if ARGS.img:
    most_similar = {}
    image = cv2.imread(ARGS.img)  # Read the image with OpenCV
    # Get the angles for roll, pitch and yaw
    roll = my_head_pose_estimator.return_roll(
        image)  # Evaluate the roll angle using a CNN
    pitch = my_head_pose_estimator.return_pitch(
        image)  # Evaluate the pitch angle using a CNN
    yaw = my_head_pose_estimator.return_yaw(
        image)  # Evaluate the yaw angle using a CNN
    image_angel = [float(
        roll[0, 0, 0]), float(pitch[0, 0, 0]), float(yaw[0, 0, 0])]

for file_name in tqdm.tqdm(Path(ARGS.folder).glob('**/*')):
    suffix = file_name.suffix.lower()
    if suffix != '.png' and suffix != '.jpg' and suffix != '.jpeg':
        continue
    image = cv2.imread(str(file_name))  # Read the image with OpenCV
    # Get the angles for roll, pitch and yaw
    roll = my_head_pose_estimator.return_roll(image)  # Evaluate the roll angle using a CNN
    pitch = my_head_pose_estimator.return_pitch(image)  # Evaluate the pitch angle using a CNN
    yaw = my_head_pose_estimator.return_yaw(image)  # Evaluate the yaw angle using a CNN
    angle_dict[str(file_name)] = [float(roll[0,0,0]), float(pitch[0,0,0]), float(yaw[0,0,0])]
    if ARGS.img:
        most_similar[str(file_name)] = cosineDS(
            angle_dict[str(file_name)], image_angel)

json.dump(angle_dict, open(str(ARGS.folder) + '.json', 'w'))

if ARGS.img:
    SORT = sorted(most_similar.items(), key=lambda x: x[1])
    print(SORT[:10])
    json.dump(SORT, open(ARGS.img + 'most_similar.json', 'w'))

#!/usr/bin/env python3

import argparse
import json
#! /usr/bin/env python
import os
from pathlib import Path

import numpy as np
import tqdm

import cv2
import dlib
import tensorflow as tf
from deepgaze.head_pose_estimation import CnnHeadPoseEstimator
from FaceSwap.face_detection import face_detection
from FaceSwap.face_points_detection import face_points_detection
from FaceSwap.face_swap import (apply_mask, correct_colours, mask_from_points,
                       transformation_from_points, warp_image_2d,
                       warp_image_3d)
from scipy.spatial.distance import cosine as cosineDS
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(
        description='Search picture with the most similar angle')
    PARSER.add_argument('-f', '--folder', required=True, dest='folder',
                        help='text input to search for')
    PARSER.add_argument('-i', '--imgfolder', required=True, dest='imgfolder',
                        help='the image which would be used to calculate similarity between other images')
    PARSER.add_argument('--warp_2d', default=False,
                        action='store_true', help='2d or 3d warp')
    PARSER.add_argument('--correct_color', default=False,
                        action='store_true', help='Correct color')
    PARSER.add_argument('--no_debug_window', default=False,
                        action='store_true', help='Don\'t show debug window')
    ARGS = PARSER.parse_args()

    def find_similar_img(img):
        sess = tf.Session()  # Launch the graph in a session.
        my_head_pose_estimator = CnnHeadPoseEstimator(
            sess)  # Head pose estimation object

        # Load the weights from the configuration folders
        my_head_pose_estimator.load_roll_variables(os.path.realpath(
            "deepgaze/etc/tensorflow/head_pose/roll/cnn_cccdd_30k.tf"))
        my_head_pose_estimator.load_pitch_variables(os.path.realpath(
            "deepgaze/etc/tensorflow/head_pose/pitch/cnn_cccdd_30k.tf"))
        my_head_pose_estimator.load_yaw_variables(os.path.realpath(
            "deepgaze/etc/tensorflow/head_pose/yaw/cnn_cccdd_30k.tf"))

        angle_dict = {}
        most_similar = {}

        # get angle of input image
        image = cv2.imread(img)  # Read the image with OpenCV
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
            roll = my_head_pose_estimator.return_roll(
                image)  # Evaluate the roll angle using a CNN
            pitch = my_head_pose_estimator.return_pitch(
                image)  # Evaluate the pitch angle using a CNN
            yaw = my_head_pose_estimator.return_yaw(
                image)  # Evaluate the yaw angle using a CNN
            angle_dict[str(file_name)] = [float(roll[0, 0, 0]),
                                        float(pitch[0, 0, 0]), float(yaw[0, 0, 0])]
            most_similar[str(file_name)] = cosineDS(
                angle_dict[str(file_name)], image_angel)
        return sorted(most_similar.items(), key=lambda x: x[1])[:10]


    def _select_face(im, r=10):
        faces = face_detection(im)

        if len(faces) == 0:
            print('Detect 0 Face !!!')
            exit(-1)

        if len(faces) == 1:
            bbox = faces[0]
        else:
            bbox = []

            def click_on_face(event, x, y, flags, params):
                if event != cv2.EVENT_LBUTTONDOWN:
                    return

                for face in faces:
                    if face.left() < x < face.right() and face.top() < y < face.bottom():
                        bbox.append(face)
                        break

            im_copy = im.copy()
            for face in faces:
                # draw the face bounding box
                cv2.rectangle(im_copy, (face.left(), face.top()),
                            (face.right(), face.bottom()), (0, 0, 255), 1)
            cv2.imshow('Click the Face:', im_copy)
            cv2.setMouseCallback('Click the Face:', click_on_face)
            while len(bbox) == 0:
                cv2.waitKey(1)
            cv2.destroyAllWindows()
            bbox = bbox[0]

        points = np.asarray(face_points_detection(im, bbox))

        im_w, im_h = im.shape[:2]
        left, top = np.min(points, 0)
        right, bottom = np.max(points, 0)

        x, y = max(0, left-r), max(0, top-r)
        w, h = min(right+r, im_h)-x, min(bottom+r, im_w)-y

        return points - np.asarray([[x, y]]), (x, y, w, h), im[y:y+h, x:x+w]

    def faceswap(src, dst, out):
        # Read images
        src_img = cv2.imread(src)
        dst_img = cv2.imread(dst)

        # Select src face
        src_points, src_shape, src_face = _select_face(src_img)
        # Select dst face
        dst_points, dst_shape, dst_face = _select_face(dst_img)

        w, h = dst_face.shape[:2]

        ### Warp Image
        if not ARGS.warp_2d:
            ## 3d warp
            warped_src_face = warp_image_3d(
                src_face, src_points[:48], dst_points[:48], (w, h))
        else:
            ## 2d warp
            src_mask = mask_from_points(src_face.shape[:2], src_points)
            src_face = apply_mask(src_face, src_mask)
            # Correct Color for 2d warp
            if ARGS.correct_color:
                warped_dst_img = warp_image_3d(
                    dst_face, dst_points[:48], src_points[:48], src_face.shape[:2])
                src_face = correct_colours(warped_dst_img, src_face, src_points)
            # Warp
            warped_src_face = warp_image_2d(
                src_face, transformation_from_points(dst_points, src_points), (w, h, 3))

        ## Mask for blending
        mask = mask_from_points((w, h), dst_points)
        mask_src = np.mean(warped_src_face, axis=2) > 0
        mask = np.asarray(mask*mask_src, dtype=np.uint8)

        ## Correct color
        if not ARGS.warp_2d and ARGS.correct_color:
            warped_src_face = apply_mask(warped_src_face, mask)
            dst_face_masked = apply_mask(dst_face, mask)
            warped_src_face = correct_colours(
                dst_face_masked, warped_src_face, dst_points)

        ## Shrink the mask
        kernel = np.ones((10, 10), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)
        ##Poisson Blending
        r = cv2.boundingRect(mask)
        center = ((r[0] + int(r[2] / 2), r[1] + int(r[3] / 2)))
        output = cv2.seamlessClone(
            warped_src_face, dst_face, mask, center, cv2.NORMAL_CLONE)

        x, y, w, h = dst_shape
        dst_img_cp = dst_img.copy()
        dst_img_cp[y:y+h, x:x+w] = output
        output = dst_img_cp

        dir_path = os.path.dirname(out)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)

        cv2.imwrite(out, output)

        ##For debug
        if not ARGS.no_debug_window:
            cv2.imshow("From", dst_img)
            cv2.imshow("To", output)
            cv2.waitKey(0)

            cv2.destroyAllWindows()

    for extract_img, convert_img in zip(Path(ARGS.imgfolder + '_extract').glob("*.jpg"), Path(ARGS.imgfolder + '_output').glob("*.jpg")):
        for index, (src_img, _) in enumerate(find_similar_img(str(extract_img))):
            try:
                faceswap(src_img, str(convert_img),
                         '{}/{}/{}.jpg'.format(ARGS.imgfolder+'_cv', str(convert_img).split('/')[-1], str(index)))
            except Exception as e:
                print("=========== {} =============".format(e))
                print("should be fixed")

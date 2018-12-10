# Model Incubator

## Prerequisite

1. You need to install python3: `brew install python3.6 git`
2. git clone these three repository: 
	1. [Deepfakes-faceswap](https://github.com/ModelIncubator/Deepfakes-faceswap)
	2. [deepgaze](https://github.com/ModelIncubator/deepgaze)
	3. [FaceSwap](https://github.com/ModelIncubator/FaceSwap)

## Install

1. `pip3 install pipenv`
2. `pipenv install`

## Train (optional)

Read README of [Deepfakes-faceswap](https://github.com/ModelIncubator/Deepfakes-faceswap)

## Run


1. Integrated CMD:
	1. Only use original FaceSwap:
		
		```bash
		run.sh -i=fixtures/normal_girl -eo=fixtures/normal_girl_extract/ -co=fixtures/normal_girl_output/  -m=/srv/model -tra=false
		```
	2. Use Traditional FaceSwap:

		```bash
		./run.sh -i=fixtures/normal_girl -eo=fixtures/normal_girl_extract/ -co=fixtures/normal_girl_output/  -m=/srv/model -tra=true --src=/fixtures/normal_girl_output/5.jpg --dst=/srv/金惠美_extract/
		```
2. Isolated CMD:
	1. Extract the face alignment of normal female that you want to convert using [Deepfakes-faceswap](https://github.com/ModelIncubator/Deepfakes-faceswap): `python3 faceswap.py extract -i <input> -o <output> -m <model>`
	2. Convert normal female to extrodinary female using [Deepfakes-faceswap](https://github.com/ModelIncubator/Deepfakes-faceswap): `python3 faceswap.py convert -i <input> -o <output> -m <model>`
	3. Select the picture with the most similar angle among beautiful girls using [Deepgaze](https://github.com/ModelIncubator/deepgaze): `python3 `
	4. Use [Traditional FaceSwap](https://github.com/ModelIncubator/FaceSwap) to get higher resolution: `python main.py --src <from> --dst <to> --out <output> --correct_color`

## Demo
#!/bin/bash

for a in "$@"
do
case $a in
    -i=*|--input=*)
    input="${a#*=}"
    shift # past argument=value
    ;;
    -m=*|--model=*)
    model="${a#*=}"
    shift # past argument=value
    ;;
    -tra=*|--tradition=*)
    tradition="${a#*=}"
    shift # past argument=value
    ;;
    -hp=*|--headpose=*)
    headpose="${a#*=}"
    shift # past argument=value
    ;;
    --default)
    DEFAULT=YES
    shift # past argument with no value
    ;;
    *)
          # unknown option
    ;;
esac
done
echo "input=${input}"
echo "model=${model}"
echo "tradition=${tradition}"
echo "headpose=${headpose}"


python3 Deepfakes-faceswap/faceswap.py extract -i ${input} -o ${input}_extract
python3 Deepfakes-faceswap/faceswap.py extract -i ${headpose}_preprocess -o ${headpose}_extract
python3 Deepfakes-faceswap/faceswap.py convert -i ${input} -o ${input}_output -m ${model}
if [ "$tradition" = true ]
then
    python3 main.py -f ${headpose} -i ${input} --correct_color --no_debug_window
fi
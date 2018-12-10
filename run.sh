#!/bin/bash

for a in "$@"
do
case $a in
    -i=*|--input=*)
    input="${a#*=}"
    shift # past argument=value
    ;;
    -eo=*|--extout=*)
    extract_output="${a#*=}"
    shift # past argument=value
    ;;
    -co=*|--convout=*)
    convert_output="${a#*=}"
    shift # past argument=value
    ;;
    -s=*|--src=*)
    src="${a#*=}"
    shift # past argument=value
    ;;
    -d=*|--dst=*)
    dst="${a#*=}"
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
echo "extract_output=${extract_output}"
echo "convert_output=${convert_output}"
echo "model=${model}"
echo "tradition=${tradition}"
echo "src=${src}"
echo "dst=${dst}"


# python3 Deepfakes-faceswap/faceswap.py extract -i ${input} -o ${extract_output}
# python3 Deepfakes-faceswap/faceswap.py convert -i ${input} -o ${convert_output} -m ${model}
if [ "$tradition" = true ]
then
    python3 head_post_estimation.py -f ${dst}
    # python FaceSwap/main.py --src ${from} --dst ${dst} --out ${convert_output} --correct_color
fi
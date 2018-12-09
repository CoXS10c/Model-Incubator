#!/bin/bash

for a in "$@"
do
case $a in
    -i=*|--input=*)
    input="${a#*=}"
    shift # past argument=value
    ;;
    -o=*|--output=*)
    output="${a#*=}"
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
    -f=*|--folder=*)
    folder="${a#*=}"
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
echo "output=${output}"
echo "src=${src}"
echo "dst=${dst}"
echo "model=${model}"
echo "folder=${folder}"


python3 faceswap.py extract -i ${input} -o ${output} -m ${model}
python3 head_post_estimation.py -f ${folder}
python3 faceswap.py convert -i ${input} -o ${output} -m ${model}
python main.py --src ${from} --dst ${dst} --out ${output} --correct_color
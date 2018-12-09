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
    -f=*|--folder=*)
    folder="${a#*=}"
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
echo "src=${src}"
echo "dst=${dst}"
echo "model=${model}"
echo "folder=${folder}"
echo "tradition=${tradition}"


python3 faceswap.py extract -i ${input} -o ${extract_output} -m ${model}
python3 faceswap.py convert -i ${input} -o ${convert_output} -m ${model}
if [ $tradition -eq 1 ]
then
    python3 head_post_estimation.py -f ${dst}
    python main.py --src ${from} --dst ${dst} --out ${convert_output} --correct_color
fi
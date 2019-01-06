#!/bin/bash
for a in "$@"
do
case $a in
    -i=*|--inputdir=*)
    inputdir="${a#*=}"
    shift # past argument=value
    ;;
    *)
          # unknown option
    ;;
esac
done

tar zxvf ${inputdir}
python3 preprocess.py -i ${inputdir}

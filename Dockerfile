FROM davidtnfsh/deepfakes-gpu:0.1

RUN apt-get update -qq -y \
 && apt-get install -y git\
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/ModelIncubator/deepgaze.git \
 && git clone https://github.com/ModelIncubator/FaceSwap.git \
 && git clone https://github.com/ModelIncubator/Deepfakes-faceswap.git \
 && apt-get remove --auto-remove --purge git -y

COPY head_post_estimation.py .
COPY run.sh .
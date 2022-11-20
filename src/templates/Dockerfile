FROM nvcr.io/nvidia/pytorch:22.10-py3
# ARG HUGGING_FACE_HUB_TOKEN
ENV DEBIAN_FRONTEND noninteractive
# gradio and streamlit default ports
EXPOSE 7860 8501
RUN  apt update && apt install -y git-lfs ffmpeg libsm6 libxext6 cmake libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*
RUN git lfs install
WORKDIR /space
RUN git clone {{ repo_url }} .
RUN pip install -r requirements.txt
# we will reinstall pillow using pillow-smid, for better performances
RUN pip uninstall -y pillow \
 && pip install -U --force-reinstall pillow-simd
RUN pip install streamlit==1.10.0 "protobuf<4" "click<8.1"         gradio==3.10.1
# if hf token was passed
# run the app once for the initial setup
# RUN if [ "$HUGGING_FACE_HUB_TOKEN" ]; then python app.py; fi
ENTRYPOINT ["python", "app.py"]
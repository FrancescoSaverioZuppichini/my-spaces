FROM my-spaces/base:latest
# ARG HUGGING_FACE_HUB_TOKEN
ENV DEBIAN_FRONTEND noninteractive
RUN  apt update && apt install -y git-lfs ffmpeg libsm6 libxext6 cmake libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*
RUN git lfs install
# we will reinstall pillow using pillow-smid, for better performances
RUN pip uninstall -y pillow \
 && pip install -U --force-reinstall pillow-simd
RUN pip install "protobuf<4" "click<8.1" gradio datasets huggingface_hub ftfy GitPython 
# some space had this error 
# https://stackoverflow.com/questions/72706073/attributeerror-partially-initialized-module-cv2-has-no-attribute-gapi-wip-gs
# so we need to downgrade opencv
RUN pip pencv-python==4.5.5.64 
RUN pip cache purge
# gradio and streamlit default ports
ENV GRADIO_SERVER_NAME "0.0.0.0"
EXPOSE 7860 8501
WORKDIR /home/user/app
# clone user stuff
RUN git clone {{ repo_url }} .
RUN if [ -f "requirements.txt" ]; then pip install -r requirements.txt; fi;
RUN if [ -f "packages.txt" ]; then apt-get install $(grep -vE "^\s*#" packages.txt  | tr "\n" " "); fi;

ENTRYPOINT ["python", "app.py"]
FROM scitools/iris
RUN apt-get -y update
RUN apt-get -y install libgl1-mesa-glx
RUN pip install matplotlib
RUN pip install awscli boto3
RUN mkdir -p /weather


COPY generateIMGFromNC.py /weather
WORKDIR /weather
CMD python generateIMGFromNC.py

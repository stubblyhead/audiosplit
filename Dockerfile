FROM public.ecr.aws/lambda/python:3.10
RUN yum -y install git wget tar xz
RUN pip install --no-cache-dir ffmpeg-python
RUN wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && tar xvf ffmpeg-release-amd64-static.tar.xz && mv ffmpeg-6.1-amd64-static/ff* /usr/bin && rm -Rf ffmpeg*
RUN curl -O https://lambda-insights-extension.s3-ap-northeast-1.amazonaws.com/amazon_linux/lambda-insights-extension.rpm && \
    rpm -U lambda-insights-extension.rpm && \
    rm -f lambda-insights-extension.rpm
COPY split.py ${LAMBDA_TASK_ROOT}
COPY app.py ${LAMBDA_TASK_ROOT}
# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.handler" ]

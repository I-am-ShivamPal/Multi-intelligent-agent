FROM ubuntu:22.04
WORKDIR /app
COPY . .
RUN echo 'Build: Installing dependencies' && type requirements.txt
EXPOSE 5000
CMD python app.py
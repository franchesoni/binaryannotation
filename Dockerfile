FROM python:3.11
WORKDIR /binaryAnnotation

RUN pip install --no-cache-dir --upgrade pip
COPY ./all_requirements.txt /binaryAnnotation/all_requirements.txt
RUN pip install --no-cache-dir -r /binaryAnnotation/all_requirements.txt

COPY . /binaryAnnotation/

EXPOSE 8000
WORKDIR /binaryAnnotation
CMD ["python", "backend.py", "--reload"]
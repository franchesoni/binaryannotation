FROM python:3.11-slim

RUN pip install --no-cache-dir --upgrade pip
COPY ./all_requirements.txt /binaryAnnotation/all_requirements.txt
RUN pip install --no-cache-dir -r /binaryAnnotation/all_requirements.txt
RUN mkdir /results

COPY ./frontend /binaryAnnotation/frontend
COPY ./backend /binaryAnnotation/backend

WORKDIR /binaryAnnotation/backend
# CMD ["python", "backend.py", "--reload"]
CMD ["bash", "launch.sh"]
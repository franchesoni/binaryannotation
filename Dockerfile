FROM python:3.11

RUN pip install --no-cache-dir --upgrade pip
COPY ./all_requirements.txt /binaryAnnotation/all_requirements.txt
RUN pip install --no-cache-dir -r /binaryAnnotation/all_requirements.txt

COPY ./frontend /binaryAnnotation/frontend
COPY ./backend /binaryAnnotation/backend


EXPOSE 8000
WORKDIR /binaryAnnotation/backend
CMD ["python", "backend.py", "--reload"]
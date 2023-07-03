# build frontend code
FROM node:20.3.1-alpine3.17 AS builder
COPY ./reactcode /reactapp
WORKDIR /reactapp
RUN npm install
RUN npm run build

# setup python and packages
FROM python:3.11-slim
RUN pip install --no-cache-dir --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# put backend in app
COPY ./backend /app/backend
# put built frontend in app
COPY --from=builder /reactapp/build /app/frontend
# prepare launch script 
RUN chmod 777 /app/backend/launch.sh
WORKDIR /app/backend

# expose port 8000
EXPOSE 8077
EXPOSE 8078

ENTRYPOINT ["./launch.sh"]
CMD ["newipaddress", "newport"]

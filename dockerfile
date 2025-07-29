FROM public.ecr.aws/lambda/python:3.12

# Copy app and requirements
COPY app app
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the FastAPI app as the handler
CMD ["app.main:handler"]

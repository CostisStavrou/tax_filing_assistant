# Use the official Python image from the Docker Hub 
FROM python:3.11-slim 

# Set the working directory in the container 
WORKDIR /app 

# Copy the requirements file into the container at /app 
COPY requirements.txt . 

# Install any dependencies 
RUN pip install --no-cache-dir -r requirements.txt 

# Copy the content of the local src directory to the working directory 
COPY . . 

# Expose port 8000 to the outside world 
EXPOSE 8000  

# Run the application 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

#docker build -t myapp .
#docker run -p 8000:8000 -e OPENAI_API_KEY="sk-proj-XXXXXXXXXXXXXXXXX" -e SECRET_KEY="XXXXXXXXXXXXXxxx" myapp


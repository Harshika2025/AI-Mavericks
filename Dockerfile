# Step 1: Use an official Python base image
FROM python:3.8-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the current directory contents into the container at /app
COPY . /app

# Step 4: Install the required Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Expose the port that FastAPI will run on
EXPOSE 8000

# Step 6: Define the command to run the FastAPI app using Uvicorn
CMD ["uvicorn", "recommender_api:app", "--host", "0.0.0.0", "--port", "8000"]

# Use SageMath latest image as base
FROM sagemath/sagemath:latest

# Set working directory inside container
WORKDIR /grader

# Copy grader folder contents into /grader
COPY grader/ .

# Install Python dependencies required for grading
RUN sage -python -m pip install nbformat

# Set the entrypoint to the runner
ENTRYPOINT ["sage", "-python", "/grader/entrypoint.py"]
FROM minizinc/minizinc:latest


WORKDIR /src

COPY . .
# Install dependencies
RUN apt-get update && \
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv 
RUN python3 -m venv venv
RUN . venv/bin/activate && \
    pip install -r requirements.txt

ENV PATH="src/venv/bin:$PATH"
RUN echo "python3 main.py" >> ~/.bashrc
CMD ["/bin/bash"]
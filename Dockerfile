FROM python:3.12

# Not required for pip-based installation of LCM.
#RUN apt update
#RUN apt install liblcm-dev

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY ./messages/*.py ./messages/
COPY ./*.lcm ./
COPY ./*.py ./

# The parameters are concatenated with the run command when we specify entrypoint but NOT CMD.
# If we want to be able to specify command-line arguments, use entrypoint:
#CMD [ "python", "./game.py" ]
ENTRYPOINT [ "python", "./game.py" ]

# Build: docker build -t pivot-robotics-challenge .
# Run: docker run -it --rm pivot-robotics-challenge
FROM ubuntu:20.04
USER root
RUN apt-get update && apt-get install -y python3-pip libssl-dev && apt-get install -y mongodb && apt-get install -y git
RUN apt-get install -y unzip
RUN apt-get install -y wget
RUN wget https://github.com/tendermint/tendermint/releases/download/v0.31.5/tendermint_v0.31.5_linux_amd64.zip
RUN unzip tendermint_v0.31.5_linux_amd64.zip && rm tendermint_v0.31.5_linux_amd64.zip && mv tendermint /usr/local/bin
RUN git clone https://github.com/enrikata/bigchaindb_fsm
RUN cd bigchaindb_fsm && python3 setup.py install
RUN apt-get install -y ufw
RUN apt-get install -y sudo
RUN apt-get install nano
RUN useradd -m docker
RUN echo "docker:docker" | chpasswd && adduser docker sudo 
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
RUN sudo ufw allow 26656
RUN bigchaindb -y configure
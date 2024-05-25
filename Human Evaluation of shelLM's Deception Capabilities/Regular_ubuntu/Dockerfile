FROM ubuntu:latest

RUN apt-get update && apt-get install -y && \
        apt-get install -y openssh-server

RUN mkdir /var/run/sshd

RUN useradd -m tomas && \
        echo "tomas:tomy" | chpasswd && \
        useradd -m anna && \
        echo "anna:thispas" | chpasswd

RUN echo 'root:your_password' | chpasswd

RUN mkdir -p /home/tomas/Documents && \
        mkdir -p /home/tomas/Desktop && \
        mkdir -p /home/tomas/Public && \
        mkdir -p /home/tomas/Misc

RUN touch /home/tomas/Documents/notes.txt && \
        echo "Remember to wash the dishes!" > /home/tomas/Documents/notes.txt

RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd && \
    echo "export VISIBLE=now" >> /etc/profile

RUN chown -R tomas:tomas /home/tomas
RUN chown -R anna:anna /home/anna

RUN usermod -s /bin/bash tomas && \
        usermod -s /bin/bash anna

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

USER root
WORKDIR /home/tomas

EXPOSE 22

CMD ["/entrypoint.sh"]

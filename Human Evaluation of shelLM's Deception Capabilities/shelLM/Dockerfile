FROM python:latest

RUN  apt update && apt-get -y install openssh-server

RUN pip install --upgrade pip

WORKDIR /opt/system

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /var/run/sshd
RUN mkdir -p /root/.ssh

RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd && \
    echo "export VISIBLE=now" >> /etc/profile

COPY config/sshd_config /etc/ssh/sshd_config
COPY config/system.sh /etc/profile.d/system.sh

RUN chmod +x /etc/profile.d/system.sh
RUN mkdir -p /opt/system/logs
RUN mkdir -p /opt/system/historylogs

RUN mkdir -p /etc/sudoers.d
RUN useradd -m -s /bin/bash tomas && echo 'tomas:tomy' | chpasswd && echo 'tomas ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/tomas
RUN chmod 0440 /etc/sudoers.d/tomas

USER tomas
RUN mkdir -p /home/tomas/.ssh
COPY config/bashrc /home/tomas/.bashrc
COPY config/hushlogin /home/tomas/.hushlogin


USER root

RUN echo 'source /etc/profile.d/system.sh' >> /home/tomas/.bashrc
COPY configSSH.yml .
COPY toolForExperiment.py tool.py
COPY .env .

RUN chown -R tomas:tomas /opt/system

#CMD /usr/sbin/sshd -D
ENTRYPOINT [ "/usr/sbin/sshd", "-D" ]

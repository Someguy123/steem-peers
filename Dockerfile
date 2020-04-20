from ubuntu:focal

RUN apt-get update -qy && apt-get install -qq -y vim nano curl tmux && apt-get clean -qy

RUN echo 'export PS1="\[$(tput bold)\]\[\033[38;5;9m\]\u\[$(tput sgr0)\] \[$(tput sgr0)\]\[\033[38;5;10m\]@\[$(tput sgr0)\]' \
         '\[$(tput sgr0)\]\[$(tput bold)\]\[\033[38;5;12m\]\h\[$(tput sgr0)\] \[$(tput sgr0)\]\[\033[38;5;170m\][\[$(tput sgr0)\]' \
         '\[$(tput sgr0)\]\[$(tput bold)\]\[\033[38;5;228m\]\w\[$(tput sgr0)\] \[$(tput sgr0)\]\[\033[38;5;211m\]]\[$(tput sgr0)\]' \
         '\[$(tput sgr0)\]\[$(tput bold)\]\[\033[38;5;171m\]\\$\[$(tput sgr0)\] "' >> /root/.bashrc

RUN curl -fsSL https://raw.githubusercontent.com/Someguy123/someguy-scripts/master/dotfiles/tmux.conf.modern > /root/.tmux.conf

WORKDIR /root/steem-peers

COPY . /root/steem-peers/

CMD [ "bash" ]
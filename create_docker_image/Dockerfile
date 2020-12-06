FROM ubuntu:18.04
RUN apt update && apt upgrade -y && apt install python3 python3-requests python3-bs4 git -y
RUN mkdir -p /etc/steam_gifts/ /opt/steam_gifts/
WORKDIR /opt/steam_gifts/
COPY bad_giveaways_link.txt sg.py win.sh won.txt files_for_unpack.zip  ./
RUN chmod +x /opt/steam_gifts/sg.py
CMD /usr/bin/python3 -u /opt/steam_gifts/sg.py

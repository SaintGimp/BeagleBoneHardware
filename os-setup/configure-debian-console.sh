#!/bin/bash

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/games:/usr/games"
sudo sed -i "s/\(\/usr\/local\/bin:\/usr\/bin:\/bin:\/usr\/local\/games:\/usr\/games\)/\/usr\/local\/sbin:\/usr\/local\/bin:\/usr\/sbin:\/usr\/bin:\/sbin:\/bin:\/usr\/local\/games:\/usr\/games/" /etc/profile

sudo apt-get update

# set locale
sudo apt-get install locales
sudo sed -i 's/\(# \)\(en_US\.UTF-8.*\)/\2/' /etc/locale.gen
sudo /usr/sbin/locale-gen

# wireless adapters
sudo apt-get -y install firmware-ralink
sudo apt-get -y install firmware-atheros
sudo apt-get -y install wicd-curses

# install additional packages
sudo apt-get -y install git
sudo apt-get -y install curl
sudo apt-get -y ntpdate
sudo apt-get -y install device-tree-compiler
sudo apt-get -y install python-smbus
sudo apt-get -y install i2c-tools
sudo apt-get -y install tmux
sudo apt-get -y install bash-completion
echo "
bind 'set completion-ignore-case on'
bind 'set show-all-if-ambiguous on'
" >> ~/.bashrc
#sudo apt-get -y install python3-dev

# Python
sudo apt-get -y install python2.7
sudo apt-get -y install python3-dev
curl https://bootstrap.pypa.io/get-pip.py | sudo python3.2
sudo pip install pyserial
# TODO: virtualenvwrapper doesn't seem to work well with sudo, and we have to sudo to run GPIO code on the BBB
#sudo pip2 install virtualenvwrapper
#mkdir ~/.virtualenvs
#echo "
#export WORKON_HOME=$HOME/.virtualenvs
#source /usr/local/bin/virtualenvwrapper_lazy.sh
#" >> ~/.bashrc

# set timezone
# ntpdate -b -s -u pool.ntp.org
sudo sh -c 'echo "US/Pacific" > /etc/timezone'
sudo dpkg-reconfigure -f noninteractive tzdata

# home folder
mkdir -p ~/bin

# git global configuration
git config --global user.email "saintgimp@hotmail.com"
git config --global user.name "Eric Lee"
git config --global alias.hist "log --graph --pretty=format:'%C(red)%h%Creset -%C(bold red)%d%Creset %s %Cgreen(%cr) %C(cyan)<%an>%Creset' --abbrev-commit --date=relative"
git config --global rerere.enabled true
#git config --global push.default simple
# TODO: Debian wheezy only has git 1.7.10, push.default simple was added in 1.7.11
git config --global push.default current
git config --global credential.helper 'cache --timeout 36000'

# git completion and prompt
curl https://raw.githubusercontent.com/git/git/master/contrib/completion/git-completion.bash -o ~/.git-completion.bash
curl https://raw.githubusercontent.com/git/git/master/contrib/completion/git-prompt.sh -o ~/.git-prompt.sh
echo "
source ~/.git-completion.bash
source ~/.git-prompt.sh
export GIT_PS1_SHOWDIRTYSTATE=1
export GIT_PS1_SHOWSTASHSTATE=1
export GIT_PS1_SHOWUNTRACKEDFILES=1
export GIT_PS1_SHOWUPSTREAM='auto'
export PS1='\[\033]0;\w\007\033[32m\]\u@\h \[\033[33m\w\$(__git_ps1)\033[0m\]
$ '
" >> ~/.bashrc

echo "
Done. Rebooting...
"

sudo reboot
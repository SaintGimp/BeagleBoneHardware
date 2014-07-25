#!/bin/bash

# make a user
sudo adduser elee
usermod -a -G debian,adm,kmem,dialout,cdrom,floppy,audio,dip,video,plugdev,users,netdev,i2c,admin,spi,systemd-journal,weston-launch,xenomai elee
sudo service dbus reload
su elee

# remove unneeded stuff
sudo apt-get -y purge vim 
sudo apt-get -y purge vim-runtime
sudo apt-get -y purge libopencv-*
sudo rm -rf /usr/share/doc

# install additional packages
sudo apt-get -y install bash-completion
echo "
bind 'set completion-ignore-case on'
bind 'set show-all-if-ambiguous on'
" >> ~/.bashrc
sudo apt-get -y install python3-dev

# remove docs again because we added stuff
sudo rm -rf /usr/share/doc

# clean up apt-get
sudo apt-get -y autoremove
sudo apt-get clean

# set timezone
# ntpdate -b -s -u pool.ntp.org
echo "US/Pacific" > /etc/timezone    
sudo dpkg-reconfigure -f noninteractive tzdata

# home folder
mkdir -p ~/bin

# git global configuration
git config --global user.email "saintgimp@hotmail.com"
git config --global user.name "Eric Lee"
git config --global alias.hist "log --graph --pretty=format:'%C(red)%h%Creset -%C(bold red)%d%Creset %s %Cgreen(%cr) %C(cyan)<%an>%Creset' --abbrev-commit --date=relative"
git config --global rerere.enabled true
git config --global push.default simple
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
To configure WiFi, use 'wicd-curses'.
"
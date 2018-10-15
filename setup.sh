#!/usr/bin/env sh

X=~/nasdaq_scraper/
if [ -d "$X" ]; then 
    rm -rf ~/nasdaq_scraper
fi

# install homebrew if not present
if [ ! "$(command -v brew)" ]; then
        ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
        export PATH=/usr/local/bin:/usr/local/sbin:$PATH
fi

# install git if not present
if [ ! "$(command -v git)" ]; then
        brew doctor
        brew install git
fi

# install python if not present
if [ ! "$(command -v python3)" ]; then
        brew install python
fi
        
git clone https://github.com/geofflangenderfer/nasdaq_scraper.git \
    ~/nasdaq_scraper

pip3 install -r ~/nasdaq_scraper/requirements.txt

Y=~/Desktop/nasdaq_scraper/
if [ -d "$Y" ]; then
	rm -rf ~/Desktop/nasdaq_scraper
fi

mkdir ~/Desktop/nasdaq_scraper

cp ~/nasdaq_scraper/nasdaq_scraper.py \
   ~/nasdaq_scraper/EarningsWatchList.xlsx \
   ~/nasdaq_scraper/nav_trad.png \
   ~/Desktop/nasdaq_scraper

mv ~/Desktop/nasdaq_scraper/nasdaq_scraper.py ~/Desktop/nasdaq_scraper/nasdaq_scraper.command

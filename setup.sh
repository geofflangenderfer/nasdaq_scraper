#!/usr/bin/env sh

X=~/nasdaq_scraper/
if [ -d "$X" ]; then 
    rm -rf ~/nasdaq_scraper
fi

git clone https://github.com/geofflangenderfer/nasdaq_scraper.git \
    ~/nasdaq_scraper

Y=~/Desktop/nasdaq_scraper/
if [ -d "$Y" ]; then
	rm -rf ~/Desktop/nasdaq_scraper
fi

mkdir ~/Desktop/nasdaq_scraper

cp ~/nasdaq_scraper/nasdaq_scraper.py \
   ~/nasdaq_scraper/EarningsWatchList.xlsx \
   ~/Desktop/nasdaq_scraper
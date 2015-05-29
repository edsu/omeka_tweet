This little script tweets new items that are added to an Omeka instance. It uses
Omeka''s RSS feed, and will get item descriptions, creators and images to post to Twitter. You can see a sample Twitter stream over at [baltimoreup](https://twitter.com/baltimoreup).

It is designed to be run from cron using environment variables. The sample
run.sh shows how you can do this.

    git clone https://github.com/edsu/omeka_tweet
    cd omeka_tweet
    virtualenv ENV
    source ENV/bin/activate
    pip install -r requirements.txt
    cp run.sh.example run.sh
    # edit run.sh with your Twitter credentials, etc.
    ./run.sh

Then you should be able to just put run.sh in your crontab to run 
every 15 minutes or whatever. For example:

    0,10,20,30,40,50 * * * * /home/ed/Projects/omeka_tweet/run.sh

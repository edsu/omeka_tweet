This little script tweets new items that are added to an Omeka 
instance. It is designed to be run from cron using environment
variables. The sample run.sh shows how you can do this.

    git clone https://github.com/edsu/omeka_tweet
    cd omeka_tweet
    virtualenv ENV
    pip install -r requirements.txt
    cp run.sh runs.sh.template
    # edit run.sh variables
    ./run.sh

You can see a sample Twitter stream over at
[baltimoreup](https://twitter.com/baltimoreup).


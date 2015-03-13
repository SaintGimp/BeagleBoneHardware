var request = require('request');
var Twitter = require('twitter');

function notify() {
  var client = new Twitter({
    consumer_key: process.env.TWITTER_CONSUMER_KEY,
    consumer_secret: process.env.TWITTER_CONSUMER_SECRET,
    access_token_key: process.env.TWITTER_ACCESS_TOKEN_KEY,
    access_token_secret: process.env.TWITTER_ACCESS_TOKEN_SECRET,
  });

  client.post('statuses/update', {status: 'Hey @saintgimp, I think the geiger counter is offline!'},  function(error, tweet, response){
    if (error) throw error;
  });  
}

var options = {
  url: 'http://gimp-phant.azurewebsites.net/output/'+ process.env.STREAM_PUBLIC_KEY +'/latest.json',
  json: true
};
console.log(options.url);

request(options, function (error, response, body) {
  if (error) throw error;
  
  if (response.statusCode == 200) {
    var latestEntry = new Date(body[0].timestamp);
    var now = new Date();
    var elapsedMinutes = (now.getTime() - latestEntry.getTime()) / 1000 / 60;
    if (elapsedMinutes > 30) {
      console.log("Hey, I think the geiger counter is offline!");
    	notify();
    } else {
      console.log("Everything's fine here, we're all fine, how are you?")
    }
  } else {
    console.log(error);
    console.log(response);
  }
});
console.log('Mixtape loaded!')

// Check that we are on soundcloud.com
if (window.document.origin.indexOf('soundcloud.com') != -1) {
  song_url = window.location.href;
  serverUrl = 'https://4a807c2a.ngrok.io/?song_url=' + encodeURI(song_url);
  console.log('sending to ' + serverUrl)
  $.get(serverUrl, function(e) {
    console.log(e);
    console.log('adding button');
    skipButton = document.createElement('button');
    skipButton.className = 'skipControl playControls__icon sc-ir skipControl__next';
    $('.playControls__playPauseSkip').appendChild(skipButton);
  })
}


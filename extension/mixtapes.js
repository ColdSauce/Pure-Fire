console.log('Mixtape loaded!')

// Check that we are on soundcloud.com
if (window.document.origin.indexOf('soundcloud.com') != -1) {
  url = window.location.href;
  serverUrl = 'mixtape.ngrok.com'
  var xhr = new XMLHttpRequest();
  xhr.open("post", serverUrl, false);
  xhr.send();
  console.log(xhr.status, xhr.statusText);
}

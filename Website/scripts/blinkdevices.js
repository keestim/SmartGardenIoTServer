function flashalllights () {
  var oReq = new XMLHttpRequest();
  oReq.open("GET", "http://localhost:5000/flash_all_lights");
  oReq.send();
}

function blinkdevice(device_id) {
  var oReq = new XMLHttpRequest();
  oReq.open("GET", "http://localhost:5000/flash_light/" + device_id);
  oReq.send(); 
}

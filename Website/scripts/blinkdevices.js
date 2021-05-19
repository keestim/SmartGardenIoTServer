function flashalllights () {
    console.log(this.responseText);
    // document.getElementById("demo").innerHTML = this.responseText;
  }
  
  var oReq = new XMLHttpRequest();
  oReq.addEventListener("load", flashalllights);
  oReq.open("GET", "http://localhost:5000/flash_all_lights");
  oReq.send();

function blinkdevice0 () {
    console.log(this.responseText);
    // document.getElementById("demo").innerHTML = this.responseText;
  }
  
  var oReq = new XMLHttpRequest();
  oReq.addEventListener("load", blinkdevice0);
  oReq.open("GET", "http://localhost:5000/flash_light/0");
  oReq.send();
  

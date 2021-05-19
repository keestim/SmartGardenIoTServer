function loadDevices () {

var oReq = new XMLHttpRequest();

oReq.onreadystatechange = function() {
document.getElementById("demo").innerHTML = "this.responseText";

oReq.open("GET", "127.0.0.1:5000/probe_devices");
oReq.send();

};
}
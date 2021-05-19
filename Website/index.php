<!--
author: Thomas Bibby
created: 18/05/2021
-->
<?php
  header("Access-Control-Allow-Origin", "*");
  header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
?>

<!DOCTYPE html> 
<html lang="en">
<head>
  <title>Responsive Web Design</title>
  <meta charset="utf-8" />
  <meta name="description" content="Home page of website" />
  <meta name="keywords" content="smart, garden, Iot, things, plants, watering" />
  <meta name="author" content="Thomas Bibby"  /> 
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="styles/style.css" rel="stylesheet">
  <link href="styles/indexStyle.css" rel="stylesheet">
  <link href="styles/responsive.css" rel="stylesheet">
  <script src="./scripts/jquery-3.6.0.min.js"></script>
  <script src="./scripts/loadhtml.js"></script>
  <script src="./scripts/loaddevices.js"></script>
 </head>
<body>
  <article>
    <header><h1>Smart Garden</h1></header>
    <div class="navbar" id="navbar">
    </div>
    
    <section id="MainSectionA">
      <section class="section1">
      <h3 id="demo">Device list</h3>
      <!-- Display all devices, name aka watering device and id -->
      <p> 
        <ul>
          <li>Device 1 <button onclick="location.href='localhost:5000/';" type="button">Blink device</button></li> <!-- href is the url to blink that id -->
          <li>Device 2 <button onclick="location.href='localhost:5000/';" type="button">Blink device</button></li> <!-- href is the url to blink that id -->
          <li>Device 3 <button onclick="location.href='localhost:5000/';" type="button">Blink device</button></li> <!-- href is the url to blink that id -->
          <li>Device 4 <button onclick="location.href='localhost:5000/';" type="button">Blink device</button></li> <!-- href is the url to blink that id -->
          <p><button onclick="location.href='localhost:5000/flash_all_lights';" type="button">Blink all device</button></p> <!-- Blinks all lights -->

          <div id="demo">
<button type="button" onclick="loadXMLDoc()">Change Content</button>
</div>

<script>
function loadXMLDoc () {
  document.getElementById("demo").innerHTML = this.responseText;
}

var oReq = new XMLHttpRequest();
oReq.addEventListener("load", loadXMLDoc);
oReq.open("GET", "http://localhost:5000/flash_all_lights");
oReq.send();

</script>
        </ul>
        
      </p>
      <!-- Display all devices, name aka watering device and id -->
      </section>
    </section>
  </article>

  <div class="footer" id="footer"></div>

</body>
</html>
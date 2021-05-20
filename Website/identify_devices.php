<!--
author: Thomas Bibby
created: 18/05/2021
-->

<?php
  //move this to shared function file for all php!
  header(
    "Access-Control-Allow-Origin", 
    "*");

  header(
    "Access-Control-Allow-Headers", 
    "Origin, X-Requested-With, Content-Type, Accept");
  
  $devices_json_obj = json_decode($output);
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
    <script src="./scripts/blinkdevices.js"></script>
  </head>
  <body>
    <div class="navbar" id="navbar"></div>

    <div class="content">
      <h3 id="demo">Device list</h3>
      <!-- Display all devices, name aka watering device and id -->
      <p> 
        <ul>
          <?php 
            foreach ($devices_json_obj as $device) {
              print("<li>" . $device->device_type . " " . $device->id . 
                " <button onclick='blinkdevice(" . $device->id . ")'>Blink Device LED</button></li>");
            }
          ?>

          <p><button type="button" onclick="flashalllights()">Blink all Devices</button></p> <!-- Blinks all lights -->
          <div id="demo"></div>
        </ul>
        
      </p>
      <!-- Display all devices, name aka watering device and id -->
    </div>

    <div class="footer" id="footer"></div>
  </body>
</html>
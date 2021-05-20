<!--
author: Thomas Bibby
created: 18/05/2021
-->
<?php
  include("./helper_functions.php");

  $api_output = curl_api_request("http://localhost:5000/get_all_devices_sensor_data");

  $devices_json_obj = json_decode($api_output);  
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
  <article>
    <div class="navbar" id="navbar">
    </div>
    
    <section id="MainSectionA">
      <section class="section1">
      <h3 id="demo">Device list</h3>
      <!-- Display all devices, name aka watering device and id -->
      <p> 
        <ul>
          <?php 
            foreach ($devices_json_obj as $device) {
              print("<li>" . $device->device_type . " " . $device->id);

              foreach($device as $key=>$value) {
                if (!in_array($key, ["id", "device_type"]))
                {
                  print("<p>" . $key . ": " . $value . "</p>");
                }
              }

              print("</li>");
            }
          ?>

          <div id="demo"></div>
        </ul>
        
      </p>
      <!-- Display all devices, name aka watering device and id -->
      </section>
    </section>
  </article>

  <div class="footer" id="footer"></div>

</body>
</html>
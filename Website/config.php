<!--
author: Thomas Bibby
created: 18/05/2021
-->

<?php
  include("./helper_functions.php");
  $api_output = curl_api_request("http://localhost:5000/get_devices_of_type_info/WateringSystem");
  $watering_devices_json_obj = json_decode($api_output);  

  $api_output = curl_api_request("http://localhost:5000/get_devices_of_type_info/PlantMonitor");
  $plant_devices_json_obj = json_decode($api_output);  
?>

<!DOCTYPE html> 
<html lang="en">
<head>
  <title>Responsive Web Design</title>
  <meta charset="utf-8" />
  <meta name="description" content="system config" />
  <meta name="keywords" content="smart, garden, Iot, things, plants, watering" />
  <meta name="author" content="Thomas Bibby"  /> 
  <link href="styles/style.css" rel="stylesheet">
  <link href="styles/configStyle.css" rel="stylesheet">
  <link href="styles/responsive.css" rel="stylesheet">
  <script type="text/javascript" src="scripts/enchancements.js"></script>
  <script src="./scripts/jquery-3.6.0.min.js"></script>
  <script src="./scripts/loadhtml.js"></script>

  <script>
    function setDeviceBinding(trigger_obj)
    {
      var parent_obj = $(trigger_obj).parent().parent();
      var plant_id = parent_obj.attr("id");

      var selected_watering_device = parent_obj.find("#selected_water_system").find(":selected");
      var watering_id = selected_watering_device.attr("value");

      var target_moisture_level = parent_obj.find("#ThresMoisture").val();

      var oReq = new XMLHttpRequest();

      oReq.open(
        "GET", 
        "http://localhost:5000/bind_watering_to_plant/?watering_id=" + watering_id + "&plant_id=" + plant_id + "&target_moisture=" + target_moisture_level);
      oReq.send();
    }

    function removeAnyDeviceBinding(trigger_obj)
    {
      var parent_obj = $(trigger_obj).parent().parent();
      var plant_id = parent_obj.attr("id");

      var oReq = new XMLHttpRequest();

      oReq.open(
        "GET", 
        "http://localhost:5000/remove_bind_watering_to_plant/" + plant_id);
      oReq.send();
    }
  </script>
 </head>
<body>
  <a name="top"></a>
<article>
  <div class="navbar" id="navbar">
  </div>

  <div class="content">

    <h3>System Configuration</h3>

    <?php
      foreach ($plant_devices_json_obj as $device) {
        print("<fieldset id='" . $device->id  . "'>");
        print("<legend>Plant Monitor " . $device->id . "</legend>");
        print('<p><label for="Device">Watering Device:</label> ');
        print('<select name="selected_water_system" id="selected_water_system">');

        foreach ($watering_devices_json_obj as $device) 
        {
          print("<option value=" . $device->id  . ">" . "Watering Device " . $device->id .  "</option>");
        }
        print("</select></p>");

        print('<p><label for="Moisture">Threshold Moisture (%):</label>');
        print('<input type="text" name= "Moisture" id="ThresMoisture" pattern="\d{0,9}" placeholder="30"/>');
        print("</p>");


        print('<button value="Bind devices"  id="bind_devices" onclick="setDeviceBinding(this)">Bind Devices</button>');
        print('<button value="Remove Any Bindings"  id="remove_any_binding" onclick="removeAnyDeviceBinding(this)">Remove Any Bindings</button>');


        print("</fieldset>");
      } 
    ?>
  </div>

<div class="footer" id="footer"></div>

</body>
</html>
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
    <title>Enquire</title>
    <meta charset="utf-8" />
    <meta name="description" content="manual watering" />
    <meta name="keywords" content="smart, garden, Iot, things, plants, watering" />
    <meta name="author" content="Thomas Bibby"  /> 
    <link href="styles/style.css" rel="stylesheet">
    <link href="styles/mwateringStyle.css" rel="stylesheet">
    <link href="styles/responsive.css" rel="stylesheet">
    <script src="./scripts/jquery-3.6.0.min.js"></script>
    <script src="./scripts/loadhtml.js"></script>
    <script src="./scripts/blinkdevices.js"></script>
    
    <script>
      function blinkSelectedWaterSystem()
      {
        var selected_option = $('#selected_water_system').find(":selected");
        var device_id = selected_option.attr("value");        
        blinkdevice(device_id);
      }

      function showSelectedWateringType(trigger_obj)
      {
        selected_objs = $(".watering_type");
        console.log(selected_objs);

        for (var obj of selected_objs)
        {
          $(obj).hide();
        }

        console.log($(trigger_obj).val());
        switch($(trigger_obj).val())
        {
          case "set_moisture_watering":
            $("#water_by_moisture").show();
            break;
          case "set_volume_watering":
            $("#water_by_volume").show();
            break;
        }
      }
    </script>

  </head>

  <body>
    <div class="navbar" id="navbar">
    </div>

    <div class="content"> 
    <h3 id="demo">Manual Watering Options</h3>
      <form method="post" novalidate> <!-- water_set_volume/deviceid/amount in ml-->

        <fieldset>
          <legend>Watering</legend>
          <p><label for="Device">Device:</label> 
            <select name="selected_water_system" id="selected_water_system">
              <?php
                foreach ($watering_devices_json_obj as $device) 
                {
                  print("<option value=" . $device->id  . ">" . "Watering Device " . $device->id .  "</option>");
                }
              ?> 
            </select>
          </p>
          <button type="button" onclick="blinkSelectedWaterSystem()">Blink Selected Device</button>
        </fieldset>

        <label>Water By Volume: <input type="radio" onclick="showSelectedWateringType(this)" name="watering_type" value="set_volume_watering" checked="true"/></label>
        <label>Water By Moisture: <input type="radio" onclick="showSelectedWateringType(this)" name="watering_type"  value="set_moisture_watering"/></label>

        <div id="water_by_volume" class="watering_type">
          <fieldset>
            <legend>Amount:</legend>
            <p><label for="Waterml">Water (ml):</label> 
              <input type='text' name= "Waterml" id="Waterml" pattern="\d{0,9}" placeholder="50" required="required"/>
            </p>
          </fieldset>
        </div>

        <div id="water_by_moisture" class="watering_type" style="display: none;">
        <fieldset>
          <legend>Selected Plant</legend>
          <p><label for="Device">Device:</label> 
            <select name="selected_water_system" id="selected_water_system">
              <?php
                foreach ($plant_devices_json_obj as $device) {
                  print("<option value=" . $device->id  . ">" . "Watering Device " . $device->id .  "</option>");
                }
              ?> 
            </select>
          </p>

          <p><label for="MoistureAmt">Moisture (%):</label> 
              <input type='text' name= "Waterml" id="Waterml" pattern="\d{0,9}" placeholder="50" required="required"/>
          </p>

          <button type="button" onclick="blinkSelectedWaterSystem()">Blink Selected Device</button>
        </fieldset>
        </div>

        <p>FIX ONCLICK FN</p>
        <button type="button" onclick="loadXMLDoc()">Water plants</button>

      </form> 
    </div>

    <div class="footer" id="footer"></div>
  </body>
</html>
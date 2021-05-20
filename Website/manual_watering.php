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
      function getSelectedWateringDeviceID()
      {
        var selected_option = $('#selected_water_system').find(":selected");
        var device_id = selected_option.attr("value");   
        return device_id;
      }

      function getSelectedPlantDeviceID()
      {
        var selected_option = $('#selected_plant_monitor').find(":selected");
        var device_id = selected_option.attr("value");   
        return device_id;
      }

      function blinkSelectedWaterSystem()
      {
        var device_id = getSelectedWateringDeviceID();
        blinkdevice(device_id);
      }

      function showSelectedWateringType(trigger_obj)
      {
        for (var obj of $(".watering_type"))
        {
          $(obj).hide();
        }

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

      function acuateWaterSystem()
      {
        var checked_radio_btn = $("#watering_type:checked");
        var oReq = new XMLHttpRequest();

        var device_id = getSelectedWateringDeviceID();

        console.log($(checked_radio_btn));
        var checked_radio_btn_val = $(checked_radio_btn).attr("value");
        
        console.log(checked_radio_btn_val);

        switch(checked_radio_btn_val)
        {
          case "set_volume_watering":
            var water_volume = $("#Waterml").val();

            console.log(water_volume);

            oReq.open(
              "GET", 
              "http://localhost:5000/water_set_volume/" + device_id + "/" + water_volume);
            break;
          
          case "set_moisture_watering":
            var plant_id = 

            oReq.open("GET", "http://localhost:5000/water_plant_to_target_moisture/" + device_id);
            break;
        }

        oReq.send();
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

        <label>Water By Volume: <input type="radio" onclick="showSelectedWateringType(this)" id="watering_type" name="watering_type" value="set_volume_watering" checked="true"/></label>
        <label>Water By Moisture: <input type="radio" onclick="showSelectedWateringType(this)" id="watering_type" name="watering_type"  value="set_moisture_watering"/></label>

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
            <select name="selected_plant_monitor" id="selected_plant_monitor">
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

        <button type="button" id="acuate_system" onclick="acuateWaterSystem()">Water plants</button>

      </form> 
    </div>

    <div class="footer" id="footer"></div>
  </body>
</html>
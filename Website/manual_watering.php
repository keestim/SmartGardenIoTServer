<!--
author: Thomas Bibby
created: 18/05/2021
-->

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
            <select name="DeviceD" id="DeviceD">
              <!-- this field changes depending on how many watering devices there are -->
              <option value="0">Watering Device 1</option>
              <option value="1">Watering Device 2</option>		
              <!-- this field changes depending on how many watering devices there are -->	
            </select>
          </p>
          <button type="button" onclick="blinkdevice()">Blink device</button>
        </fieldset>


        <label>Water By Volume: <input type="radio" name="watering_type" value="set_volume_watering"/></label>
        <label>Water By Moisture: <input type="radio" name="watering_type"  value="set_moisture_watering"/></label>

        <div id="water_by_volume">
          <fieldset>
          </fieldset>
        </div>

        <div id="water_by_moisture">
          <fieldset>
          </fieldset>
        </div>



          <fieldset>
            <legend>Amount:</legend>
            <p><label for="Waterml">Water (ml):</label> 
              <input type='text' name= "Waterml" id="Waterml" pattern="\d{0,9}" placeholder="50" required="required"/>
            </p>
          </fieldset>
        <p></p>
        <button type="button" onclick="loadXMLDoc()">Water plants</button>
        <input type= "reset" value="Reset Form"/>

      </form> 
    </div>

    <div class="footer" id="footer"></div>
  </body>
</html>
<!--
author: Thomas Bibby
created: 18/05/2021
-->
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
 </head>
<body>
  <a name="top"></a>
<article>
  <div class="navbar" id="navbar">
  </div>

  <div class="content">

    <h3>System Configuration</h3>
    <form onSubmit="return alert('Plant devices bound') ">
    <fieldset>
            <legend>Plant A</legend>
            <p><label for="Device">Watering Device:</label> 
              <select name="DeviceD" id="DeviceA">
                <!-- this field changes depending on how many watering devices there are -->
                <option value="Watering Device 1">Watering Device 1</option>
                <option value="Watering Device 2">Watering Device 2</option>		
                <!-- this field changes depending on how many watering devices there are -->	
              </select>     
            </p>
            <p><label for="Device">Moisture Sensor:</label> 
              <select name="DeviceD" id="DeviceA">
                <!-- this field changes depending on how many watering devices there are -->
                <option value="Watering Device 1">Watering Device 1</option>
                <option value="Watering Device 2">Watering Device 2</option>		
                <!-- this field changes depending on how many watering devices there are -->	
              </select>     
            </p>
            <p><label for="Device">Fire Sensor:</label> 
              <select name="DeviceD" id="DeviceA">
                <!-- this field changes depending on how many watering devices there are -->
                <option value="Watering Device 1">Watering Device 1</option>
                <option value="Watering Device 2">Watering Device 2</option>		
                <!-- this field changes depending on how many watering devices there are -->	
              </select>     
            </p>
            <p><label for="Moisture">Moisture (%):</label> 
              <input type='text' name= "Moisture" id="MoistureA" pattern="\d{0,9}" placeholder="30"/>
            </p>
            <input type= "submit" value="Bind devices"  id="submit" name="bindA"/>
            </fieldset>

            <fieldset>
            <legend>Plant B</legend>
            <p><label for="Device">Watering Device:</label> 
              <select name="DeviceD" id="WDeviceA">
                <!-- this field changes depending on how many watering devices there are -->
                <option value="Watering Device 1">Watering Device 1</option>
                <option value="Watering Device 2">Watering Device 2</option>		
                <!-- this field changes depending on how many watering devices there are -->	
              </select>     
            </p>
            <p><label for="Device">Moisture Sensor:</label> 
              <select name="DeviceD" id="MDeviceA">
                <!-- this field changes depending on how many watering devices there are -->
                <option value="Watering Device 1">Watering Device 1</option>
                <option value="Watering Device 2">Watering Device 2</option>		
                <!-- this field changes depending on how many watering devices there are -->	
              </select>     
            </p>
            <p><label for="Device">Fire Sensor:</label> 
              <select name="DeviceD" id="FDeviceA">
                <!-- this field changes depending on how many watering devices there are -->
                <option value="Watering Device 1">Watering Device 1</option>
                <option value="Watering Device 2">Watering Device 2</option>		
                <!-- this field changes depending on how many watering devices there are -->	
              </select>     
            </p>
            <p><label for="Moisture">Moisture (%):</label> 
              <input type='text' name= "Moisture" id="MoistureB" pattern="\d{0,9}" placeholder="30"/>
            </p>
            <input type= "submit" value="Bind devices"  id="submit" name="bindB"/>
            </fieldset>
            </form>
  </div>

<div class="footer" id="footer"></div>

</body>
</html>
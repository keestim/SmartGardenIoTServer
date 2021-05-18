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
 </head>
<body>
  <a name="top"></a>
<article>
<header><h1>Smart Garden</h1></header>
<nav>
          <ul>
            <li><a href="index.php" id="NavHome">Home</a></li>
            <li><a href="config.php" id="NavProductD">System config</a></li>
            <li><a href="mwatering.php" id="NavProductE">Manual watering</a></li>
            <li><a href="history.php" id="NavAbout">History</a></li>
          </ul>		
</nav>
<section id="MainSectionA">
<section class="section1">
<h3>System Configuration</h3>
<fieldset>
        <legend>Watering</legend>
        <p><label for="Device">Device:</label> 
          <select name="DeviceD" id="DeviceD">
            <!-- this field changes depending on how many watering devices there are -->
            <option value="Watering Device 1">Watering Device 1</option>
            <option value="Watering Device 2">Watering Device 2</option>		
            <!-- this field changes depending on how many watering devices there are -->	
          </select>
          <a><  ></a>
          <select name="DeviceD" id="DeviceD">
            <!-- this field changes depending on how many watering devices there are -->
            <option value="Watering Device 1">Watering Device 1</option>
            <option value="Watering Device 2">Watering Device 2</option>		
            <!-- this field changes depending on how many watering devices there are -->	
          </select>
          
        </p>
        <input type= "submit" value="Bind devices"  id="submit"/>
      </fieldset>
</section>
</body>
</html>
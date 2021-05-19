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
  <script type="text/javascript" src="scripts/part2.js"></script>
  
 </head>

<body>
  <a name="top"></a>
  <article>
    <header><h1>Smart Garden</h1></header>
    <div class="navbar" id="navbar">
    </div>

    <section id="section1">
      <form method="post" action="localhost:5000/water_set_volume/0/50" novalidate> <!-- water_set_volume/deviceid/amount in ml-->
        </p>
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
            <input type= "submit" value="Blink device"  id="submit"/>
          </fieldset>

          <fieldset>
            <legend>Amount:</legend>
            <p><label for="Waterml">Water (ml):</label> 
              <input type='text' name= "Waterml" id="Waterml" pattern="\d{0,9}" placeholder="50" required="required"/>
            </p>
          </fieldset>
        <p></p>
        <button type="button" onclick="loadXMLDoc()">Change Content</button>
        <input type= "reset" value="Reset Form"/>

        <script>
function loadXMLDoc () {
  console.log(this.responseText);
}
var $deviceID = document.getElementById("DeviceD");
var $volume = document.getElementById("DeviceD");;
var oReq = new XMLHttpRequest();
oReq.addEventListener("load", loadXMLDoc);
oReq.open("GET", "http://localhost:5000/water_set_volume/"$deviceID"/"$volume"");
oReq.send();

</script>

      </form> 
    </section>
  
  </article>

  <div class="footer" id="footer"></div>

</body>
</html>
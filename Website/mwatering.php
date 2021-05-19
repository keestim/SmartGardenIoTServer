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
      <form method="post" action="payment.php" novalidate>
        </p>
          <fieldset>
            <legend>Watering</legend>
            <p><label for="Device">Device:</label> 
              <select name="DeviceD" id="DeviceD">
                <!-- this field changes depending on how many watering devices there are -->
                <option value="Watering Device 1">Watering Device 1</option>
                <option value="Watering Device 2">Watering Device 2</option>		
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
        <input type= "submit" value="Confirm"  id="submit"/>
        <input type= "reset" value="Reset Form"/>
      </form> 
    </section>
  
  </article>

  <div class="footer" id="footer"></div>

</body>
</html>
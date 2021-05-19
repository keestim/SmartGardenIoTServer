<!--
author: Thomas Bibby
created: 18/05/2021
-->
<!DOCTYPE html> 
<html lang="en">
<head>
  <title>Responsive Web Design</title>
  <meta charset="utf-8" />
  <meta name="description" content="history" />
  <meta name="keywords" content="smart, garden, Iot, things, plants, watering" />
  <meta name="author" content="Thomas Bibby"  /> 
  <link href="styles/style.css" rel="stylesheet">
  <link href="styles/historyStyle.css" rel="stylesheet">
  <link href="styles/responsive.css" rel="stylesheet">
  <script src="./scripts/jquery-3.6.0.min.js"></script>
  <script src="./scripts/loadhtml.js"></script>
</head>
<body>
  <article>
  <header><h1>Smart Garden</h1></header>
  <div class="navbar" id="navbar">
  </div>
      
  <article>

  <section id="MainSectionA">
    <section class="section1">
    <h3>History</h3>
    <p>
    <?php
        error_reporting(0);
        require_once ("settings.php");

        $conn = @mysqli_connect($host,
        $user,
        $pwd,
        $sql_db
        );
        
        if (isset($_POST['query']))
        {
            $search = $_POST['querytype'];
            if (!$conn)
            {
                echo "<p>Database connection failure</p>";
            } else
            {
                    if (isset($_POST['statusupdatebtn']))
                    {
                        //CHANGES THE STATUS OF THE ORDER TO THE VALUE OF THE OPTION
                        echo "here";
                    }

                $sql_table="orders";
        
                //$make=trim($_POST["carmake"]); //whats being searched
                //$search = "Thomas Bibby";//whats being searched e.g. name,product,status,cost
                $value = $_POST['Input'];
                if ($search == "allorders")
                {
                    $query = "select order_id, order_time, product, featuresselected, quality, order_cost, nameoncard, order_status from orders;";
                }
                if ($search == "name")
                {
                    
                    $query = "select order_id, order_time, product, featuresselected, quality, order_cost, nameoncard, order_status from orders where nameoncard like '%$value%';";
                }
                if ($search == "product")
                {
                    $query = "select order_id, order_time, product, featuresselected, quality, order_cost, nameoncard, order_status from orders where product like '%$value%';";
                }
                if ($search == "status")
                {
                    
                    $query = "select order_id, order_time, product, featuresselected, quality, order_cost, nameoncard, order_status from orders where order_status like '%$value%';";
                }
                if ($search == "cost")
                {
                    
                    $query = "select order_id, order_time, product, featuresselected, quality, order_cost, nameoncard, order_status from orders where order_cost like '%$value%';";
                }

                $result = mysqli_query($conn, $query);
        
                if(!$result)
                {
                    echo "<p>something is wrong with ", $query, "</p>";
                } else
                {
                  //setups table headings
                    echo "<table border=\"1\">\n";
                    echo "<tr>\n "
                    ."<th scope=\"col\">Order_id</th>\n "
                    ."<th scope=\"col\">order_time</th>\n "
                    ."<th scope=\"col\">product</th>\n "
                    ."<th scope=\"col\">featuresselected</th>\n "
                    ."<th scope=\"col\">quality</th>\n "
                    ."<th scope=\"col\">order_cost</th>\n "
                    ."<th scope=\"col\">name</th>\n "
                    ."<th scope=\"col\">order_status</th>\n "
                    ."<th scope=\"col\">update status</th>\n "
                    ."</tr>\n ";
        
                    while ($row = mysqli_fetch_assoc($result))
                    {
                      //setups table contents
                        echo "<tr>\n ";
                        echo "<td>" , $row["order_id"] ,"</td>\n ";
                        echo "<td>" , $row["order_time"] ,"</td>\n ";
                        echo "<td>" , $row["product"] ,"</td>\n ";
                        echo "<td>" , $row["featuresselected"] ,"</td>\n ";
                        echo "<td>" , $row["quality"] ,"</td>\n ";
                        echo "<td>" , $row["order_cost"] ,"</td>\n ";
                        echo "<td>" , $row["nameoncard"] ,"</td>\n ";
                        echo "<td>" , $row["order_status"] ,"</td>\n ";
                        echo "<td>" , "<p> 
                        <select name='statusupdate' id='statusupdate'>
                          <option value='PENDING'>PENDING</option>
                          <option value='FULFILLED'>FULFILLED</option>
                          <option value='PAID'>PAID</option>
                          <option value='ARCHIVED'>ARCHIVED</option>
                        </select>
                        <input type='text' value=$row[order_id] name='idhidden' hidden/>
                      <input type='submit' value='Update' name='statusupdatebtn'/></p>" ,"</td>\n ";
                        echo "</tr>\n ";
                    }
                    echo "</table>\n ";
                    mysqli_free_result($result);
                }
                mysqli_close($conn);
            }
        }
        
    ?>
    
    </p>
    </section>
    </section>
  </article>

  <div class="footer" id="footer"></div>
</body>
</html>
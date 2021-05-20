"use strict";

$(document).ready(function (e)
{
  $("#navbar").load("./menu.html", function()
  {
    var last_url_segment = "./" + document.URL.substring(document.URL.lastIndexOf('/') + 1);
    var currentLinks = $("a[href='" + last_url_segment + "']");

    currentLinks[0].className = 'current-link';
  
  });

  $("#footer").load("./footer.html");

});



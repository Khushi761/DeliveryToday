
$(document).ready(() => {         
     //in js because js is dynamic,link between front end and back end, else will have to reload the page every 30 seconds
    var Url = location.protocol + "//" + location.host + "/notifications_count"; //building url //using location makes sure that it can be used on different machines and networks and is not specified on eoe same network 
    $.ajax({
      url: Url,    
      type: "GET",   //tells that it is a http request           
      success: function(result){  
        console.log(result)       //console.log = print of js
        $("#notification-bagde").text(result); //jquery wrps js functions in easier ways to work with
      },
      error: function(error){      //error examples: server network or network error 
        console.log(`Error ${error}`)
      }
    })

    var timer = setInterval(function(){  //setinterval acts as a loop. A function is given to it and it is told after how long it is supposed to run
      $.ajax({        //ajaz is a library in jquery   $ = jquery
        url: Url,
        type: "GET",    //url and type passed to ajaz
        success: function(result){
          console.log(result)
          $("#notification-bagde").text(result);  //modifies html element, in this case any element that has notification.badge 
        },
        error: function(error){       //error passed     
          console.log(`Error ${error}`)
        }
      })
    },30000)
  })

  //js is collecting the notification count and updating it
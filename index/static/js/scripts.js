// Function for setting overlay actions
// function on() {
//   document.getElementById("overlay").style.display = "block";
// }

function off() {
  document.getElementById("overlay").style.display = "none";
}

// Function for creating a onClick action to show loader
function ShowFunction(){
          console.log("This is the on click action")
          var x = document.getElementById("loader");
          x.style.display = "block";
}


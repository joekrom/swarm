function selected_mission(){
  var sel = document.getElementById('mission').value;

  var sm = sel;

  var mission = String(sm);
  var arm = document.getElementById('arming');
  var takeoff = document.getElementById('takeoff');
  var goto = document.getElementById('goto');
  if (arm.style.display == "none" && sm == "Arming"){

    /*if(sm=="Arming"){
        x.style.display = "block";
      }
    } else {
    x.style.display = "none";
  }*///document.getElementById('text_value').innerHTML = "Just push press to arm the drone ";
     arm.style.display = "block";
     takeoff.style.display = "none";
     goto.style.display = "none";

   } else if (goto.style.display == "none" && sm == "Goto") {
      //document.getElementById('text_value').innerHTML = "Set a single waypoint";
      goto.style.display = "block";
      arm.style.display = "none";
      takeoff.style.display = "none";

   } else if (takeoff.style.display == "none" && sm == "Takeoff"){
      //document.getElementById('text_value').innerHTML = " set a the desired altitude";
      takeoff.style.display = "block";
      goto.style.display = "none";
      arm.style.display = "none";

   } else {
     takeoff.style.display = "none";
     goto.style.display = "none";
     arm.style.display = "none";
   }

}

function set_default_mission(sel,valsearch){
  // we get the select tag
  // now we access the select tag where value is equal to default
  for ( var i = 0; i < sel.options.length; i++ ) {

        if ( sel.options[i].value == valsearch ) {

            sel.options[i].selected = true;
            sel.options[i].disabled = true;

            break;

        }

    }

}
set_default_mission(document.getElementById("mission"),"default")

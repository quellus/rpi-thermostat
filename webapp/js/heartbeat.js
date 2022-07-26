var xhr = new XMLHttpRequest()
xhr.responseType=''

var restURL = "http://" + window.location.host + ":8000/"
var heartbeat = setInterval(getStatus, 5000)
getStatus()

function getStatus() {
  xhr.onreadystatechange=(event)=>{
  console.log(event)

    if(xhr.status==200 && xhr.readyState==4){
      jsonResp = JSON.parse(xhr.responseText)
      let status = jsonResp["status"]

      if (status) {
        processStatus(status)
      }
   }
  }
  xhr.open("GET", restURL)
  xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest')
  xhr.setRequestHeader('Access-Control-Allow-Origin', '*')
  xhr.send()
}

function setTemperature() {
  let input = document.getElementById("temperature-input").value
  if (!isNaN(input) && input >= 1 && input <= 100) {
    console.log(input)
    xhr.open("PUT", restURL + "target_temperature?temperature=" + input)
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest')
    xhr.setRequestHeader('Access-Control-Allow-Origin', '*')
    xhr.send()
  }
}

function processStatus(status) {
  document.getElementById("temperature").innerHTML = status["temp"]
  document.getElementById("set-temperature").innerHTML = status["target_temp"]

  let coolerStatus = null
  let furnaceStatus = null
  let pinsStatus = status["pins"]

  if (pinsStatus["fan_on"] == true) {
    if (pinsStatus["pump"] == true) {
      coolerStatus = "Cooling"
    } else {
      coolerStatus = "Fan"
    }
    if (pinsStatus["fan_speed"] == true) {
      coolerStatus += " High"
    } else {
      coolerStatus += " Low"
    }
  } else {
    coolerStatus = "Off"
  }
  document.getElementById("cooler-status").innerHTML = coolerStatus

  if (pinsStatus["furnace"] == true) {
    furnaceStatus = "On"
  } else {
    furnaceStatus = "Off"
  }

  document.getElementById("furnace-status").innerHTML = furnaceStatus



}

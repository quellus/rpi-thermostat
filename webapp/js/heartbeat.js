var xhr = new XMLHttpRequest()
xhr.responseType=''

var restURL = "http://" + window.location.host + ":8000/"
var heartbeat = setInterval(getStatus, 2000)
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
  let temperatures = getTemperatures(status)
  document.getElementById("temperature").innerHTML = temperatures
  document.getElementById("set-temperature").innerHTML = status["target_temp"]
  document.getElementById("humidity").innerHTML = status["humidity"]
  let coolerStatus = getCoolerStatus(status)
  document.getElementById("cooler-status").innerHTML = coolerStatus
  let furnaceStatus = getFurnaceStatus(status)
  document.getElementById("furnace-status").innerHTML = furnaceStatus
}

function getTemperatures(status) {
  let temperatures = status["temperatures"]
  let tempString = ""
  let sum = 0

  for (name in temperatures) {
    let temp = temperatures[name]["temperature"]
    tempString += name + ": " + temp + "<br>"
    sum += temp
  }

  tempString += "Average: " + sum / Object.keys(temperatures).length

  return tempString
}

function getCoolerStatus(status) {
  let pinsStatus = status["pins"]
  let coolerStatus = null
  if (status["usable"]["cooler"])  {
    if (pinsStatus["pump"] == true) {
      coolerStatus = "Pump on <br>"
    } else {
      coolerStatus = "Pump off <br>"
    }
    if (pinsStatus["fan_low"] == true) {
      coolerStatus += "Fan low"
    } else if (pinsStatus["fan_high"] == true) {
      coolerStatus += "Fan high"
    } else {
      coolerStatus += "Fan off"
    }
  } else {
    coolerStatus = "Disabled"
  }
  return coolerStatus
}

function getFurnaceStatus(status) {
  let pinsStatus = status["pins"]
  if (status["usable"]["furnace"]) {
    if (pinsStatus["furnace"] == true) {
      furnaceStatus = "On"
    } else {
      furnaceStatus = "Off"
    }
  } else {
    furnaceStatus = "Disabled"
  }
  return furnaceStatus
}

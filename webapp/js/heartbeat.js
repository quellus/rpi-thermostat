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
        console.log(status)
        processStatus(status)
      }
   }
  }
  xhr.open("GET", restURL)
  xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest')
  xhr.setRequestHeader('Access-Control-Allow-Origin', '*')
  xhr.send()
}

function temperatureUp() {
  let setTemp = ++document.getElementById("set-temperature").innerHTML
  document.getElementById("set-temperature").innerHTML = setTemp
  setTemperature(setTemp)
}

function temperatureDown() {
  setTemp = --document.getElementById("set-temperature").innerHTML
  document.getElementById("set-temperature").innerHTML = setTemp
  setTemperature(setTemp)
}

function setTemperature(input) {
  if (!isNaN(input) && input >= 1 && input <= 100) {
    console.log(input)
    xhr.open("PUT", restURL + "target_temperature?temperature=" + input)
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest')
    xhr.setRequestHeader('Access-Control-Allow-Origin', '*')
    xhr.send()
  }
}

function processStatus(status) {
  let sensors = status["sensors"]
  let sensorTable = "<tr><th>Sensor</th><th>Temperature</th><th>Humidity</th></tr>"

  for (let key in sensors) {
    let sensor = sensors[key]
    sensorTable += "<tr><td>" + key + "</td><td>" + sensor["temperature"] + "</td><td>" + sensor["humidity"] + "</td></tr>"
  }
  sensorTable += "<tr><td>Average</td><td>" + status["average_temp"] + "</td></tr>"
  document.getElementById("sensors-table").innerHTML = sensorTable

  document.getElementById("set-temperature").innerHTML = status["target_temp"]

  let coolerStatus = null
  let furnaceStatus = null
  let pinsStatus = status["pins"]

  if (status["usable"]["cooler"])  {
    if (pinsStatus["pump"] == true) {
      coolerStatus = "Pump on <br>"
    } else {
      coolerStatus = "Pump off <br>"
    }
    if (pinsStatus["fan_on"] == true) {
      if (pinsStatus["fan_speed"] == true) {
        coolerStatus += "Fan high"
      } else {
        coolerStatus += "Fan low"
      }
    } else {
      coolerStatus = "Fan off"
    }
  } else {
    coolerStatus = "Disabled"
  }
  document.getElementById("cooler-status").innerHTML = coolerStatus

  if (status["usable"]["furnace"]) {
    if (pinsStatus["furnace"] == true) {
      furnaceStatus = "On"
    } else {
      furnaceStatus = "Off"
    }
  } else {
    furnaceStatus = "Disabled"
  }

  document.getElementById("furnace-status").innerHTML = furnaceStatus

}


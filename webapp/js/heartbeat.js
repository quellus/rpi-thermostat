var xhr = new XMLHttpRequest()
xhr.responseType=''

var restURL = "//" + window.location.host + ":8000/"
var heartbeat = setInterval(getStatus, 2000)
var historyHeartBeat = setInterval(getHistory, 120000)
var chart = undefined

var grafana_iframe = document.getElementById("grafana-embed-iframe")
var grafana_content = document.getElementById("grafana-embed")
var history_graph_content = document.getElementById("history-chart")
var use_grafana = false

fetch('config.json')
  .then(response => response.json())
  .then(data => {
    if (data && data["use_grafana"]) {
      use_grafana = true
      grafana_iframe.src = data["grafana_embed_url"]
      history_graph_content.style.display = 'none'
      grafana_content.style.display = 'block'
    } else {
      grafana_content.style.display = 'none'
    }
  })
  .catch(error => {
    console.error('Error fetching or parsing config JSON:', error);
  })

getStatus()
getHistory()

function getStatus() {
  xhr.onreadystatechange=(event)=>{
    if(xhr.status==200 && xhr.readyState==4){
      jsonResp = JSON.parse(xhr.responseText)
      let status = jsonResp["status"]
      let history = jsonResp["history"]

      if (status) {
        processStatus(status)
      } else if (history) {
        console.log(history)
        processHistory(history)
      }
     }
  }
  xhr.open("GET", restURL)
  xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest')
  xhr.setRequestHeader('Access-Control-Allow-Origin', '*')
  xhr.send()
}

function getHistory() {
  if (use_grafana) {
    console.log("Refreshing embedded graph")
    grafana_iframe.src = grafana_iframe.src
  } else {
    xhr.open("GET", restURL + "history")
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest')
    xhr.setRequestHeader('Access-Control-Allow-Origin', '*')
    xhr.send()
  }
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

function submitUsable() {
  let acUsable = document.getElementById("ac-usable-checkbtn").checked 
  let coolerUsable = document.getElementById("cooler-usable-checkbtn").checked 
  let furnaceUsable = document.getElementById("furnace-usable-checkbtn").checked 

  xhr.open("PUT", restURL + "usable?ac=" + acUsable + "&cooler=" + coolerUsable + "&furnace=" + furnaceUsable)
  xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest')
  xhr.setRequestHeader('Access-Control-Allow-Origin', '*')
  xhr.send()
}

function submitManualOverride() {
  let override = document.getElementById("override-checkbtn").checked

  let body = {
    pump: document.getElementById("pump-override-checkbtn").checked,
    fan_on: document.getElementById("fan-on-override-checkbtn").checked,
    ac: document.getElementById("ac-override-checkbtn").checked,
    furnace: document.getElementById("furnace-override-checkbtn").checked
  }

  xhr.open("PUT", restURL + "manual_override?override=" + override)
  xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest')
  xhr.setRequestHeader('Access-Control-Allow-Origin', '*')
  xhr.setRequestHeader('Content-Type', 'application/json')
  xhr.send(JSON.stringify(body))
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
  let sensorTable = ""

  for (let key in sensors) {
    let sensor = sensors[key]
    sensorTable += "<tr><td>" + key + "</td><td>" + parseFloat(sensor["temperature"].toFixed(2)) + "</td><td>" + parseFloat(sensor["humidity"].toFixed(2)) + "</td></tr>"
  }
  document.getElementById("avg-temp").innerHTML = parseFloat(status["average_temp"].toFixed(2))
  document.getElementById("sensors-table").innerHTML = sensorTable

  document.getElementById("set-temperature").innerHTML = status["target_temp"]

  let acStatus = "" 
  let coolerStatus = ""
  let furnaceStatus = ""
  let pinsStatus = status["pins"]

  if (status["manual_override"]) {
    document.getElementById("manual-override-indicator").style.visibility = "visible"; 
  } else {
    document.getElementById("manual-override-indicator").style.visibility = "hidden"; 
  }

  if (status["usable"]["ac"])  {
    if (pinsStatus["ac"] == true) {
      acStatus = "On"
    } else {
      acStatus = "Off"
    }
  } else {
    acStatus = "Disabled"
  }
  document.getElementById("ac-status").innerHTML = acStatus
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
      coolerStatus += "Fan off"
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

function processHistory(history) {
  const ctx = document.getElementById('history-graph');

  graphx = []
  graphy = []

  history.forEach((item) => {
    graphx.push(item[0])
    graphy.push(item[1])
  })

  if (chart) {
    chart.destroy()
  }

  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: graphx,
      datasets: [{
        data: graphy,
        borderWidth: 1,
        spanGaps: true
      }]
    },
    options: {
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
      }
    }
  })
}


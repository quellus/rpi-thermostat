#pragma once

#include <string>
#include <vector>
#include <mutex>

#include "Models.h"

class Controller{
public:
	// Fetch singleton across threads
	static Controller& getStaticObject();

	Controller() = default;

private:
	float targetTemperature;
	PinStatus pinStatus;
	PinStatus usable;
	std::vector<SensorStatus> sensorStatus;
  //std::vector<int> history; // TODO make this not an int
  
	mutable std::mutex m_mutex;
};


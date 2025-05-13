#pragma once

#include <string>
#include <vector>
#include <mutex>

class Controller{
public:
	// Fetch singleton across threads
	static Controller& getStaticObject();

	Controller() = default;

	Controller(Controller const& other);

	Controller& operator=(Controller const& other);

private:
	float targetTemperature;
	// usable
	// sensors status
	// pin status
	// manual override?
	// sensor history
	
	mutable std::mutex m_mutex;
};


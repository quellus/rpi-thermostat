#include <string>

struct PinStatus {
	bool ac = false;
	bool furnace = false;
};

struct SensorStatus {
	std::string name;
	float temperature;
	float humidity;
	int time;
};

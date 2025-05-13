#include <crow.h>
#include <iostream>
#include <string>

#include "Controller.h"

const int DEFAULT_PORT = 18080;

int main(int argc, char* argv[]) {
    crow::SimpleApp app;

    CROW_ROUTE(app, "/get_target_temperature").methods("GET"_method)([](){
        static Controller& controller = Controller::getStaticObject();
    });
}


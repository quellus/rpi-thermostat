#include "Controller.h"

Controller& Controller::getStaticObject() {
    static Controller data;
    return data;
}

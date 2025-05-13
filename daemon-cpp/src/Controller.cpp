#include "Controller.h"

Controller& Controller::getStaticObject() {
    static Controller data;
    return data;
}

Controller::Controller(Controller const& other) {
    std::unique_lock<std::mutex> lock_other(other.m_mutex);
    //inputs = other.inputs;
    //calls = other.calls;
}

Controller& Controller::operator=(Controller const& other) {
    if(&other != this)
    {
        std::unique_lock<std::mutex> lock_this(m_mutex, std::defer_lock);
        std::unique_lock<std::mutex> lock_other(other.m_mutex, std::defer_lock);

        std::lock(lock_this, lock_other);

        //inputs = other.inputs;
        //calls = other.calls;
    }

    return *this;
}


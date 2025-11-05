#include <iostream>
#include "NumSimCore/NumSimObject.h"

namespace NumSimSolver
{
    NumSimObject::NumSimObject()
        : objectName_("NumSimObject")
    {
        this->className_ = __func__;
    }

    NumSimObject::~NumSimObject()
    {
    }
}
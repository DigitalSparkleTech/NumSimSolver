#pragma once

#include "NumSimObject.h"

namespace NumSimSolver
{
    class BOOST_SYMBOL_EXPORT NumSimSimulation : public NumSimObject
    {
    public:
        NumSimSimulation();
        virtual ~NumSimSimulation();

        virtual void Initialize(boost::json::object& numSimSolverJson) {}
        virtual void PrintInfo() {}
        virtual void ReadMesh() {}
        virtual void InitFields(int flag) {}
        virtual void InitBoundaries(int flag) {}
        virtual void InitFromRestart() {}
        virtual void Solve() {}
        virtual void Post() {}
        virtual void Finalize() {}
        virtual bool IsFinished() const { return true; }
    };
}

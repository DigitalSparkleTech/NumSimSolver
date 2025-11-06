#pragma once

#include <string>

#include "NumSimObject.h"

namespace NumSimSolver
{
    class NumSimComm : public NumSimObject
    {
    public:
        NumSimComm();
        virtual ~NumSimComm();
        virtual void Initialize(boost::json::object& numSimSolverJson);
        virtual void PrintInfo() {}
        virtual void Finalize();

        inline int GetMyRank() const
        {
            return this->myRank_;
        }

        inline int GetNumProcs() const
        {
            return this->numProcs_;
        }

    private:
        // Add communication-specific members here
        int myRank_ = 0;
        int numProcs_ = 1;
    };
} // namespace NumSimSolver

#include <mpi.h>

#include "NumSimComm.h"

namespace NumSimSolver
{
    NumSimComm::NumSimComm()
    {
        this->className_ = __func__;
    }

    NumSimComm::~NumSimComm()
    {
    }

    void NumSimComm::Initialize(boost::json::object& numSimSolverJson)
    {
        MPI_Init(nullptr, nullptr);
        MPI_Comm_rank(MPI_COMM_WORLD, &this->myRank_);
        MPI_Comm_size(MPI_COMM_WORLD, &this->numProcs_);
    }

    void NumSimComm::Finalize()
    {
        MPI_Finalize();
    }
} // namespace NumSimSolver
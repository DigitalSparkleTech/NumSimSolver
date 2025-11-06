#include <iostream>

#include "NumSimFramework.h"
#include "NumSimComm.h"
#include "NumSimSimulation.h"

namespace NumSimSolver 
{
    NumSimFramework::NumSimFramework()
    {
    }

    NumSimFramework::~NumSimFramework()
    {
        if (this->comm_)
        {
            delete this->comm_;
            this->comm_ = nullptr;
        }

        for (auto simulation : this->simulations_)
        {
            delete simulation;
        }

        std::vector<NumSimSimulation*>().swap(this->simulations_);
    }

    void NumSimFramework::Initialize(boost::json::object& numSimSolverJson)
    {

    }

    void NumSimFramework::PrintInfo()
    {
        std::cout << "NumSimSolver Information:" << std::endl;

        if (this->comm_)
        {
            this->comm_->PrintInfo();
        }

        for (auto simulation : this->simulations_)
        {
            simulation->PrintInfo();
        }
    }

    void NumSimFramework::Run()
    {
        for(auto simulation : this->simulations_)
        {
            simulation->ReadMesh();
        }

        for (int flag = 0; flag < 2; ++flag)
        {
            for (auto simulation : this->simulations_)
            {
                simulation->InitFields(flag);
            }
        }

        for (int flag = 0; flag < 2; ++flag)
        {
            for (auto simulation : this->simulations_)
            {
                simulation->InitBoundaries(flag);
            }
        }

        for (auto simulation : this->simulations_)
        {
            simulation->InitFromRestart();
        }

        for (auto simulation : this->simulations_)
        {
            simulation->Post();
        }

        while (true)
        {
            bool allFinished = true;

            for (auto simulation : this->simulations_)
            {
                if (!simulation->IsFinished())
                {
                    allFinished = false;
                    simulation->Solve();
                    simulation->Post();
                }
            }

            if (allFinished)
            {
                break;
            }
        }

        for (auto simulation : this->simulations_)
        {
            simulation->Post();
        }
    }

    void NumSimFramework::Finalize()
    {
        for (auto simulation : this->simulations_)
        {
            simulation->Finalize();
        }

        if (this->comm_)
        {
            this->comm_->Finalize();
        }
    }
}
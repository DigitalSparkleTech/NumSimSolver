#pragma once

#include "NumSimObject.h"

namespace NumSimSolver 
{
    class NumSimComm;
    class NumSimSimulation;

    /**
     * @brief framework
     */
    class BOOST_SYMBOL_EXPORT NumSimFramework: public NumSimObject 
    {
    protected:
        NumSimComm* comm_ = nullptr; /**< 通信对象指针 */
        std::vector<NumSimSimulation*> simulations_; /**< 仿真对象列表 */

    public:
        NumSimFramework();
        virtual ~NumSimFramework();

    public:
        /**
         * @brief 求解器配置。
         * @param numSimSolverJson Json配置对象。
         */
        void Initialize(boost::json::object& numSimSolverJson);

        /**
         * @brief display framework information
         */
        void PrintInfo();

        /**
         * @brief run the framework
         */
        void Run();

        /**
         * @brief finalize the framework
         */
        void Finalize();

    public:
        NUMSIM_DEFINE_FACTORY_METHOD(NumSimFramework);
    }; 
}

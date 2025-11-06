#pragma once

#include <string>
#include <vector>
#include <map>
#include <boost/config.hpp>
#include <boost/container/map.hpp>
#include <boost/dll/shared_library.hpp>
#include <boost/dll/alias.hpp>
#include <boost/json.hpp>

namespace NumSimSolver {

    typedef double real_t;
    typedef unsigned int uint_t;
    typedef int int_t;

    /**
     * @brief object_class 表示一个对象的类
     * 
     * @details 提供默认的构造函数和析构函数
     */
    class BOOST_SYMBOL_EXPORT NumSimObject
    {
    public:
        NumSimObject();
        virtual ~NumSimObject();

        inline const std::string& GetObjectName() const
        {
            return this->objectName_;
        }

        inline void SetObjectName(const std::string& objectName)
        {
            this->objectName_ = objectName;
        }

        inline const std::string& GetClassName() const
        {
            return this->className_;
        }

        inline boost::json::object* GetNumSimSolverJson() const
        {
            if (this->numSimSolverJson_)
            {
                return this->numSimSolverJson_;
            }

            return nullptr;
        }

        inline void SetNumSimSolverJson(boost::json::object& numSimSolverJson)
        {
            this->numSimSolverJson_ = &numSimSolverJson;
        }

    protected:
        std::string className_;

    private:
        std::string objectName_;
        boost::json::object* numSimSolverJson_ = nullptr;
    };

#define NUMSIM_DEFINE_FACTORY_METHOD(className) \
    static className* Create() \
    { \
        return new className(); \
    }

#define NUMSIM_DLL_ALIAS(className) \
    BOOST_DLL_ALIAS(NumSimSolver::className::Create, Create##className)

#define NUMSIM_CREATE_OBJECT(classNameAndDllMaps, baseClassName, className) \
    classNameAndDllMaps[className].get_alias<baseClassName*()>((std::string("Create") + className).c_str())();
}
#include <iostream>
#include <fstream>
#include <boost/program_options.hpp>

#include "NumSimFramework.h"

int main(int argc, char* argv[])
{
    boost::program_options::options_description desc("Allowed options");
    
    desc.add_options()
        ("help,h", "produce help message")
        ("input,i", boost::program_options::value<std::string>(), "Input File");

    boost::program_options::variables_map vm;

    std::string inputFile;

    try {
        boost::program_options::store
        (
            boost::program_options::parse_command_line(argc, argv, desc),
            vm
        );
        
        boost::program_options::notify(vm);

        if (vm.count("help"))
        {
            std::cout << desc << std::endl;
            return 0;
        }

        if (vm.count("input")) {
            inputFile = vm["input"].as<std::string>();
            std::cout << "Input File: " << inputFile << std::endl;
        }
    } catch (const boost::program_options::error& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        std::cout << desc << std::endl;
        return 1;
    }

    std::cout << "Hello NumSimSolver." << std::endl;

    boost::system::error_code ec;

    boost::json::object numSimSolverJson;

    std::ifstream inputFileStream(inputFile);

    if (!inputFileStream.is_open())
    {
        throw std::runtime_error("Failed to open NumSimSolver config file: " + inputFile);
    }

    std::string inputFileContent((std::istreambuf_iterator<char>(inputFileStream)), std::istreambuf_iterator<char>());

    inputFileStream.close();

    numSimSolverJson = boost::json::parse(inputFileContent, ec).as_object();

    if (ec)
    {
        throw std::runtime_error("Failed to parse NumSimSolver config file: " + ec.message());
    }

    auto framework = NumSimSolver::NumSimFramework::Create();

    framework->SetObjectName("MainFramework");
    framework->Initialize(numSimSolverJson);
    framework->PrintInfo();
    framework->Run();
    framework->Finalize();

    delete framework;

    return 0;
}
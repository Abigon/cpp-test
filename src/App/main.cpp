#include <cstdlib>
#include <exception>
#include <fstream>
#include <print>

#include "Config.h"

int main()
{
    std::ifstream file("config.json");
    if (!file)
    {
        std::println(stderr, "config.json not found in the current directory");
        return EXIT_FAILURE;
    }

    try
    {
        const LifeExe::AppConfig config = LifeExe::parseConfig(file);
        std::println("Hello, {}! Window: {}x{}", config.title, config.width, config.height);
    }
    catch (const std::exception& e)
    {
        std::println(stderr, "{}", e.what());
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
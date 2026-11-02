#include <cstdlib>
#include <cstdio>
#include <exception>
#include <fstream>
#include <print>

#include "Config.h"

int main()
{
    try
    {
        std::ifstream file("config.json");
        if (!file)
        {
            std::println(stderr, "config.json not found in the current directory");
            return EXIT_FAILURE;
        }

        const LifeExe::AppConfig config{LifeExe::parseConfig(file)};
        std::println("Hello, {}! Window: {}x{}", config.title, config.width, config.height);
    }
    catch (const std::exception& e)
    {
        // Use std::fputs in the catch block: it is guaranteed not to throw.
        // std::println itself may throw a formatting exception.
        std::fputs(e.what(), stderr);
        std::fputs("\n", stderr);
        return EXIT_FAILURE;
    }
    catch (...)
    {
        std::fputs("Critical unknown error occurred\n", stderr);
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}

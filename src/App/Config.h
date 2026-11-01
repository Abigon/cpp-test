#pragma once

#include <istream>
#include <string>

namespace LifeExe
{

struct AppConfig
{
    std::string title;
    int width{0};
    int height{0};
};

// Reads the application configuration from a JSON stream.
// Throws std::runtime_error with the missing or invalid key name.
AppConfig parseConfig(std::istream& input);

}  // namespace LifeExe

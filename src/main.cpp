#include <cstdlib>
#include <fstream>
#include <print>
#include <string>
#include <nlohmann/json.hpp>

int main(){
    std::ifstream file("config.json");
    if (!file.is_open())
    {
        std::println(stderr, "Error: failed to open config.json");
        return EXIT_FAILURE;
    }

    try
    {
        const auto config = nlohmann::json::parse(file);

        const auto title = config.at("title").get<std::string>();
        const auto width = config.at("window").at("width").get<int>();
        const auto height = config.at("window").at("height").get<int>();

        std::println("Hello, {}! Window: {}x{}", title, width, height);
    }
    catch (const std::exception& e)
    {
        std::println(stderr, "Error parsing config: {}", e.what());
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}

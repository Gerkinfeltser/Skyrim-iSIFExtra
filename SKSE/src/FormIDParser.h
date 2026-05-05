#pragma once

namespace iSIFExtra {
    RE::FormID ParseFormID(const std::string& identifier);
    std::vector<RE::FormID> ParseFormIDArray(const Json::Value& value);
}

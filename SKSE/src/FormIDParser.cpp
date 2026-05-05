#include "FormIDParser.h"

namespace iSIFExtra {
    RE::FormID ParseFormID(const std::string& identifier) {
        std::istringstream ss{ identifier };
        std::string plugin, id;

        std::getline(ss, plugin, '|');
        std::getline(ss, id);

        RE::FormID rawFormID = 0;
        std::istringstream(id) >> std::hex >> rawFormID;

        if (plugin.empty()) {
            SKSE::log::warn("Empty plugin name in FormID: {}", identifier);
            return 0;
        }

        const auto dataHandler = RE::TESDataHandler::GetSingleton();
        if (!dataHandler)
            return 0;

        const auto* file = dataHandler->LookupModByName(plugin);
        if (!file) {
            SKSE::log::warn("Plugin not found: {}", plugin);
            return 0;
        }

        RE::FormID formID = file->compileIndex << 24;
        if (file->IsLight()) {
            formID += file->smallFileCompileIndex << 12;
        }
        formID += rawFormID;

        return formID;
    }

    std::vector<RE::FormID> ParseFormIDArray(const Json::Value& value) {
        std::vector<RE::FormID> result;

        if (value.isString()) {
            auto id = ParseFormID(value.asString());
            if (id != 0) {
                result.push_back(id);
            }
        }
        else if (value.isArray()) {
            for (const auto& elem : value) {
                if (elem.isString()) {
                    auto id = ParseFormID(elem.asString());
                    if (id != 0) {
                        result.push_back(id);
                    }
                }
            }
        }

        return result;
    }
}

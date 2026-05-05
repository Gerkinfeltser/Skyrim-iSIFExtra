#pragma once

#include "SIF_API.h"

#include <cstdint>
#include <unordered_set>
#include <vector>

namespace iSIFExtra {
    class PackageCondition : public SIF::ICondition {
    public:
        explicit PackageCondition(std::vector<RE::FormID> packageIDs);

        bool Match(RE::TESObjectREFR* ref) const override;

    private:
        std::unordered_set<RE::FormID> _packageIDs;
    };
}

#pragma once

#include "SIF_API.h"

#include <cstdint>
#include <vector>

namespace iSIFExtra {
    class FactionCondition : public SIF::ICondition {
    public:
        FactionCondition(std::vector<RE::TESFaction*> factions, int8_t minRank);

        bool Match(RE::TESObjectREFR* ref) const override;

    private:
        std::vector<RE::TESFaction*> _factions;
        int8_t _minRank;
    };
}

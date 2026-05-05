#include "FactionCondition.h"

namespace iSIFExtra {
    FactionCondition::FactionCondition(std::vector<RE::TESFaction*> factions, int8_t minRank)
        : _factions(std::move(factions)), _minRank(minRank) {}

    bool FactionCondition::Match(RE::TESObjectREFR* ref) const {
        auto* actor = ref ? ref->As<RE::Actor>() : nullptr;
        if (!actor) return false;

        for (const auto* faction : _factions) {
            if (actor->GetFactionRank(const_cast<RE::TESFaction*>(faction), false) >= _minRank)
                return true;
        }

        return false;
    }
}

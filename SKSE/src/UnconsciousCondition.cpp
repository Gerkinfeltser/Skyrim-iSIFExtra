#include "UnconsciousCondition.h"

namespace iSIFExtra {
    bool UnconsciousCondition::Match(RE::TESObjectREFR* ref) const {
        auto* actor = ref ? ref->As<RE::Actor>() : nullptr;
        if (!actor) return false;

        auto* state = actor->AsActorState();
        if (!state) return false;

        return state->GetLifeState() == RE::ACTOR_LIFE_STATE::kUnconcious;
    }
}

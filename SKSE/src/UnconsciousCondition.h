#pragma once

#include "SIF_API.h"

namespace iSIFExtra {
    class UnconsciousCondition : public SIF::ICondition {
    public:
        UnconsciousCondition() = default;

        bool Match(RE::TESObjectREFR* ref) const override;
    };
}

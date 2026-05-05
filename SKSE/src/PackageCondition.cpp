#include "PackageCondition.h"

namespace iSIFExtra {
    PackageCondition::PackageCondition(std::vector<RE::FormID> packageIDs)
        : _packageIDs(packageIDs.begin(), packageIDs.end()) {}

    bool PackageCondition::Match(RE::TESObjectREFR* ref) const {
        auto* actor = ref ? ref->As<RE::Actor>() : nullptr;
        if (!actor) return false;

        auto* process = actor->GetActorRuntimeData().currentProcess;
        if (!process) return false;

        auto* package = process->currentPackage.package;
        if (!package) return false;

        return _packageIDs.contains(package->GetFormID());
    }
}

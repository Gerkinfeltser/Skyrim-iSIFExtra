#include "FactionCondition.h"
#include "FormIDParser.h"
#include "PackageCondition.h"
#include "UnconsciousCondition.h"
#include "SIF_API.h"

#include <SKSE/SKSE.h>

using namespace iSIFExtra;

class NeverMatch : public SIF::ICondition {
    bool Match(RE::TESObjectREFR*) const override { return false; }
};

static std::unique_ptr<SIF::ICondition> BuildFaction(const Json::Value& val, RE::FormType) {
    if (!val.isObject()) return std::make_unique<NeverMatch>();

    auto ids = ParseFormIDArray(val["formId"]);
    if (ids.empty()) return std::make_unique<NeverMatch>();

    std::vector<RE::FormID> formIDs;
    for (auto id : ids) {
        auto* resolved = RE::TESForm::LookupByID(id);
        if (!resolved) continue;

        if (auto* faction = resolved->As<RE::TESFaction>()) {
            formIDs.push_back(id);
            continue;
        }

        if (auto* list = resolved->As<RE::BGSListForm>()) {
            list->ForEachForm([&](RE::TESForm* form) {
                if (form->As<RE::TESFaction>())
                    formIDs.push_back(form->GetFormID());
                return RE::BSContainer::ForEachResult::kContinue;
            });
        }
    }
    if (formIDs.empty()) return std::make_unique<NeverMatch>();

    int8_t minRank = 0;
    if (val["rank"].isNumeric())
        minRank = static_cast<int8_t>(val["rank"].asInt());
    else if (val["minRank"].isNumeric())
        minRank = static_cast<int8_t>(val["minRank"].asInt());

    std::vector<RE::TESFaction*> factions;
    for (auto id : formIDs) {
        if (auto* faction = RE::TESForm::LookupByID<RE::TESFaction>(id))
            factions.push_back(faction);
    }
    if (factions.empty()) return std::make_unique<NeverMatch>();

    return std::make_unique<FactionCondition>(std::move(factions), minRank);
}

static std::unique_ptr<SIF::ICondition> BuildPackage(const Json::Value& val, RE::FormType) {
    auto ids = ParseFormIDArray(val.isObject() ? val["formId"] : val);
    if (ids.empty()) return std::make_unique<NeverMatch>();

    std::set<RE::FormID> resolvedIDs;
    for (auto id : ids) {
        auto* resolved = RE::TESForm::LookupByID(id);
        if (!resolved) continue;

        if (auto* list = resolved->As<RE::BGSListForm>()) {
            list->ForEachForm([&](RE::TESForm* form) {
                resolvedIDs.insert(form->GetFormID());
                return RE::BSContainer::ForEachResult::kContinue;
            });
        } else {
            resolvedIDs.insert(resolved->GetFormID());
        }
    }
    if (resolvedIDs.empty()) return std::make_unique<NeverMatch>();

    return std::make_unique<PackageCondition>(std::vector<RE::FormID>(resolvedIDs.begin(), resolvedIDs.end()));
}

static std::unique_ptr<SIF::ICondition> BuildUnconscious(const Json::Value& val, RE::FormType) {
    if (!val.isBool() || !val.asBool()) return std::make_unique<NeverMatch>();
    return std::make_unique<UnconsciousCondition>();
}

SKSEPluginLoad(const SKSE::LoadInterface* skse) {
    SKSE::Init(skse);

    SIF::ListenForRegistration([](SKSE::MessagingInterface::Message* msg) {
        if (msg->type == SIF::kMessage_GetAPI) {
            auto* api = static_cast<SIF::IAPI*>(msg->data);
            if (!api) return;

            api->RegisterCondition("faction", BuildFaction);
            api->RegisterCondition("isUnconscious", BuildUnconscious);
            api->RegisterCondition("package", BuildPackage);
            SKSE::log::info("iSIFExtra: registered faction, isUnconscious, and package conditions with SIF");
        }
    });

    return true;
}

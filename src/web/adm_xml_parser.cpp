/****************************************************************************
 *
 *
 * Copyright (c) 2026 Dolby International AB.
 * All rights reserved.

 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its
 *    contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED
 * BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
 * BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 ******************************************************************************/

#include "adm_xml_parser.h"

#include <tinyxml2.h>

#include <algorithm>
#include <cctype>
#include <cstdint>
#include <cstring>
#include <map>
#include <memory>
#include <unordered_map>
#include <unordered_set>
#include <string>
#include <vector>

#include <zlib.h>

#include "model/types.hpp"

namespace {

int parse_adm_id(const char* value, const char* prefix) {
    if (!value || !prefix) {
        return 0;
    }

    const std::string id = value;
    const std::string marker = prefix;

    if (id.rfind(marker, 0) != 0 || id.size() <= marker.size()) {
        return 0;
    }

    try {
        return std::stoi(id.substr(marker.size()), nullptr, 16) - 0x1000;
    } catch (...) {
        return 0;
    }
}

std::string attr_or_empty(const tinyxml2::XMLElement* element, const char* name) {
    if (!element) {
        return {};
    }
    const char* value = element->Attribute(name);
    return value ? std::string(value) : std::string();
}

bool element_name_is(const tinyxml2::XMLElement* element, const char* localName) {
    if (!element || !localName) {
        return false;
    }

    const char* name = element->Name();
    if (!name) {
        return false;
    }

    if (std::strcmp(name, localName) == 0) {
        return true;
    }

    const char* colon = std::strrchr(name, ':');
    return colon && std::strcmp(colon + 1, localName) == 0;
}

void collect_elements_local_name(const tinyxml2::XMLElement* root,
                                 const char* localName,
                                 std::vector<const tinyxml2::XMLElement*>& out) {
    if (!root || !localName) {
        return;
    }

    if (element_name_is(root, localName)) {
        out.push_back(root);
    }

    for (auto* child = root->FirstChildElement(); child; child = child->NextSiblingElement()) {
        collect_elements_local_name(child, localName, out);
    }
}

void collect_elements(const tinyxml2::XMLElement* root,
                      const char* name,
                      std::vector<const tinyxml2::XMLElement*>& out) {
    if (!root || !name) {
        return;
    }

    if (std::strcmp(root->Name(), name) == 0) {
        out.push_back(root);
    }

    for (auto* child = root->FirstChildElement(); child; child = child->NextSiblingElement()) {
        collect_elements(child, name, out);
    }
}

const tinyxml2::XMLElement* find_first_descendant(const tinyxml2::XMLElement* root, const char* name) {
    if (!root || !name) {
        return nullptr;
    }

    if (std::strcmp(root->Name(), name) == 0) {
        return root;
    }

    for (auto* child = root->FirstChildElement(); child; child = child->NextSiblingElement()) {
        if (auto* found = find_first_descendant(child, name)) {
            return found;
        }
    }

    return nullptr;
}

std::string text_or_empty(const tinyxml2::XMLElement* element) {
    if (!element || !element->GetText()) {
        return {};
    }
    return element->GetText();
}

double parse_double_or_zero(const tinyxml2::XMLElement* element) {
    if (!element || !element->GetText()) {
        return 0.0;
    }
    try {
        return std::stod(element->GetText());
    } catch (...) {
        return 0.0;
    }
}

std::string trim_copy(std::string value) {
    const auto begin = value.find_first_not_of(" \t\n\r");
    if (begin == std::string::npos) {
        return {};
    }
    const auto end = value.find_last_not_of(" \t\n\r");
    return value.substr(begin, end - begin + 1);
}

std::string to_lower_copy(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char c) {
        return static_cast<char>(std::tolower(c));
    });
    return value;
}

bool contains_icase(const std::string& haystack, const std::string& needle) {
    if (needle.empty()) {
        return true;
    }
    return to_lower_copy(haystack).find(to_lower_copy(needle)) != std::string::npos;
}

int parse_int_or_default(const std::string& text, int fallback = -1) {
    try {
        return std::stoi(trim_copy(text));
    } catch (...) {
        return fallback;
    }
}

std::string split_camel_case(const std::string& key) {
    std::string out;
    out.reserve(key.size() + 8);
    for (std::size_t i = 0; i < key.size(); ++i) {
        const char c = key[i];
        if (i > 0 && std::isupper(static_cast<unsigned char>(c)) &&
            (std::islower(static_cast<unsigned char>(key[i - 1])) || std::isdigit(static_cast<unsigned char>(key[i - 1])))) {
            out.push_back(' ');
        }
        out.push_back(c);
    }
    return out;
}

std::string label_for_field(const std::string& key) {
    static const std::unordered_map<std::string, std::string> labels = {
        {"programConfig", "Program Configuration"},
        {"frameRateCode", "Frame Rate"},
        {"smpteTimeCode", "SMPTE Time Code"},
        {"acMod", "AC-3 Channel Mode"},
        {"bsMod", "AC-3 Bit Stream Mode"},
        {"lfeOn", "LFE Channel"},
        {"cMixLev", "Center Downmix Level"},
        {"surMixLev", "Surround Downmix Level"},
        {"dSurMod", "Dolby Surround Mode"},
        {"dialNorm", "Dialogue Normalization"},
        {"copyRightB", "Copyright Bit"},
        {"origBs", "Original Bit Stream"},
        {"langCod", "Language Code"},
        {"mixLevel", "Mixing Level"},
        {"roomTyp", "Room Type"},
        {"loRoCMixLev", "Lo/Ro Center Downmix Level"},
        {"loRoSurMixLev", "Lo/Ro Surround Downmix Level"},
        {"ltRtCMixLev", "Lt/Rt Center Downmix Level"},
        {"ltRtSurMixLev", "Lt/Rt Surround Downmix Level"},
        {"dMixMod", "Preferred Downmix Mode"},
        {"dSurExMod", "Dolby Surround EX Mode"},
        {"dHeadPhonMod", "Dolby Headphone Mode"},
        {"adConvTyp", "A/D Converter Type"},
        {"compr1", "Compression Gain Word"},
        {"dynRng1", "Dynamic Range Gain Word"},
        {"programDescriptionText", "Program Description"},
        {"hpFOn", "High-Pass Filter"},
        {"bwLpFOn", "Bandwidth Low-Pass Filter"},
        {"lfeLpFOn", "LFE Low-Pass Filter"},
        {"sur90On", "Surround 90° Phase Shift"},
        {"surAttOn", "Surround Attenuation"},
        {"rfPremphOn", "RF Pre-emphasis"},
        {"exists", "Present"}
    };

    const auto it = labels.find(key);
    if (it != labels.end()) {
        return it->second;
    }
    return split_camel_case(key);
}

std::string decode_field_value(const std::string& key, const std::string& rawValue) {
    const std::string value = trim_copy(rawValue);
    const int code = parse_int_or_default(value, -1);

    static const std::vector<std::string> programConfigText = {
        "5.1+2", "5.1+1+1", "4+4", "4+2+2", "4+2+1+1", "4+1+1+1+1", "2+2+2+2",
        "2+2+2+1+1", "2+2+1+1+1+1", "2+1+1+1+1+1+1", "1+1+1+1+1+1+1+1",
        "5.1", "4+2", "4+1+1", "2+2+2", "2+2+1+1", "2+1+1+1+1", "1+1+1+1+1+1",
        "4", "2+2", "2+1+1", "1+1+1+1", "7.1", "7.1 Screen"
    };
    static const std::vector<std::string> frameRateText = {
        "23.98 fps", "24 fps", "25 fps", "29.97 fps", "30 fps", "50 fps", "59.94 fps", "60 fps"
    };
    static const std::vector<std::string> ac3BsmodText = {
        "Complete Main", "Music and Effects", "Visually Impaired", "Hearing Impaired",
        "Dialogue", "Commentary", "Emergency", "Voice Over", "Karaoke"
    };
    static const std::vector<std::string> ac3AcmodText = {
        "1+1", "1/0", "2/0", "3/0", "2/1", "3/1", "2/2", "3/2"
    };
    static const std::vector<std::string> cMixLevText = {
        "-3 dB", "-4.5 dB", "-6 dB", "Reserved"
    };
    static const std::vector<std::string> surMixLevText = {
        "-3 dB", "-6 dB", "-∞ dB", "Reserved"
    };
    static const std::vector<std::string> dSurModText = {
        "Not Indicated", "Not Dolby Surround Encoded", "Dolby Surround Encoded", "Reserved"
    };
    static const std::vector<std::string> roomTypeText = {
        "Not Indicated", "Large Room (X-curve)", "Small Room (Flat)", "Reserved"
    };
    static const std::vector<std::string> dMixModText = {
        "Not Indicated", "Lt/Rt Preferred", "Lo/Ro Preferred", "Reserved"
    };
    static const std::vector<std::string> dSurExModText = {
        "Not Indicated", "Not Dolby Surround EX Encoded", "Dolby Surround EX Encoded", "Reserved"
    };
    static const std::vector<std::string> dHeadPhoneModText = {
        "Not Indicated", "Not Dolby Headphone Encoded", "Dolby Headphone Encoded", "Reserved"
    };
    static const std::vector<std::string> adConvTypeText = {
        "Standard", "HDCD"
    };

    const auto decode_from_table = [&](const std::vector<std::string>& table) {
        if (code >= 0 && static_cast<std::size_t>(code) < table.size()) {
            return table[static_cast<std::size_t>(code)] + " (" + value + ")";
        }
        return value;
    };

    if (key == "programConfig") return decode_from_table(programConfigText);
    if (key == "frameRateCode") return decode_from_table(frameRateText);
    if (key == "acMod") return decode_from_table(ac3AcmodText);
    if (key == "bsMod") return decode_from_table(ac3BsmodText);
    if (key == "cMixLev") return decode_from_table(cMixLevText);
    if (key == "surMixLev") return decode_from_table(surMixLevText);
    if (key == "dSurMod") return decode_from_table(dSurModText);
    if (key == "roomTyp") return decode_from_table(roomTypeText);
    if (key == "dMixMod") return decode_from_table(dMixModText);
    if (key == "dSurExMod") return decode_from_table(dSurExModText);
    if (key == "dHeadPhonMod") return decode_from_table(dHeadPhoneModText);
    if (key == "adConvTyp") return decode_from_table(adConvTypeText);

    if (key == "dialNorm" && code >= 0) {
        if (code == 0) {
            return "Reserved (0)";
        }
        return "-" + std::to_string(code) + " dBFS (" + value + ")";
    }

    static const std::unordered_set<std::string> onOffFields = {
        "hpFOn", "bwLpFOn", "lfeLpFOn", "sur90On", "surAttOn", "rfPremphOn",
        "lfeOn", "copyRightB", "origBs", "exists"
    };
    if (onOffFields.find(key) != onOffFields.end() && (value == "0" || value == "1")) {
        return (value == "1" ? "On" : "Off") + std::string(" (") + value + ")";
    }

    return value;
}

void append_dolby_field(std::vector<adm_xml::DolbyEMetadataField>* fields,
                        const std::string& group,
                        const std::string& key,
                        const std::string& rawValue) {
    if (!fields) {
        return;
    }
    const std::string trimmedValue = trim_copy(rawValue);
    if (trimmedValue.empty()) {
        return;
    }
    fields->push_back({
        group,
        label_for_field(key),
        decode_field_value(key, trimmedValue)
    });
}

void collect_child_text_fields(const tinyxml2::XMLElement* parent,
                               const std::string& group,
                               std::vector<adm_xml::DolbyEMetadataField>* fields) {
    if (!parent || !fields) {
        return;
    }

    for (auto* child = parent->FirstChildElement(); child; child = child->NextSiblingElement()) {
        const std::string key = child->Name() ? child->Name() : "";
        if (key.empty()) {
            continue;
        }

        const std::string existsAttr = attr_or_empty(child, "exists");
        if (!existsAttr.empty()) {
            append_dolby_field(fields, group, key + " exists", existsAttr);
        }

        if (child->FirstChildElement() != nullptr) {
            collect_child_text_fields(child, group, fields);
            continue;
        }

        append_dolby_field(fields, group, key, text_or_empty(child));
    }
}

void extract_dolby_e_fields(const tinyxml2::XMLElement* root,
                            std::vector<adm_xml::DolbyEMetadataField>* fields) {
    if (!root || !fields) {
        return;
    }

    std::vector<const tinyxml2::XMLElement*> dbmdNodes;
    collect_elements(root, "dbmd", dbmdNodes);

    std::vector<const tinyxml2::XMLElement*> metadataSegments;
    for (const auto* dbmd : dbmdNodes) {
        collect_elements(dbmd, "metadataSegment", metadataSegments);
    }

    if (metadataSegments.empty()) {
        collect_elements(root, "metadataSegment", metadataSegments);
    }

    for (const auto* segment : metadataSegments) {
        const int segmentId = parse_int_or_default(attr_or_empty(segment, "ID"), -1);

        for (auto* item = segment->FirstChildElement(); item; item = item->NextSiblingElement()) {
            const std::string itemName = item->Name() ? item->Name() : "";

            if (itemName == "dolbyE") {
                const std::string dolbyId = attr_or_empty(item, "ID");
                const std::string group = "Dolby E" + (dolbyId.empty() ? "" : (" " + dolbyId));
                collect_child_text_fields(item, group, fields);
                continue;
            }

            if (itemName == "ac3Program") {
                const std::string programId = attr_or_empty(item, "ID");
                const std::string group = "AC-3 Program" + (programId.empty() ? "" : (" " + programId));
                collect_child_text_fields(item, group, fields);
                continue;
            }

            if (itemName == "encodeParameters") {
                const std::string encoderId = attr_or_empty(item, "ID");
                const std::string group = "Encode Parameters" + (encoderId.empty() ? "" : (" " + encoderId));
                collect_child_text_fields(item, group, fields);
                continue;
            }

            if (segmentId == 1 || segmentId == 3 || segmentId == 11) {
                const std::string group = "Metadata Segment " + std::to_string(segmentId);
                collect_child_text_fields(item, group, fields);
            }
        }
    }
}

std::vector<int> build_program_element_ids(
    const tinyxml2::XMLElement* programme,
    const std::unordered_map<std::string, std::vector<std::string>>& contentToObjectIds) {
    std::vector<int> ids;
    if (!programme) {
        return ids;
    }

    std::unordered_set<int> dedup;

    for (auto* objectRef = programme->FirstChildElement("audioObjectIDRef");
         objectRef;
         objectRef = objectRef->NextSiblingElement("audioObjectIDRef")) {
        const int id = parse_adm_id(text_or_empty(objectRef).c_str(), "AO_");
        if (id > 0 && dedup.insert(id).second) {
            ids.push_back(id);
        }
    }

    for (auto* contentRef = programme->FirstChildElement("audioContentIDRef");
         contentRef;
         contentRef = contentRef->NextSiblingElement("audioContentIDRef")) {
        const std::string contentId = text_or_empty(contentRef);
        const auto it = contentToObjectIds.find(contentId);
        if (it == contentToObjectIds.end()) {
            continue;
        }
        for (const auto& objectIdText : it->second) {
            const int id = parse_adm_id(objectIdText.c_str(), "AO_");
            if (id > 0 && dedup.insert(id).second) {
                ids.push_back(id);
            }
        }
    }

    return ids;
}

}

namespace adm_xml {

static bool parse_document(tinyxml2::XMLDocument& doc,
                           amviewer::types::metadata::sadm::SADMMetadata& model,
                           std::string& error,
                           ParseInfo* info) {
    auto* root = doc.RootElement();
    if (!root) {
        error = "XML has no root element";
        return false;
    }

    model.clear();

    const tinyxml2::XMLElement* frame = find_first_descendant(root, "frame");
    const tinyxml2::XMLElement* audioFormatExtended = find_first_descendant(root, "audioFormatExtended");

    {
        std::unordered_set<std::string> seenProfiles;

        const auto apply_profile_list = [&](const tinyxml2::XMLElement* profileList) {
            if (!profileList) {
                return;
            }

            for (auto* profile = profileList->FirstChildElement();
                 profile;
                 profile = profile->NextSiblingElement()) {
                if (!element_name_is(profile, "profile")) {
                    continue;
                }

                std::string profileName = attr_or_empty(profile, "profileName");
                if (profileName.empty()) {
                    profileName = text_or_empty(profile);
                }
                if (profileName.empty()) {
                    continue;
                }

                const std::string profileVersion = attr_or_empty(profile, "profileVersion");
                const std::string profileLevel = attr_or_empty(profile, "profileLevel");
                const std::string profileText = text_or_empty(profile);

                const std::string profileKey = profileName + "\n" + profileVersion + "\n" + profileLevel + "\n" + profileText;
                if (seenProfiles.insert(profileKey).second) {
                    std::string displayName = profileName;
                    if (!profileVersion.empty() || !profileLevel.empty()) {
                        displayName += " (";
                        bool hasPart = false;
                        if (!profileVersion.empty()) {
                            displayName += "v" + profileVersion;
                            hasPart = true;
                        }
                        if (!profileLevel.empty()) {
                            if (hasPart) {
                                displayName += ", ";
                            }
                            displayName += "L" + profileLevel;
                        }
                        displayName += ")";
                    }
                    model.admProfiles.push_back(displayName);
                }

                if (contains_icase(profileName, "dolby e adm and s-adm profile for emission")) {
                    model.isDolbyEProfile = true;
                    model.admProfile = "Dolby E ADM and S-ADM Profile for emission";
                    continue;
                }

                if (contains_icase(profileName, "advanced sound system")) {
                    if (model.admProfile.empty()) {
                        model.admProfile = "ITU-R AdvSS";
                    }
                    continue;
                }

                if (model.admProfile.empty()) {
                    model.admProfile = profileName;
                }
            }
        };

        if (frame) {
            model.sadmVersion = attr_or_empty(frame, "version");
            if (model.sadmVersion.empty()) {
                model.sadmVersion = "ITU-R_BS.2125-0";
            }

            const auto* frameHeader = frame->FirstChildElement("frameHeader");
            if (frameHeader) {
                std::vector<const tinyxml2::XMLElement*> profileLists;
                collect_elements_local_name(frameHeader, "profileList", profileLists);
                for (const auto* profileList : profileLists) {
                    apply_profile_list(profileList);
                }
            }
        }

        if (audioFormatExtended) {
            model.admVersion = attr_or_empty(audioFormatExtended, "version");
            if (model.admVersion.empty()) {
                model.admVersion = "ITU-R_BS.2076-0";
            }

            std::vector<const tinyxml2::XMLElement*> profileLists;
            collect_elements_local_name(audioFormatExtended, "profileList", profileLists);
            for (const auto* profileList : profileLists) {
                apply_profile_list(profileList);
            }
        }

        if (model.admProfile.empty()) {
            model.admProfile = "Unknown";
        }

        if (model.admProfiles.empty()) {
            model.admProfiles.push_back(model.admProfile);
        }

        extract_dolby_e_fields(root, &model.dolbyEFields);
        if (!model.dolbyEFields.empty()) {
            model.isDolbyEProfile = true;
            if (model.admProfile == "Unknown") {
                model.admProfile = "Dolby E ADM and S-ADM Profile for emission";
            }
        }
    }

    // --- Build ATU UID → transport track number map ---
    std::unordered_map<std::string, int> atuToTrack;
    {
        std::vector<const tinyxml2::XMLElement*> ttfElements;
        collect_elements(root, "transportTrackFormat", ttfElements);
        for (const auto* ttf : ttfElements) {
            for (auto* audioTrack = ttf->FirstChildElement("audioTrack");
                 audioTrack;
                 audioTrack = audioTrack->NextSiblingElement("audioTrack")) {
                int trackId = 0;
                const char* trackIdStr = audioTrack->Attribute("trackID");
                if (trackIdStr) {
                    try { trackId = std::stoi(trackIdStr); } catch (...) {}
                }
                for (auto* uidRef = audioTrack->FirstChildElement("audioTrackUIDRef");
                     uidRef;
                     uidRef = uidRef->NextSiblingElement("audioTrackUIDRef")) {
                    const std::string uid = text_or_empty(uidRef);
                    if (!uid.empty()) {
                        atuToTrack.emplace(uid, trackId);
                    }
                }
            }
        }
    }

    // --- Build audioChannelFormat ID → position data map ---
    struct PositionData { double x = 0.0, y = 0.0, z = 0.0; };
    std::unordered_map<std::string, PositionData> channelFormatPositions;
    {
        std::vector<const tinyxml2::XMLElement*> cfElements;
        collect_elements(root, "audioChannelFormat", cfElements);
        for (const auto* cf : cfElements) {
            const std::string cfId = attr_or_empty(cf, "audioChannelFormatID");
            if (cfId.empty()) continue;

            const auto* blockFormat = cf->FirstChildElement("audioBlockFormat");
            if (!blockFormat) continue;

            bool isCartesian = false;
            const auto* cartElem = blockFormat->FirstChildElement("cartesian");
            if (cartElem && cartElem->GetText()) {
                try { isCartesian = std::stoi(cartElem->GetText()) != 0; } catch (...) {}
            }

            PositionData pos;
            for (auto* posElem = blockFormat->FirstChildElement("position");
                 posElem;
                 posElem = posElem->NextSiblingElement("position")) {
                const std::string coord = attr_or_empty(posElem, "coordinate");
                const double val = parse_double_or_zero(posElem);
                if (isCartesian) {
                    if (coord == "X") pos.x = val;
                    else if (coord == "Y") pos.y = val;
                    else if (coord == "Z") pos.z = val;
                } else {
                    if (coord == "azimuth") pos.x = val;
                    else if (coord == "elevation") pos.y = val;
                    else if (coord == "distance") pos.z = val;
                }
            }
            channelFormatPositions.emplace(cfId, pos);
        }
    }

    // --- Build audioPackFormat ID → first audioChannelFormat ID map ---
    std::unordered_map<std::string, std::string> packFormatToChannelFormat;
    {
        std::vector<const tinyxml2::XMLElement*> pfElements;
        collect_elements(root, "audioPackFormat", pfElements);
        for (const auto* pf : pfElements) {
            const std::string pfId = attr_or_empty(pf, "audioPackFormatID");
            if (pfId.empty()) continue;
            const auto* cfRef = pf->FirstChildElement("audioChannelFormatIDRef");
            if (cfRef) {
                const std::string cfId = text_or_empty(cfRef);
                if (!cfId.empty()) {
                    packFormatToChannelFormat.emplace(pfId, cfId);
                }
            }
        }
    }

    // --- Build audioObject ID → classification map from audioContent dialogue ---
    std::unordered_map<std::string, int> objectIdToClassification;
    std::vector<const tinyxml2::XMLElement*> contentElements;
    collect_elements(root, "audioContent", contentElements);
    for (const auto* content : contentElements) {
        int classification = 3; // Generic default
        const auto* dialogue = content->FirstChildElement("dialogue");
        if (dialogue && dialogue->GetText()) {
            int dialogueValue = 0;
            try { dialogueValue = std::stoi(dialogue->GetText()); } catch (...) {}
            if (dialogueValue == 1) {
                const std::string ckStr = attr_or_empty(dialogue, "dialogueContentKind");
                int contentKind = 0;
                try { contentKind = std::stoi(ckStr); } catch (...) {}
                switch (contentKind) {
                    case 1: classification = 0; break; // Dialogue
                    case 2: classification = 2; break; // Voice Over
                    case 3: classification = 4; break; // Spoken Subtitle
                    case 4: classification = 1; break; // VDS / Audio Description
                    case 5: classification = 0; break; // Commentary → Dialogue
                    case 6: classification = 5; break; // Emergency Alert
                    default: classification = 3; break;
                }
            }
        }
        for (auto* objRef = content->FirstChildElement("audioObjectIDRef");
             objRef;
             objRef = objRef->NextSiblingElement("audioObjectIDRef")) {
            const std::string objId = text_or_empty(objRef);
            if (!objId.empty()) {
                objectIdToClassification.emplace(objId, classification);
            }
        }
    }

    // --- Build contentId → object ID list map (for presentations) ---
    std::unordered_map<std::string, std::vector<std::string>> contentToObjectIds;
    for (const auto* content : contentElements) {
        const std::string contentId = attr_or_empty(content, "audioContentID");
        if (contentId.empty()) continue;
        std::vector<std::string> ids;
        for (auto* ref = content->FirstChildElement("audioObjectIDRef");
             ref;
             ref = ref->NextSiblingElement("audioObjectIDRef")) {
            const std::string value = text_or_empty(ref);
            if (!value.empty()) ids.push_back(value);
        }
        contentToObjectIds.emplace(contentId, std::move(ids));
    }

    // --- Pack format ID → human-readable speaker config ---
    static const std::pair<const char*, const char*> kPackFormatNames[] = {
        {"AP_00010001", "1.0"},
        {"AP_00010002", "2.0"},
        {"AP_0001000a", "3.0"},
        {"AP_00010003", "5.1"},
        {"AP_00010013", "5.1.2"},
        {"AP_00010005", "5.1.4"},
        {"AP_00010017", "7.1.4"},
        {"AP_0001000e", "7.1"},
        {"AP_00010009", "7.1.2"},
    };
    auto speakerConfigName = [](const std::string& packId) -> std::string {
        for (const auto& kv : kPackFormatNames) {
            if (packId == kv.first) return kv.second;
        }
        return packId;
    };

    // --- Process audioObjects: beds first, then non-bed objects ---
    std::vector<const tinyxml2::XMLElement*> objectElements;
    collect_elements(root, "audioObject", objectElements);

    for (const auto* element : objectElements) {
        const auto* packRefElem = element->FirstChildElement("audioPackFormatIDRef");
        if (!packRefElem || !packRefElem->GetText()) continue;
        const std::string packId = packRefElem->GetText();
        if (packId.rfind("AP_00010", 0) != 0) continue; // Not a bed

        const double baseGain = parse_double_or_zero(element->FirstChildElement("gain"));

        auto make_bed = [&](const std::string& nameSuffix, double gainOverride) {
            amviewer::types::metadata::sadm::SADMAudioBed bed{};
            bed.id = parse_adm_id(element->Attribute("audioObjectID"), "AO_");
            bed.name = attr_or_empty(element, "audioObjectName") + nameSuffix;
            bed.source = "Direct";
            bed.config = speakerConfigName(packId);
            bed.gainDb = static_cast<float>(gainOverride);
            bed.start = 0;
            bed.end = 0;

            for (auto* uidRef = element->FirstChildElement("audioTrackUIDRef");
                 uidRef;
                 uidRef = uidRef->NextSiblingElement("audioTrackUIDRef")) {
                const std::string uid = text_or_empty(uidRef);
                const auto it = atuToTrack.find(uid);
                if (it != atuToTrack.end()) {
                    const int trackNum = it->second;
                    if (bed.start == 0) bed.start = trackNum;
                    bed.end = trackNum;
                }
            }
            return bed;
        };

        model.beds.push_back(make_bed("", baseGain));

        for (auto* avs = element->FirstChildElement("alternativeValueSet");
             avs;
             avs = avs->NextSiblingElement("alternativeValueSet")) {
            const std::string avsId = attr_or_empty(avs, "alternativeValueSetID");
            double avsGain = baseGain;
            const auto* avsGainElem = avs->FirstChildElement("gain");
            if (avsGainElem) avsGain = parse_double_or_zero(avsGainElem);
            model.beds.push_back(make_bed(":" + avsId, avsGain));
        }
    }

    for (const auto* element : objectElements) {
        const auto* packRefElem = element->FirstChildElement("audioPackFormatIDRef");
        if (packRefElem && packRefElem->GetText()) {
            const std::string packId = packRefElem->GetText();
            if (packId.rfind("AP_00010", 0) == 0) continue; // Skip beds
        }

        amviewer::types::metadata::sadm::SADMAudioObject object{};
        object.id = parse_adm_id(element->Attribute("audioObjectID"), "AO_");
        object.name = attr_or_empty(element, "audioObjectName");
        object.gainDb = static_cast<float>(parse_double_or_zero(element->FirstChildElement("gain")));
        object.diverge = false;
        object.channel = 0;
        object.x = 0.0f;
        object.y = 0.0f;
        object.z = 0.0f;

        const std::string objId = attr_or_empty(element, "audioObjectID");
        const auto classIt = objectIdToClassification.find(objId);
        object.classification = (classIt != objectIdToClassification.end()) ? classIt->second : 3;

        const auto* divergeElem = element->FirstChildElement("diverge");
        if (divergeElem && divergeElem->GetText()) {
            try { object.diverge = std::stoi(divergeElem->GetText()) != 0; } catch (...) {}
        }

        const auto* firstUidRef = element->FirstChildElement("audioTrackUIDRef");
        if (firstUidRef) {
            const auto it = atuToTrack.find(text_or_empty(firstUidRef));
            if (it != atuToTrack.end()) object.channel = it->second;
        }

        if (packRefElem && packRefElem->GetText()) {
            const std::string packId = packRefElem->GetText();
            const auto pfIt = packFormatToChannelFormat.find(packId);
            if (pfIt != packFormatToChannelFormat.end()) {
                const auto posIt = channelFormatPositions.find(pfIt->second);
                if (posIt != channelFormatPositions.end()) {
                    object.x = static_cast<float>(posIt->second.x);
                    object.y = static_cast<float>(posIt->second.y);
                    object.z = static_cast<float>(posIt->second.z);
                }
            }
        }

        model.objects.push_back(std::move(object));
    }

    // --- Process audioProgrammes ---
    std::vector<const tinyxml2::XMLElement*> programmeElements;
    collect_elements(root, "audioProgramme", programmeElements);
    for (const auto* element : programmeElements) {
        amviewer::types::metadata::sadm::SADMAudioProgramme programme{};
        programme.id = parse_adm_id(element->Attribute("audioProgrammeID"), "APR_");
        programme.name = attr_or_empty(element, "audioProgrammeName");
        programme.language = attr_or_empty(element, "audioProgrammeLanguage");
        programme.config = "5.1.4";
        programme.alternativeValueSetId = text_or_empty(element->FirstChildElement("alternativeValueSetIDRef"));
        programme.elementIds = build_program_element_ids(element, contentToObjectIds);

        int maxChannels = 0;
        for (const int elementId : programme.elementIds) {
            for (const auto& bed : model.beds) {
                if (bed.id == elementId) {
                    const int channelCount = bed.end - bed.start + 1;
                    if (channelCount > maxChannels) {
                        maxChannels = channelCount;
                        programme.config = bed.config;
                    }
                }
            }
        }

        model.programmes.push_back(std::move(programme));
    }

    if (info) {
        info->sadmVersion = model.sadmVersion;
        info->admVersion = model.admVersion;
        info->admProfile = model.admProfile;
        info->admProfiles = model.admProfiles;
        info->isDolbyEProfile = model.isDolbyEProfile;
        info->dolbyEFields = model.dolbyEFields;
    }

    return true;
}

bool parse_file(const std::string& filePath,
                amviewer::types::metadata::sadm::SADMMetadata& model,
                std::string& error,
                ParseInfo* info) {
    tinyxml2::XMLDocument doc;
    const auto result = doc.LoadFile(filePath.c_str());
    if (result != tinyxml2::XML_SUCCESS) {
        error = std::string("Failed to parse XML: ") + doc.ErrorStr();
        return false;
    }

    return parse_document(doc, model, error, info);
}


bool parse_content(const std::string& xmlContent,
                   amviewer::types::metadata::sadm::SADMMetadata& model,
                   std::string& error,
                   ParseInfo* info) {
    tinyxml2::XMLDocument doc;
    const auto result = doc.Parse(xmlContent.c_str(), xmlContent.size());
    if (result != tinyxml2::XML_SUCCESS) {
        error = std::string("Failed to parse XML content: ") + doc.ErrorStr();
        return false;
    }

    return parse_document(doc, model, error, info);
}

bool extract_st2127_xml(const std::vector<std::uint8_t>& payload,
                        std::string& xml,
                        std::string& error) {
    xml.clear();

    if (payload.size() < 11) {
        error = "Payload too small for ST2127";
        return false;
    }

    std::size_t index = 0;

    const std::uint8_t identifier = payload[index++];
    if (identifier != 2) {
        error = "Invalid ST2127 identifier";
        return false;
    }

    if (payload.size() < index + 4) {
        error = "Invalid ST2127 length field";
        return false;
    }
    index += 4;

    const std::uint8_t payloadTag = payload[index++];
    if (payloadTag != 0x12) {
        error = "Invalid ST2127 payload tag";
        return false;
    }

    if (payload.size() <= index) {
        error = "Invalid ST2127 BER length";
        return false;
    }

    std::uint8_t length2Byte = payload[index++];
    if (length2Byte & 0x80) {
        const std::size_t octets = static_cast<std::size_t>(length2Byte & 0x7f);
        if (payload.size() < index + octets) {
            error = "Invalid ST2127 BER extended length";
            return false;
        }
        index += octets;
    }

    if (payload.size() <= index + 1) {
        error = "Invalid ST2127 version/format";
        return false;
    }

    const std::uint8_t version = payload[index++];
    if (version != 0) {
        error = "Unsupported ST2127 version";
        return false;
    }

    const std::uint8_t format = payload[index++];
    if (format > 1) {
        error = "Unsupported ST2127 format";
        return false;
    }

    if (payload.size() < index) {
        error = "Invalid ST2127 payload offset";
        return false;
    }

    if (format == 0) {
        std::string uncompressed(reinterpret_cast<const char*>(payload.data() + index), payload.size() - index);
        while (!uncompressed.empty() && uncompressed.back() == '\0') {
            uncompressed.pop_back();
        }
        xml = std::move(uncompressed);
        return true;
    }

    const auto* compressedPtr = reinterpret_cast<const Bytef*>(payload.data() + index);
    const uLong compressedSize = static_cast<uLong>(payload.size() - index);
    if (compressedSize == 0) {
        error = "Empty compressed ST2127 payload";
        return false;
    }

    z_stream stream{};
    stream.next_in = const_cast<Bytef*>(compressedPtr);
    stream.avail_in = compressedSize;

    if (inflateInit2(&stream, 15 + 32) != Z_OK) {
        error = "Failed to initialize gzip inflater";
        return false;
    }

    std::string output;
    constexpr std::size_t kChunk = 8192;
    std::uint8_t buffer[kChunk];
    int ret = Z_OK;

    while (ret == Z_OK) {
        stream.next_out = buffer;
        stream.avail_out = static_cast<uInt>(kChunk);
        ret = inflate(&stream, Z_NO_FLUSH);

        const std::size_t produced = kChunk - stream.avail_out;
        output.append(reinterpret_cast<const char*>(buffer), produced);
    }

    inflateEnd(&stream);

    if (ret != Z_STREAM_END) {
        error = "Failed to decompress ST2127 gzip payload";
        return false;
    }

    xml = std::move(output);
    return true;
}

bool extract_st2116_xml(const std::vector<std::uint8_t>& payload,
                        int bitDepth,
                        bool assembleFlag,
                        bool formatFlag,
                        std::string& xml,
                        std::string& error) {
    xml.clear();

    if (payload.empty()) {
        error = "Empty ST2116 payload";
        return false;
    }

    if (bitDepth != 20 && bitDepth != 24) {
        error = "Unsupported ST2116 bit depth";
        return false;
    }

    auto get_word = [&](std::size_t byteIndex) -> std::uint32_t {
        if (byteIndex + 2 >= payload.size()) {
            return 0;
        }
        const std::uint32_t b0 = static_cast<std::uint8_t>(payload[byteIndex]);
        const std::uint32_t b1 = static_cast<std::uint8_t>(payload[byteIndex + 1]);
        const std::uint32_t b2 = static_cast<std::uint8_t>(payload[byteIndex + 2]);
        const std::uint32_t sample = (b0 << 16) | (b1 << 8) | b2;
        return sample >> (24 - bitDepth);
    };

    std::size_t indexBytes = 0;
    int formatType = 0;

    if (assembleFlag) {
        const std::uint32_t assembleInfo = get_word(indexBytes);
        const int inTimelineFlag = static_cast<int>((assembleInfo >> 4) & 0x3);
        if (inTimelineFlag != 0) {
            error = "Unsupported ST2116 in-timeline mode";
            return false;
        }
        indexBytes += static_cast<std::size_t>((bitDepth + 7) / 8);
    }

    if (formatFlag) {
        const std::uint32_t formatInfo = get_word(indexBytes);
        formatType = static_cast<int>((formatInfo >> (bitDepth - 16)) & 0xF);
        indexBytes += static_cast<std::size_t>((bitDepth + 7) / 8);
    }

    const std::size_t byteOffset = indexBytes;
    if (byteOffset >= payload.size()) {
        error = "Invalid ST2116 payload offset";
        return false;
    }

    if (formatType == 0) {
        std::string raw(reinterpret_cast<const char*>(payload.data() + byteOffset), payload.size() - byteOffset);
        while (!raw.empty() && raw.back() == '\0') {
            raw.pop_back();
        }
        xml = std::move(raw);
        return true;
    }

    if (formatType != 1) {
        error = "Unsupported ST2116 format";
        return false;
    }

    std::vector<std::uint8_t> compressed;
    if (bitDepth == 20) {
        compressed.reserve(((payload.size() - byteOffset) / 3) * 2);
        int outputNibbleHiLo = 0;
        int outputNibbleCount = 0;
        for (std::size_t i = byteOffset; i + 2 < payload.size(); i += 3) {
            const std::uint8_t inputBytes[3] = {
                payload[i],
                payload[i + 1],
                payload[i + 2],
            };
            std::uint8_t inputNibbles[6];
            int nibbleIndex = 0;
            for (int j = 0; j < 3; ++j) {
                inputNibbles[nibbleIndex++] = static_cast<std::uint8_t>((inputBytes[j] >> 4) & 0x0F);
                inputNibbles[nibbleIndex++] = static_cast<std::uint8_t>(inputBytes[j] & 0x0F);
            }
            for (const std::uint8_t nibble : inputNibbles) {
                if (outputNibbleCount != 5) {
                    if (outputNibbleHiLo == 1) {
                        if (compressed.empty()) {
                            compressed.push_back(0);
                        }
                        compressed.back() = static_cast<std::uint8_t>(compressed.back() | nibble);
                    } else {
                        compressed.push_back(static_cast<std::uint8_t>(nibble << 4));
                    }
                    outputNibbleHiLo = 1 - outputNibbleHiLo;
                    ++outputNibbleCount;
                } else {
                    outputNibbleCount = 0;
                }
            }
        }
    } else {
        compressed.assign(payload.begin() + static_cast<std::ptrdiff_t>(byteOffset), payload.end());
    }

    if (compressed.empty()) {
        error = "Empty ST2116 compressed payload";
        return false;
    }

    z_stream stream{};
    stream.next_in = reinterpret_cast<Bytef*>(compressed.data());
    stream.avail_in = static_cast<uInt>(compressed.size());

    if (inflateInit2(&stream, 15 + 32) != Z_OK) {
        error = "Failed to initialize ST2116 gzip inflater";
        return false;
    }

    std::string output;
    constexpr std::size_t kChunk = 8192;
    std::uint8_t buffer[kChunk];
    int ret = Z_OK;

    while (ret == Z_OK) {
        stream.next_out = buffer;
        stream.avail_out = static_cast<uInt>(kChunk);
        ret = inflate(&stream, Z_NO_FLUSH);
        const std::size_t produced = kChunk - stream.avail_out;
        output.append(reinterpret_cast<const char*>(buffer), produced);
    }

    inflateEnd(&stream);

    if (ret != Z_STREAM_END) {
        error = "Failed to decompress ST2116 gzip payload";
        return false;
    }

    xml = std::move(output);
    return true;
}

}

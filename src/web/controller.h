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

#pragma once

#include "adm_xml_parser.h"
#include "app_state.h"
#include "background_service_discovery.h"
#include "capture_service.h"
#include "./dto.h"
#include "logging.h"
#include "service_discovery.h"

#include "oatpp/web/server/api/ApiController.hpp"
#include "oatpp-websocket/Handshaker.hpp"

#include <algorithm>
#include <chrono>
#include <ctime>
#include <set>
#include <sstream>
#include <mutex>
#include <memory>
#include <thread>
#include <cstdlib>

#include OATPP_CODEGEN_BEGIN(ApiController)

using namespace amviewer::dto;

class AmViewerController : public oatpp::web::server::api::ApiController,
                           public std::enable_shared_from_this<AmViewerController> {
private:
    OATPP_COMPONENT(std::shared_ptr<oatpp::network::ConnectionHandler>, websocketConnectionHandler, "websocket");
    OATPP_COMPONENT(std::shared_ptr<WebsocketConnectionListener>, websocketConnectionListener);
public:
    AmViewerController(const std::shared_ptr<ObjectMapper>& objectMapper,
                       const std::shared_ptr<AppState>& state)
        : oatpp::web::server::api::ApiController(objectMapper)
        , m_state(state) {
    }

    static std::shared_ptr<AmViewerController> createShared(std::shared_ptr<AppState> state) {
        OATPP_COMPONENT(std::shared_ptr<ObjectMapper>, objectMapper);
        return std::make_shared<AmViewerController>(objectMapper, state);
    }

    // Registers a metadata-frame callback on the CaptureService that
    // broadcasts a "metadata" envelope to all websocket peers. Call once
    // after the capture service is wired up. Uses weak ownership so the
    // capture service does not keep AppState alive via a cycle.
    void setupCaptureCallbacks() {
        if (!m_state || !m_state->captureService) {
            return;
        }
        std::weak_ptr<AppState> weakState = m_state;
        std::weak_ptr<AmViewerController> weakSelf = shared_from_this();

        m_state->captureService->setMetadataFrameCallback(
            [weakState, weakSelf]() {
                auto state = weakState.lock();
                auto self = weakSelf.lock();
                
                if (!state || !self || !state->captureService) return;

                auto captureSnapshot = state->captureService->snapshot();
                if (!captureSnapshot.active) {
                    return;
                }
                state->metadata = captureSnapshot.stream ? captureSnapshot.stream->metadata : nullptr;
                state->rtpInfo = captureSnapshot.stream ? captureSnapshot.stream->rtpInfo : nullptr;
                state->metadataFrameCounter = captureSnapshot.frameCount;
                state->metadataTimestampMs = captureSnapshot.packetTimestampMs;
                self->broadcastEnvelope(self->buildMetadataEnvelope());
            });
    }

    // Registers a welcome handler that, on each new websocket connection,
    // sends a full snapshot of the current state so the client does not need
    // to wait for the next delta. Call once at startup.
    void setupWelcomeHandler() {
        std::weak_ptr<AmViewerController> weakSelf = shared_from_this();
        OATPP_COMPONENT(std::shared_ptr<oatpp::data::mapping::ObjectMapper>, objectMapper);
        auto mapper = objectMapper;

        websocketConnectionListener->setWelcomeHandler(
            [weakSelf, mapper](const std::shared_ptr<WebsocketPeer>& peer) {
                auto self = weakSelf.lock();
                if (!self || !peer) return;

                peer->sendMessage(mapper->writeToString(self->buildInterfaceEnvelope()));
                peer->sendMessage(mapper->writeToString(self->buildServiceEnvelope()));
                peer->sendMessage(mapper->writeToString(self->buildCaptureEnvelope()));
                peer->sendMessage(mapper->writeToString(self->buildMetadataEnvelope()));
            });
    }

    // Registers a callback on BackgroundServiceDiscovery so that every time
    // the discovered-services set changes, we push a "services" envelope to
    // all websocket peers. buildServiceEnvelope() reads live from the
    // discovery singleton, so we don't cache anything on AppState here.
    void setupDiscoveryCallbacks() {
        std::weak_ptr<AmViewerController> weakSelf = shared_from_this();
        OATPP_COMPONENT(std::shared_ptr<oatpp::data::mapping::ObjectMapper>, objectMapper);
        auto mapper = objectMapper;
        auto listener = websocketConnectionListener;
        auto previousIds = std::make_shared<std::set<std::string>>();

        BackgroundServiceDiscovery::instance().set_services_changed_callback(
            [weakSelf, mapper, listener, previousIds](std::vector<DiscoveredService> services) {
                auto self = weakSelf.lock();
                if (!self) return;

                std::set<std::string> currentIds;
                for (const auto& s : services) {
                    std::ostringstream id;
                    id << s.system << "|" << s.name << "|" << s.address << ":" << s.port;
                    currentIds.insert(id.str());
                }
                std::vector<std::string> added;
                std::vector<std::string> removed;
                std::set_difference(currentIds.begin(), currentIds.end(),
                                    previousIds->begin(), previousIds->end(),
                                    std::back_inserter(added));
                std::set_difference(previousIds->begin(), previousIds->end(),
                                    currentIds.begin(), currentIds.end(),
                                    std::back_inserter(removed));
                if (!added.empty() || !removed.empty()) {
                    auto join = [](const std::vector<std::string>& v) {
                        std::ostringstream o;
                        for (size_t i = 0; i < v.size(); ++i) {
                            if (i) o << ", ";
                            o << v[i];
                        }
                        return o.str();
                    };
                    AMV_LOG_INFO("discovery.changed count={} added=[{}] removed=[{}]",
                                 currentIds.size(), join(added), join(removed));
                }
                *previousIds = std::move(currentIds);

                auto envelope = self->buildServiceEnvelope();
                oatpp::String json = mapper->writeToString(envelope);
                listener->broadcast(json);
            });
    }

        ENDPOINT("GET", "/", root) {
                static const char* kHtml = R"HTML(<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>AM-Viewer Backend</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; max-width: 760px; margin: 2rem auto; line-height: 1.45; padding: 0 1rem; }
            code { background: #f2f2f2; padding: 0.1rem 0.35rem; border-radius: 4px; }
        </style>
    </head>
    <body>
        <h1>AM-Viewer backend is running</h1>
        <p>This service exposes API endpoints and does not host the SvelteKit app directly in development mode.</p>
        <ul>
            <li>Health: <a href="/api/health">/api/health</a></li>
            <li>Model summary: <a href="/api/model">/api/model</a></li>
        </ul>
        <p>For the web UI, run the frontend dev server and open <code>http://localhost:5173</code>.</p>
    </body>
</html>)HTML";

                auto response = createResponse(Status::CODE_200, kHtml);
                response->putHeader("Content-Type", "text/html; charset=utf-8");
                return response;
        }

    ENDPOINT("GET", "/api/health", health) {
        auto dto = StatusDto::createShared();
        dto->status = "ok";
        dto->message = "Service is healthy";
        return createDtoResponse(Status::CODE_200, dto);
    }


    /**
     * List available capture interfaces.
     */
    ENDPOINT("GET", "/api/interfaces", interfaces) {
        auto list = oatpp::List<oatpp::String>::createShared();
        for (const auto& name : CaptureService::list_interfaces()) {
            list->push_back(name.c_str());
        }
        return createDtoResponse(Status::CODE_200, list);
    }


    /**
     * Gets the currently selected interface as a plain string.
     */
    ENDPOINT("GET", "/api/interface", listInterfaces) {
        std::string selectedInterface;
        {
            std::lock_guard<std::mutex> lock(m_state->mutex);
            selectedInterface = m_state->selectedService ? m_state->selectedService->interfaceName : std::string();
        }
        auto response = createResponse(Status::CODE_200, selectedInterface);
        response->putHeader("Content-Type", "text/plain; charset=utf-8");
        return response;
    }

    ENDPOINT("POST", "/api/interface", setInterface,
             REQUEST(std::shared_ptr<IncomingRequest>, request)) {
        // Body of the request should be text/plain with the interface name to select
        auto body = request->readBodyToString();
        std::string newIface = body ? *body : std::string();

        if(newIface.empty()) {
            auto dto = StatusDto::createShared();
            dto->status = "error";
            dto->message = "Request body must contain the interface name";
            return createDtoResponse(Status::CODE_400, dto);
        }

        std::string oldIface;
        bool changed = false;
        {
            std::lock_guard<std::mutex> lock(m_state->mutex);
            oldIface = m_state->selectedService ? m_state->selectedService->interfaceName : std::string();
            AMV_LOG_INFO("state.interface current=\"{}\" new=\"{}\"", oldIface, newIface);
            if (oldIface != newIface) {
                if (!m_state->selectedService) {
                    m_state->selectedService = std::make_unique<ServiceSelection>();
                }
                m_state->selectedService->interfaceName = newIface;
                BackgroundServiceDiscovery::instance().set_interface(newIface);

                changed = true;
            }
        }
        if (changed) {
            broadcastInterfaceUpdate();
        }

        auto dto = StatusDto::createShared();
        dto->status = "ok";
        dto->message = changed ? "Interface updated" : "Interface unchanged";
        return createDtoResponse(Status::CODE_200, dto);
    }



    /**
     * Discovers available services on the specified interface and returns them as JSON. 
     * Also updates the current interface selection which may trigger a capture restart. 
     * The timeoutMs query parameter is currently ignored but may be used in the future 
     * to specify how long the discovery process should run before returning results.
     * DEPRECATED: Use POST /api/interface to set the interface and either GET /api/services 
     * for a snapshot or the "services" websocket envelope for real-time updates instead.
     */
    ENDPOINT("GET", "/api/services/discover", discoverServices,
             QUERY(String, interfaceName, "interface"),
             QUERY(Int32, timeoutMs, "timeoutMs")) {
        const std::string iface = interfaceName ? std::string(interfaceName) : std::string();
        (void)timeoutMs;

        BackgroundServiceDiscovery::instance().set_interface(iface);
        const auto services = BackgroundServiceDiscovery::instance().snapshot();

        auto list = oatpp::List<oatpp::Object<DiscoveredServiceDto>>::createShared();
        for (const auto& service : services) {
            auto dto = DiscoveredServiceDto::createShared();
            dto->name = service.name.c_str();
            dto->system = service.system.c_str();
            dto->address = service.address.c_str();
            dto->port = service.port;
            dto->codec = service.codec.c_str();
            dto->channels = service.channels;
            dto->sampleRate = service.sampleRate;
            dto->sdpText = service.sdpText.c_str();
            list->push_back(dto);
        }

        return createDtoResponse(Status::CODE_200, list);
    }

    /**
     * Returns a list of currently discovered services on the selected interface. 
     * This is a snapshot of the current state and does not trigger any discovery 
     * process. For real-time updates, use the websocket "services" envelope instead.
     */
    ENDPOINT("GET", "/api/services", getSelectedServices) {
        const auto services = BackgroundServiceDiscovery::instance().snapshot();

        auto list = oatpp::List<oatpp::Object<DiscoveredServiceDto>>::createShared();
        for (const auto& service : services) {
            auto dto = DiscoveredServiceDto::createShared();
            dto->name = service.name.c_str();
            dto->system = service.system.c_str();
            dto->address = service.address.c_str();
            dto->port = service.port;
            dto->codec = service.codec.c_str();
            dto->channels = service.channels;
            dto->sampleRate = service.sampleRate;
            dto->sdpText = service.sdpText.c_str();
            list->push_back(dto);
        }

        return createDtoResponse(Status::CODE_200, list);
    }
    
    /**
     * Returns the currently selected service which may or may not be among the discovered services.
     */
    ENDPOINT("GET", "/api/service", getSelectedService) {
        auto dto = ServiceSelectionDto::createShared();
        {
            std::lock_guard<std::mutex> lock(m_state->mutex);
            if (m_state->selectedService) {
                dto->name = m_state->selectedService->name;
                dto->system = m_state->selectedService->system;
                dto->interfaceName = m_state->selectedService->interfaceName;
                dto->address = m_state->selectedService->address;
                dto->port = static_cast<v_int32>(m_state->selectedService->port);
                dto->codec = m_state->selectedService->codec;
                dto->audio = m_state->selectedService->audio;
                dto->sampleRate = static_cast<v_int32>(m_state->selectedService->sampleRate);
            }
        }
        return createDtoResponse(Status::CODE_200, dto);
    }

    ENDPOINT("POST", "/api/service/clear", clearService) {
        std::string previousInterface;
        std::string previousName;
        {
            std::lock_guard<std::mutex> lock(m_state->mutex);
            if (m_state->selectedService) {
                previousInterface = m_state->selectedService->interfaceName;
                previousName = m_state->selectedService->name;
            }
            m_state->selectedService = std::make_unique<ServiceSelection>();
        }

        AMV_LOG_INFO("state.service cleared old=\"{}\" iface=\"{}\"", previousName, previousInterface);

        if (!previousInterface.empty()) {
            broadcastInterfaceUpdate();
        }
        broadcastServiceUpdate();

        auto dto = StatusDto::createShared();
        dto->status = "ok";
        dto->message = "Service selection cleared";
        return createDtoResponse(Status::CODE_200, dto);
    }

    /**
     * Accepts raw SDP text in the request body, parses it to extract the
     * multicast address, port and codec, then starts the capture service
     * with those parameters. The currently selected interface is reused;
     * pass an 'interface' query parameter to override it.
     */
    ENDPOINT("POST", "/api/service/sdp", setServiceFromSdp,
             BODY_STRING(String, body)) {
        if (!body || body->empty()) {
            AMV_LOG_WARN("Received request to set service from SDP with empty body");
            auto dto = StatusDto::createShared();
            dto->status = "error";
            dto->message = "Request body must contain SDP text";
            return createDtoResponse(Status::CODE_400, dto);
        }

        const DiscoveredService parsed = parse_sdp(std::string(body));

        if (parsed.address.empty() || parsed.port <= 0) {
            AMV_LOG_WARN("SDP does not contain a valid multicast address and port");
            auto dto = StatusDto::createShared();
            dto->status = "error";
            dto->message = "SDP does not contain a valid multicast address and port";
            return createDtoResponse(Status::CODE_400, dto);
        }
        if (parsed.codec.empty()) {
            AMV_LOG_WARN("SDP does not contain a recognised codec (expected AM824 or ST2110-41)");
            auto dto = StatusDto::createShared();
            dto->status = "error";
            dto->message = "SDP does not contain a recognised codec (expected AM824 or ST2110-41)";
            return createDtoResponse(Status::CODE_400, dto);
        }

        std::string iface;
        {
            std::lock_guard<std::mutex> lock(m_state->mutex);
            if (m_state->selectedService) {
                iface = m_state->selectedService->interfaceName;
            }
        }

        if (iface.empty()) {
            AMV_LOG_WARN("No interface selected for SDP service");
            auto dto = StatusDto::createShared();
            dto->status = "error";
            dto->message = "No interface selected — pass ?interface= or select one first";
            return createDtoResponse(Status::CODE_400, dto);
        }

        if (!m_state->captureService) {
            AMV_LOG_WARN("Attempted to set service from SDP but capture service is not available");
            auto dto = StatusDto::createShared();
            dto->status = "error";
            dto->message = "Capture service is not available";
            return createDtoResponse(Status::CODE_500, dto);
        }

        if (m_state->captureService->running()) {
            m_state->captureService->stop();
        }

        std::string error;
        const bool ok = m_state->captureService->start(iface, parsed.address, parsed.port, parsed.codec, parsed.sampleRate, error);
        if (!ok) {

            auto dto = StatusDto::createShared();
            dto->status = "error";
            dto->message = "Failed to start capture: " + error;
            AMV_LOG_ERROR("Failed to start capture service with interface=\"{}\" address=\"{}\" port={} codec=\"{}\": {}", iface, parsed.address, parsed.port, parsed.codec, error);
            return createDtoResponse(Status::CODE_500, dto);
        }

        std::string previousInterface;
        {
            std::lock_guard<std::mutex> lock(m_state->mutex);
            if (!m_state->selectedService) {
                m_state->selectedService = std::make_unique<ServiceSelection>();
            }
            previousInterface = m_state->selectedService->interfaceName;
            m_state->selectedService->interfaceName = iface;
            m_state->selectedService->name = parsed.name;
            m_state->selectedService->system = "SDP";
            m_state->selectedService->address = parsed.address;
            m_state->selectedService->port = parsed.port;
            m_state->selectedService->codec = parsed.codec;
            m_state->selectedService->sampleRate = parsed.sampleRate;
        }

        AMV_LOG_INFO("state.service.sdp name=\"{}\" iface=\"{}\" addr={}:{} codec={}",
                     parsed.name, iface, parsed.address, parsed.port, parsed.codec);

        if (previousInterface != iface) {
            broadcastInterfaceUpdate();
        }
        broadcastServiceUpdate();
        broadcastCaptureUpdate();

        auto dto = StatusDto::createShared();
        dto->status = "ok";
        dto->message = "Service configured from SDP";
        return createDtoResponse(Status::CODE_200, dto);
    }

    /**
     * Sets the currently selected service based on the JSON body of the request.
     */
    ENDPOINT("POST", "/api/service", setService, REQUEST(std::shared_ptr<IncomingRequest>, request)) {
        // Parse service from body which should be in json format
        auto body = request->readBodyToString();
        if (!body) {
            auto dto = StatusDto::createShared();
            dto->status = "error";
            dto->message = "Request body is required";
            AMV_LOG_WARN("Received request to set service with empty body");
            return createDtoResponse(Status::CODE_400, dto);
        }
        // Reject oversized bodies and non-object JSON to guard against CVE-2025-6566 (oatpp deserializeArray stack overflow)
        static constexpr size_t kMaxBodyBytes = 16 * 1024;
        if (body->size() > kMaxBodyBytes) {
            auto dto = StatusDto::createShared();
            dto->status = "error";
            dto->message = "Request body too large";
            AMV_LOG_WARN("Rejected oversized service selection body ({} bytes)", body->size());
            return createDtoResponse(Status::CODE_400, dto);
        }
        {
            const auto* p = body->c_str();
            const auto* end = p + body->size();
            while (p < end && std::isspace(static_cast<unsigned char>(*p))) ++p;
            if (p >= end || *p != '{') {
                auto dto = StatusDto::createShared();
                dto->status = "error";
                dto->message = "Request body must be a JSON object";
                AMV_LOG_WARN("Rejected non-object JSON body for service selection");
                return createDtoResponse(Status::CODE_400, dto);
            }
        }
        OATPP_COMPONENT(std::shared_ptr<oatpp::data::mapping::ObjectMapper>, objectMapper);
        auto serviceDto = objectMapper->readFromString<oatpp::Object<ServiceSelectionDto>>(body);
        if (!serviceDto) {
            auto dto = StatusDto::createShared();
            dto->status = "error";
            dto->message = "Invalid service selection format";
            AMV_LOG_WARN("Failed to parse service selection from request body");
            return createDtoResponse(Status::CODE_400, dto);
        }

        if(!m_state->captureService) {
            auto dto = StatusDto::createShared();
            dto->status = "error";
            dto->message = "Capture service is not available";
            AMV_LOG_ERROR("Attempted to set service from SDP but capture service is not available");
            return createDtoResponse(Status::CODE_500, dto);
        }

        if(m_state->captureService->running()) {
            m_state->captureService->stop();
        }

        const int sampleRate = serviceDto->sampleRate ? static_cast<int>(serviceDto->sampleRate) : 0;

        std::string error;
        const bool ok = m_state->captureService->start(serviceDto->interfaceName, serviceDto->address, serviceDto->port, serviceDto->codec, sampleRate, error);
        if (!ok) {
            auto dto = StatusDto::createShared();
            dto->status = "error";
            dto->message = "Failed to start capture service: " + error;
            return createDtoResponse(Status::CODE_500, dto);
        }

        std::string previousInterface;
        std::string previousName;
        ServiceSelection newSelection;
        {
            std::lock_guard<std::mutex> lock(m_state->mutex);
            if (!m_state->selectedService) {
                m_state->selectedService = std::make_unique<ServiceSelection>();
            }
            previousInterface = m_state->selectedService->interfaceName;
            previousName = m_state->selectedService->name;
            m_state->selectedService->interfaceName = serviceDto->interfaceName ? std::string(serviceDto->interfaceName) : std::string();
            m_state->selectedService->name = serviceDto->name ? std::string(serviceDto->name) : std::string();
            m_state->selectedService->system = serviceDto->system ? std::string(serviceDto->system) : std::string();
            m_state->selectedService->address = serviceDto->address ? std::string(serviceDto->address) : std::string();
            m_state->selectedService->port = serviceDto->port ? static_cast<int>(serviceDto->port) : 0;
            m_state->selectedService->codec = serviceDto->codec ? std::string(serviceDto->codec) : std::string();
            m_state->selectedService->audio = serviceDto->audio ? std::string(serviceDto->audio) : std::string();
            m_state->selectedService->sampleRate = sampleRate;
            newSelection = *m_state->selectedService;
        }



        AMV_LOG_INFO("state.service old=\"{}\" new=\"{}\" iface=\"{}\" addr={}:{} codec={}",
                     previousName, newSelection.name, newSelection.interfaceName,
                     newSelection.address, newSelection.port, newSelection.codec);

        if (previousInterface != newSelection.interfaceName) {
            broadcastInterfaceUpdate();
        }
        broadcastServiceUpdate();

        auto dto = StatusDto::createShared();
        dto->status = "ok";
        dto->message = "Service selection updated";
        return createDtoResponse(Status::CODE_200, dto);
    }

    /**
     * DEPRECATED: Use POST /api/service with a JSON body instead. 
     * Sets the currently selected service based on query parameters. 
     * Used by v1 of the frontend and may be removed in the future.
     */
    ENDPOINT("POST", "/api/service/select", selectService,
             QUERY(String, interfaceName, "interface"),
             QUERY(String, name, "name"),
             QUERY(String, system, "system"),
             QUERY(String, address, "address"),
             QUERY(Int32, port, "port"),
             QUERY(String, codec, "codec"),
             QUERY(String, audio, "audio")) {
        std::string previousInterface;
        std::string previousName;
        ServiceSelection newSelection;
        {
            std::lock_guard<std::mutex> lock(m_state->mutex);
            if (!m_state->selectedService) {
                m_state->selectedService = std::make_unique<ServiceSelection>();
            }
            previousInterface = m_state->selectedService->interfaceName;
            previousName = m_state->selectedService->name;
            m_state->selectedService->interfaceName = interfaceName ? std::string(interfaceName) : std::string();
            m_state->selectedService->name = name ? std::string(name) : std::string();
            m_state->selectedService->system = system ? std::string(system) : std::string();
            m_state->selectedService->address = address ? std::string(address) : std::string();
            m_state->selectedService->port = port ? static_cast<int>(port) : 0;
            m_state->selectedService->codec = codec ? std::string(codec) : std::string();
            m_state->selectedService->audio = audio ? std::string(audio) : std::string();
            newSelection = *m_state->selectedService;
        }

        AMV_LOG_INFO("state.service old=\"{}\" new=\"{}\" iface=\"{}\" addr={}:{} codec={}",
                     previousName, newSelection.name, newSelection.interfaceName,
                     newSelection.address, newSelection.port, newSelection.codec);

        if (previousInterface != newSelection.interfaceName) {
            broadcastInterfaceUpdate();
        }
        broadcastServiceUpdate();

        auto dto = StatusDto::createShared();
        dto->status = "ok";
        dto->message = "Service selection updated";
        return createDtoResponse(Status::CODE_200, dto);
    }

    /**
     * Returns a full snapshot of the current application state including model summary, 
     * capture status, selected service, discovered interfaces, and stream info if available.
     */
    ENDPOINT("GET", "/api/ui-state", uiState) {
        auto dto = UiStateDto::createShared();
        dto->summary = ModelSummaryDto::createShared();
        dto->capture = CaptureStatusDto::createShared();
        dto->service = ServiceSelectionDto::createShared();
        dto->interfaces = oatpp::List<oatpp::String>::createShared();

        for (const auto& name : CaptureService::list_interfaces()) {
            dto->interfaces->push_back(name.c_str());
        }

        CaptureSnapshot captureSnapshot;
        bool hasCaptureSnapshot = false;
        if (m_state->captureService) {
            captureSnapshot = m_state->captureService->snapshot();
            hasCaptureSnapshot = true;
        }

        std::shared_ptr<amviewer::types::metadata::MetadataBase> metadataSource;
        uint64_t metadataTimestampMs = 0;
        uint64_t metadataFrameCounter = 0;
        {
            std::lock_guard<std::mutex> lock(m_state->mutex);
            metadataSource = m_state->metadata;
            metadataTimestampMs = m_state->metadataTimestampMs;
            metadataFrameCounter = m_state->metadataFrameCounter;


            dto->summary->loadedFile = m_state->loadedFile.c_str();
            dto->summary->lastError = m_state->lastError.c_str();
            dto->summary->lastUpdated = m_state->lastUpdated.c_str();

            if (m_state->selectedService) {
                dto->service->name = m_state->selectedService->name;
                dto->service->system = m_state->selectedService->system;
                dto->service->interfaceName = m_state->selectedService->interfaceName;
                dto->service->address = m_state->selectedService->address;
                dto->service->port = static_cast<v_int32>(m_state->selectedService->port);
                dto->service->codec = m_state->selectedService->codec;
                dto->service->audio = m_state->selectedService->audio;
                dto->service->sampleRate = static_cast<v_int32>(m_state->selectedService->sampleRate);
            }

            dto->shutdownPending = m_state->shouldShutdown.load(std::memory_order_acquire);
        }

        if(metadataSource){
            switch(metadataSource->type) {
                case amviewer::types::metadata::MetadataBase::Type::SADM:
                    dto->summary->metadata = buildSadmMetadataDto(
                        std::static_pointer_cast<amviewer::types::metadata::sadm::SADMMetadata>(metadataSource),
                        metadataTimestampMs,
                        metadataFrameCounter
                    );
                    break;
                default:
                    break;
            }
        }

        if (hasCaptureSnapshot && captureSnapshot.active && captureSnapshot.stream) {
            switch(captureSnapshot.stream->protocol) {
                case amviewer::types::streaminfo::StreamInfoBase::Protocol::ST2110_31:
                    dto->streamInfo = buildST2110_31StreamInfoDto(*captureSnapshot.stream);
                    break;
                case amviewer::types::streaminfo::StreamInfoBase::Protocol::ST2110_41:
                    dto->streamInfo = buildST2110_41StreamInfoDto(*captureSnapshot.stream, captureSnapshot.ditValue);
                    break;
                default:
                    dto->streamInfo = buildUnknownStreamInfoDto();
                    break;
            }
            dto->capture->streamInfo = dto->streamInfo;
        }

        return createDtoResponse(Status::CODE_200, dto);
    }

    /**
     * Read an XML file from disk, parse it, and update the current metadata state.
     * The file path is specified via the 'file' query parameter. The XML is parsed 
     * using the adm_xml library and must conform to the expected SADM format. 
     * If parsing is successful, the metadata state is updated accordingly.
     */
    ENDPOINT("POST", "/api/load-xml", loadXml, QUERY(String, file, "file")) {
        if (!file || file->empty()) {
            auto dto = StatusDto::createShared();
            dto->status = "error";
            dto->message = "Query parameter 'file' is required";
            return createDtoResponse(Status::CODE_400, dto);
        }

        AMV_LOG_DEBUG("Received request to load local XML file: {}", *file);

        // Stop the capture service if it's running to release any file locks and ensure a clean state for loading new metadata
        if (m_state->captureService) {
            AMV_LOG_DEBUG("Stopping capture service before loading local XML");
            m_state->captureService->stop();
        }

        const std::string filePath = file;

        auto parsed = std::make_shared<amviewer::types::metadata::sadm::SADMMetadata>();
        adm_xml::ParseInfo parseInfo;
        std::string parseError;
        const bool ok = adm_xml::parse_file(filePath, *parsed, parseError, &parseInfo);

        {
            std::lock_guard<std::mutex> lock(m_state->mutex);
            if (ok) {
                m_state->metadata = std::move(parsed);
                m_state->loadedFile = filePath;
                m_state->lastError.clear();
                m_state->lastUpdated = nowIso();
            } else {
                m_state->metadata.reset();
                m_state->lastError = parseError;
                m_state->lastUpdated = nowIso();
            }
        }
        broadcastEnvelope(buildMetadataEnvelope());

        auto dto = StatusDto::createShared();
        if (ok) {
            AMV_LOG_INFO("xml.load file=\"{}\"", filePath);
            dto->status = "ok";
            dto->message = "XML loaded";
            return createDtoResponse(Status::CODE_200, dto);
        }

        AMV_LOG_ERROR("xml.load failed file=\"{}\" error=\"{}\"", filePath, parseError);
        dto->status = "error";
        dto->message = parseError.c_str();
        return createDtoResponse(Status::CODE_400, dto);
    }

    /**
     * Parses XML content from the request body and updates the current metadata state.
     * The XML should conform to the expected SADM format. This endpoint is intended for
     * use with file uploads where the XML content is sent directly in the request body, 
     * and an optional 'fileName' query parameter can be provided for logging and display purposes.
     */
    ENDPOINT("POST", "/api/load-xml-upload", loadXmlUpload,
             QUERY(String, fileName, "name"),
             BODY_STRING(String, body)) {
        if (!body || body->empty()) {
            auto dto = StatusDto::createShared();
            dto->status = "error";
            dto->message = "Request body is empty";
            return createDtoResponse(Status::CODE_400, dto);
        }

        AMV_LOG_DEBUG("Received request to load XML from upload: name=\"{}\" size={} bytes",
                     fileName ? *fileName : "<no name>", body->size());

        // Stop the capture service if it's running to release any file locks and ensure a clean state for loading new metadata
        if (m_state->captureService) {
            AMV_LOG_DEBUG("Stopping capture service before loading uploaded XML");
            m_state->captureService->stop();
        }

        const std::string xmlContent = body;
        const std::string displayName = fileName ? std::string(fileName) : "<uploaded>";

        auto parsed = std::make_shared<amviewer::types::metadata::sadm::SADMMetadata>();
        adm_xml::ParseInfo parseInfo;
        std::string parseError;
        const bool ok = adm_xml::parse_content(xmlContent, *parsed, parseError, &parseInfo);

        {
            std::lock_guard<std::mutex> lock(m_state->mutex);
            if (ok) {
                m_state->metadata = std::move(parsed);
                m_state->loadedFile = displayName;
                m_state->metadataFrameCounter = 0;
                m_state->lastError.clear();
                m_state->lastUpdated = nowIso();
            } else {
                m_state->metadata.reset();
                m_state->lastError = parseError;
                m_state->lastUpdated = nowIso();
            }
        }
        broadcastEnvelope(buildMetadataEnvelope());

        auto dto = StatusDto::createShared();
        if (ok) {
            AMV_LOG_INFO("xml.load file=\"{}\" (uploaded, {} bytes)", displayName, xmlContent.size());
            dto->status = "ok";
            dto->message = "XML loaded";
            return createDtoResponse(Status::CODE_200, dto);
        }

        AMV_LOG_ERROR("xml.load failed file=\"{}\" error=\"{}\"", displayName, parseError);
        dto->status = "error";
        dto->message = parseError.c_str();
        return createDtoResponse(Status::CODE_400, dto);
    }


    /**
     * Returns the most recently captured live XML from the capture pipeline.
     * Returns 200 with text/xml if XML is available, or 204 No Content if
     * no live XML has been captured yet.
     */
    ENDPOINT("GET", "/api/live-xml", liveXml) {
        if (!m_state->captureService) {
            return createResponse(Status::CODE_204, "");
        }
        const auto snap = m_state->captureService->snapshot();
        if (snap.liveXml.empty()) {
            return createResponse(Status::CODE_204, "");
        }
        auto response = createResponse(Status::CODE_200, snap.liveXml);
        response->putHeader("Content-Type", "text/xml; charset=utf-8");
        return response;
    }

    ENDPOINT("POST", "/api/capture/start", startCapture,
             QUERY(String, interfaceName, "interface"),
             QUERY(String, address, "address"),
             QUERY(Int32, port, "port"),
             QUERY(String, codecParam, "codec")) {
        std::string iface;
        std::string addr;
        int capturePort = 0;
        std::string codec;
        int clockRate = 0;

        {
            std::lock_guard<std::mutex> lock(m_state->mutex);
            if(!m_state->selectedService){
                m_state->selectedService = std::make_unique<ServiceSelection>();
            }

            iface = interfaceName ? std::string(interfaceName) : (m_state->selectedService ? m_state->selectedService->interfaceName : "");
            addr = address ? std::string(address) : (m_state->selectedService ? m_state->selectedService->address : "");
            capturePort = port ? static_cast<int>(port) : (m_state->selectedService ? m_state->selectedService->port : 0);
            codec = codecParam ? std::string(codecParam) : (m_state->selectedService ? m_state->selectedService->codec : "");
            clockRate = m_state->selectedService ? m_state->selectedService->sampleRate : 0;
        }

        if (iface.empty()) {
            auto dto = StatusDto::createShared();
            dto->status = "error";
            dto->message = "Query parameter 'interface' is required";
            AMV_LOG_WARN("Failed to start capture service error=\"{}\"", "Missing required 'interface' parameter");
            return createDtoResponse(Status::CODE_400, dto);
        }

        if (!m_state->captureService) {
            auto dto = StatusDto::createShared();
            dto->status = "error";
            dto->message = "Capture service not initialized";
            AMV_LOG_WARN("Failed to start capture service iface=\"{}\" addr={}:{} codec={} error=\"{}\"",
                        iface, addr, capturePort, codec, "Capture service not initialized");
            return createDtoResponse(Status::CODE_500, dto);
        }

        std::string error;
        const bool ok = m_state->captureService->start(iface, addr, capturePort, codec, clockRate, error);


        if (!ok) {
            auto dto = StatusDto::createShared();
            dto->status = "error";
            dto->message = error.c_str();
            AMV_LOG_WARN("Failed to start capture service iface=\"{}\" addr={}:{} codec={} error=\"{}\"",
                        iface, addr, capturePort, codec, error);
            return createDtoResponse(Status::CODE_400, dto);
        }

        {
            std::lock_guard<std::mutex> lock(m_state->mutex);
            if (!m_state->selectedService) {
                m_state->selectedService = std::make_unique<ServiceSelection>();
            }
            m_state->selectedService->interfaceName = iface;
            m_state->selectedService->address = addr;
            m_state->selectedService->port = capturePort;
            m_state->selectedService->codec = codec;
            m_state->selectedService->sampleRate = clockRate;
        }

        broadcastCaptureUpdate();
        broadcastServiceUpdate();

        auto dto = StatusDto::createShared();
        dto->status = "ok";
        dto->message = "Capture started";

        AMV_LOG_DEBUG("Capture service started iface=\"{}\" addr={}:{} codec={}", iface, addr, capturePort, codec);
        return createDtoResponse(Status::CODE_200, dto);
    }

    ENDPOINT("POST", "/api/capture/stop", stopCapture) {
        if (!m_state->captureService) {
            auto dto = StatusDto::createShared();
            dto->status = "error";
            dto->message = "Capture service not initialized";
            return createDtoResponse(Status::CODE_500, dto);
        }

        m_state->captureService->stop();
        AMV_LOG_DEBUG("Capture service stopped");

        {
            std::lock_guard<std::mutex> lock(m_state->mutex);
            broadcastCaptureUpdate();
        }

        auto dto = StatusDto::createShared();
        dto->status = "ok";
        dto->message = "Capture stopped";
        return createDtoResponse(Status::CODE_200, dto);
    }

    /**
     * DEPRECATED: This endpoint is intended for v1 of the frontend and may be removed in the future.
     * Signals the application to shut down by setting a flag in AppState. 
     * The monitoring thread will detect this flag and initiate a graceful shutdown. 
     * Also stops the capture service if it's running to ensure a clean shutdown process.
     */
    ENDPOINT("POST", "/api/app/exit", exitApplication) {
        if (m_state->captureService) {
            m_state->captureService->stop();
        }

        auto dto = StatusDto::createShared();
        dto->status = "ok";
        dto->message = "Application shutdown requested";

        // Signal the shutdown flag - the monitoring thread will detect this
        m_state->shouldShutdown.store(true, std::memory_order_release);

        return createDtoResponse(Status::CODE_200, dto);
    }

    ENDPOINT("GET", "/api/capture/status", captureStatus) {
        auto dto = CaptureStatusDto::createShared();

        if (!m_state->captureService) {
            dto->active = false;
            dto->interfaceName = "";
            dto->address = "";
            dto->port = 0;
            dto->packetCount = static_cast<v_uint64>(0);
            dto->lastError = "Capture service not initialized";
            return createDtoResponse(Status::CODE_200, dto);
        }

        const auto snapshot = m_state->captureService->snapshot();
        dto->active = snapshot.active;
        dto->interfaceName = snapshot.interfaceName.c_str();
        dto->address = snapshot.address.c_str();
        dto->port = snapshot.port;
        dto->packetCount = static_cast<v_uint64>(snapshot.packetCount);
        dto->lastError = snapshot.lastError.c_str();

        return createDtoResponse(Status::CODE_200, dto);
    }

    ENDPOINT("GET", "/api/deframer-stats", deframerStats) {
        auto dto = DeframerStatsDto::createShared();

        if (!m_state->captureService) {
            dto->paAcquisitions = static_cast<v_uint64>(0);
            dto->paAcceptedRightBlanking = static_cast<v_uint64>(0);
            dto->paAcceptedLeftBlanking = static_cast<v_uint64>(0);
            dto->paAcceptedWithoutBlanking = static_cast<v_uint64>(0);
            dto->pbDetections = static_cast<v_uint64>(0);
            dto->pbAtPos6WrongChannel = static_cast<v_uint64>(0);
            dto->nonPbAtPos6 = static_cast<v_uint64>(0);
            dto->nonPbAtPos9 = static_cast<v_uint64>(0);
            dto->headerDecodesAttempted = static_cast<v_uint64>(0);
            dto->headerDecodesSucceeded = static_cast<v_uint64>(0);
            dto->framesEmitted = static_cast<v_uint64>(0);
            dto->framesRejectedWrongDataType = static_cast<v_uint64>(0);
            dto->abortsDuringGotPa = static_cast<v_uint64>(0);
            dto->abortsDuringGotSync = static_cast<v_uint64>(0);
            dto->idleNonZeroRightResets = static_cast<v_uint64>(0);
            dto->idleNonZeroLeftResets = static_cast<v_uint64>(0);
            dto->gotPaStateEntries = static_cast<v_uint64>(0);
            dto->gotSyncStateEntries = static_cast<v_uint64>(0);
            dto->gotHeaderStateEntries = static_cast<v_uint64>(0);
            return createDtoResponse(Status::CODE_200, dto);
        }

        const auto stats = m_state->captureService->getDeframerStats();
        dto->paAcquisitions = static_cast<v_uint64>(stats.paAcquisitions);
        dto->paAcceptedRightBlanking = static_cast<v_uint64>(stats.paAcceptedRightBlanking);
        dto->paAcceptedLeftBlanking = static_cast<v_uint64>(stats.paAcceptedLeftBlanking);
        dto->paAcceptedWithoutBlanking = static_cast<v_uint64>(stats.paAcceptedWithoutBlanking);
        dto->pbDetections = static_cast<v_uint64>(stats.pbDetections);
        dto->pbAtPos6WrongChannel = static_cast<v_uint64>(stats.pbAtPos6WrongChannel);
        dto->nonPbAtPos6 = static_cast<v_uint64>(stats.nonPbAtPos6);
        dto->nonPbAtPos9 = static_cast<v_uint64>(stats.nonPbAtPos9);
        dto->headerDecodesAttempted = static_cast<v_uint64>(stats.headerDecodesAttempted);
        dto->headerDecodesSucceeded = static_cast<v_uint64>(stats.headerDecodesSucceeded);
        dto->framesEmitted = static_cast<v_uint64>(stats.framesEmitted);
        dto->framesRejectedWrongDataType = static_cast<v_uint64>(stats.framesRejectedWrongDataType);
        dto->abortsDuringGotPa = static_cast<v_uint64>(stats.abortsDuringGotPa);
        dto->abortsDuringGotSync = static_cast<v_uint64>(stats.abortsDuringGotSync);
        dto->idleNonZeroRightResets = static_cast<v_uint64>(stats.idleNonZeroRightResets);
        dto->idleNonZeroLeftResets = static_cast<v_uint64>(stats.idleNonZeroLeftResets);
        dto->gotPaStateEntries = static_cast<v_uint64>(stats.gotPaStateEntries);
        dto->gotSyncStateEntries = static_cast<v_uint64>(stats.gotSyncStateEntries);
        dto->gotHeaderStateEntries = static_cast<v_uint64>(stats.gotHeaderStateEntries);

        return createDtoResponse(Status::CODE_200, dto);
    }

    // WEBSOCKET ENDPOINT
    ENDPOINT("GET", "/ws", websocket, REQUEST(std::shared_ptr<IncomingRequest>, request)) {
        return oatpp::websocket::Handshaker::serversideHandshake(request->getHeaders(), websocketConnectionHandler);
    }

private:

    static oatpp::Object<RTPInfoDto> buildRtoInfoDto(const amviewer::types::streaminfo::RTPInfo& rtpInfo) {
        auto dto = RTPInfoDto::createShared();
        dto->version = rtpInfo.version;
        dto->seq = rtpInfo.seq;
        dto->timestamp = rtpInfo.timestamp;
        dto->ssrc = rtpInfo.ssrc;
        dto->timestampSeconds = rtpInfo.timestampSeconds;
        dto->packetsInBurst = rtpInfo.packetsInBurst;
        return dto;
    }

    static oatpp::Object<SADMMetadataDto> buildSadmMetadataDto(
            const std::shared_ptr<amviewer::types::metadata::sadm::SADMMetadata> source,
            uint64_t timestampMs,
            uint64_t frameCounter
        ) {
        auto sadmMeta = SADMMetadataDto::createShared();
        sadmMeta->beds = oatpp::List<oatpp::Object<SADMAudioBedDto>>::createShared();
        sadmMeta->objects = oatpp::List<oatpp::Object<SADMAudioObjectDto>>::createShared();
        sadmMeta->presentations = oatpp::List<oatpp::Object<PresentationDto>>::createShared();
        sadmMeta->admProfiles = oatpp::List<oatpp::String>::createShared();
        sadmMeta->dolbyEFields = oatpp::List<oatpp::Object<SADMDolbyEMetadataFieldDto>>::createShared();
        sadmMeta->timestampMs = timestampMs;
        sadmMeta->frameCounter = frameCounter;

        static constexpr const char* kObjectClasses[] = {
            "Dialog", "VDS", "Voice Over", "Generic", "Spoken Subtitle", "Emergency Alert", "Emergency Information"
        };

        if(!source) {
            sadmMeta->sadmVersion = "N/A";
            sadmMeta->admVersion = "N/A";
            sadmMeta->admProfile = "Unknown";
            return sadmMeta;
        }

        if(source->type != amviewer::types::metadata::MetadataBase::Type::SADM) {
            sadmMeta->sadmVersion = "N/A";
            sadmMeta->admVersion = "N/A";
            sadmMeta->admProfile = "Unknown";
            return sadmMeta;
        }

        for (const auto& bed : source->beds) {
            auto row = SADMAudioBedDto::createShared();
            row->source = bed.source.c_str();
            row->config = bed.config.c_str();
            row->name = bed.name.c_str();
            row->gainDb = bed.gainDb;
            row->start = bed.start;
            row->end = bed.end;
            sadmMeta->beds->push_back(row);
        }

        for (size_t i = 0; i < source->objects.size(); ++i) {
            const auto& object = source->objects[i];
            auto row = SADMAudioObjectDto::createShared();
            row->id = static_cast<v_int32>(i + 1);
            const int typeIndex = object.classification;
            if (typeIndex >= 0 && typeIndex < 7) {
                row->type = kObjectClasses[typeIndex];
            } else {
                row->type = "Unknown";
            }
            row->name = object.name.c_str();
            row->diverge = object.diverge;
            row->channel = object.channel;
            row->gainDb = object.gainDb;
            row->x = object.x;
            row->y = object.y;
            row->z = object.z;
            sadmMeta->objects->push_back(row);
        }

        std::vector<std::pair<int, int>> objectIdToDisplayId;
        objectIdToDisplayId.reserve(source->objects.size());
        for (size_t i = 0; i < source->objects.size(); ++i) {
            objectIdToDisplayId.emplace_back(source->objects[i].id, static_cast<int>(i + 1));
        }

        for (size_t index = 0; index < source->programmes.size(); ++index) {
            const auto& programme = source->programmes[index];
            auto row = PresentationDto::createShared();
            row->index = static_cast<v_int32>(index + 1);
            row->name = programme.name.c_str();
            row->nameLang = programme.language.c_str();
            row->targetCfg = programme.config.c_str();
            row->presLang = programme.language.c_str();

            std::ostringstream objectElements;
            bool first = true;
            for (const int elementId : programme.elementIds) {
                if (elementId <= 0) continue;
                int displayId = 0;
                for (const auto& mapping : objectIdToDisplayId) {
                    if (mapping.first == elementId) {
                        displayId = mapping.second;
                        break;
                    }
                }
                if (displayId <= 0) continue;
                if (!first) objectElements << ",";
                objectElements << displayId;
                first = false;
            }
            row->objectElements = objectElements.str().c_str();

            std::string bedName;
            std::string fallbackBedName;
            std::string avsId = programme.alternativeValueSetId;
            const auto trimWhitespace = [](std::string value) {
                const auto begin = value.find_first_not_of(" \t\n\r");
                if (begin == std::string::npos) return std::string();
                const auto end = value.find_last_not_of(" \t\n\r");
                return value.substr(begin, end - begin + 1);
            };
            avsId = trimWhitespace(avsId);
            const std::string avsNeedle = avsId.empty() ? std::string() : std::string(":") + avsId;

            for (const int elementId : programme.elementIds) {
                if (elementId <= 0) continue;
                for (const auto& bed : source->beds) {
                    if (bed.id != elementId) continue;
                    if (fallbackBedName.empty()) fallbackBedName = bed.name;
                    if (!avsNeedle.empty()) {
                        if (bed.name.find(avsNeedle) != std::string::npos) {
                            bedName = bed.name;
                            break;
                        }
                    } else {
                        if (bed.name.find(':') == std::string::npos) {
                            bedName = bed.name;
                            break;
                        }
                    }
                }
                if (!bedName.empty()) break;
            }
            if (bedName.empty() && avsNeedle.empty()) bedName = fallbackBedName;
            row->bedElement = bedName.c_str();
            sadmMeta->presentations->push_back(row);
        }

        sadmMeta->sadmVersion = source->sadmVersion.empty() ? "N/A" : source->sadmVersion.c_str();
        sadmMeta->admVersion = source->admVersion.empty() ? "N/A" : source->admVersion.c_str();
        sadmMeta->admProfile = source->admProfile.empty() ? "Unknown" : source->admProfile.c_str();
        for (const auto& profile : source->admProfiles) {
            sadmMeta->admProfiles->push_back(profile.c_str());
        }
        sadmMeta->isDolbyEProfile = source->isDolbyEProfile;
        for (const auto& field : source->dolbyEFields) {
            auto row = SADMDolbyEMetadataFieldDto::createShared();
            row->group = field.group.c_str();
            row->label = field.label.c_str();
            row->value = field.value.c_str();
            sadmMeta->dolbyEFields->push_back(row);
        }

        return sadmMeta;
    }

    static oatpp::Object<StreamInfoBaseDto> buildST2110_31StreamInfoDto(
            const amviewer::types::streaminfo::StreamInfoBase& stream) {
        using namespace amviewer::types::streaminfo;
        if (stream.protocol != StreamInfoBase::Protocol::ST2110_31) {
            throw std::invalid_argument("Stream protocol is not ST2110-31");
        }
        auto info = ST2110_31InfoDto::createShared();
        const auto& typed = static_cast<const st2110_31::ST2110_31Info&>(stream);
        info->mode = typed.mode == st2110_31::ST2110_31Mode::Frame ? "frame" : "subframe";
        info->depth = typed.depth;
        info->deframer_stats = DeframerStatsDto::createShared();
        return info;
    }


    static oatpp::Object<ST2110_41InfoDto> buildST2110_41StreamInfoDto(
            const amviewer::types::streaminfo::StreamInfoBase& stream,
            const std::string& ditValue) {
        using namespace amviewer::types::streaminfo;

        if (stream.protocol != StreamInfoBase::Protocol::ST2110_41) {
            throw std::invalid_argument("Stream protocol is not ST2110-41");
        }
        auto info = ST2110_41InfoDto::createShared();
        info->ditValue = ditValue.c_str();
        return info;
    }

    static oatpp::Object<StreamInfoBaseDto> buildUnknownStreamInfoDto() {

        auto info = StreamInfoBaseDto::createShared();
        info->protocol = "unknown";
        return info;
    }

    template <typename T>
    void broadcastEnvelope(const T& envelope) {
        OATPP_COMPONENT(std::shared_ptr<oatpp::data::mapping::ObjectMapper>, objectMapper);
        oatpp::String json = objectMapper->writeToString(envelope);
        websocketConnectionListener->broadcast(json);
    }

    oatpp::Object<CaptureStatusDto> buildCaptureStatusDto(const CaptureSnapshot* snapshot) {
        auto dto = CaptureStatusDto::createShared();
        if (snapshot) {
            dto->active = snapshot->active;
            dto->interfaceName = snapshot->interfaceName.c_str();
            dto->address = snapshot->address.c_str();
            dto->port = snapshot->port;
            dto->packetCount = static_cast<v_uint64>(snapshot->packetCount);
            dto->lastError = snapshot->lastError.c_str();
            if (snapshot->active && snapshot->stream) {
                switch(snapshot->stream->protocol) {
                    case amviewer::types::streaminfo::StreamInfoBase::Protocol::ST2110_31:
                        dto->streamInfo = buildST2110_31StreamInfoDto(*snapshot->stream);
                        break;
                    case amviewer::types::streaminfo::StreamInfoBase::Protocol::ST2110_41:
                        dto->streamInfo = buildST2110_41StreamInfoDto(*snapshot->stream, snapshot->ditValue);
                        break;
                    default:
                        dto->streamInfo = buildUnknownStreamInfoDto();
                        break;
                }
            }
        } else {
            dto->active = false;
            dto->interfaceName = "";
            dto->address = "";
            dto->port = 0;
            dto->packetCount = static_cast<v_uint64>(0);
            dto->lastError = "Capture service not initialized";
        }
        return dto;
    }

    oatpp::Object<ServiceSelectionDto> buildServiceSelectionDto(const ServiceSelection& selection) {
        auto dto = ServiceSelectionDto::createShared();
        dto->name = selection.name.c_str();
        dto->system = selection.system.c_str();
        dto->interfaceName = selection.interfaceName.c_str();
        dto->address = selection.address.c_str();
        dto->port = static_cast<v_int32>(selection.port);
        dto->codec = selection.codec.c_str();
        dto->audio = selection.audio.c_str();
        dto->sampleRate = static_cast<v_int32>(selection.sampleRate);
        return dto;
    }

    oatpp::List<oatpp::Object<DiscoveredServiceDto>> buildDiscoveredServicesDto(const std::vector<DiscoveredService>& services) {
        auto list = oatpp::List<oatpp::Object<DiscoveredServiceDto>>::createShared();
        for (const auto& service : services) {
            auto dto = DiscoveredServiceDto::createShared();
            dto->name = service.name.c_str();
            dto->system = service.system.c_str();
            dto->address = service.address.c_str();
            dto->port = service.port;
            dto->codec = service.codec.c_str();
            dto->channels = service.channels;
            dto->sampleRate = service.sampleRate;
            dto->sdpText = service.sdpText.c_str();
            list->push_back(dto);
        }
        return list;
    }

    oatpp::Object<ws::WsStreamInfoDto> buildStreamInfoEnvelope(const CaptureSnapshot& snapshot) {
        if (!snapshot.active || !snapshot.stream) return nullptr;
        auto envelope = ws::WsStreamInfoDto::createShared();
        envelope->type = "streamInfo";
        switch(snapshot.stream->protocol) {
            case amviewer::types::streaminfo::StreamInfoBase::Protocol::ST2110_31:
                envelope->streamInfo = buildST2110_31StreamInfoDto(*snapshot.stream);
                break;
            case amviewer::types::streaminfo::StreamInfoBase::Protocol::ST2110_41:
                envelope->streamInfo = buildST2110_41StreamInfoDto(*snapshot.stream, snapshot.ditValue);
                break;
            default:
                envelope->streamInfo = buildUnknownStreamInfoDto();
                break;
        }
        return envelope;
    }

    void broadcastStreamInfoUpdate(const CaptureSnapshot& snapshot) {
        auto envelope = buildStreamInfoEnvelope(snapshot);
        if (envelope) broadcastEnvelope<oatpp::Object<ws::WsStreamInfoDto>>(envelope);
    }

    oatpp::Object<ws::WsCaptureStatusDto> buildCaptureEnvelope() {
        CaptureSnapshot snap;
        bool hasSnap = false;
        if (m_state->captureService) {
            snap = m_state->captureService->snapshot();
            hasSnap = true;
        }
        auto envelope = ws::WsCaptureStatusDto::createShared();
        envelope->type = "capture";
        envelope->captureStatus = buildCaptureStatusDto(hasSnap ? &snap : nullptr);
        return envelope;
    }

    void broadcastCaptureUpdate() {
        broadcastEnvelope<oatpp::Object<ws::WsCaptureStatusDto>>(buildCaptureEnvelope());
    }

    oatpp::Object<ws::WsServicesDto> buildServiceEnvelope() {
        auto envelope = ws::WsServicesDto::createShared();
        envelope->type = "services";

        ServiceSelection selection;
        {
            std::lock_guard<std::mutex> lock(m_state->mutex);
            selection = m_state->selectedService ? *m_state->selectedService : ServiceSelection{};
        }
        auto services = BackgroundServiceDiscovery::instance().snapshot();
        if(m_state->selectedService) {
            envelope->selectedService = buildServiceSelectionDto(*m_state->selectedService);
        } else {
            envelope->selectedService = nullptr;
        }
        envelope->services = buildDiscoveredServicesDto(services);
        return envelope;
    }

    void broadcastServiceUpdate() {
        broadcastEnvelope<oatpp::Object<ws::WsServicesDto>>(buildServiceEnvelope());
    }

    oatpp::Object<ws::WsInterfacesDto> buildInterfaceEnvelope() {
        auto envelope = ws::WsInterfacesDto::createShared();
        envelope->interfaces = oatpp::List<oatpp::String>::createShared();
        {
            std::lock_guard<std::mutex> lock(m_state->mutex);
            for (const auto& name : CaptureService::list_interfaces()) {
                envelope->interfaces->push_back(name.c_str());
            }
            auto selectedInterface = BackgroundServiceDiscovery::instance().get_interface();
            if(selectedInterface.empty()) {
                envelope->selectedInterface = nullptr;
            } else {
                envelope->selectedInterface = selectedInterface;
            }
        }
        return envelope;
    }

    void broadcastInterfaceUpdate() {
        broadcastEnvelope<oatpp::Object<ws::WsInterfacesDto>>(buildInterfaceEnvelope());
    }

    oatpp::Object<ws::WsMetadataDto> buildMetadataEnvelope() {
        auto envelope = ws::WsMetadataDto::createShared();
        std::shared_ptr<amviewer::types::metadata::MetadataBase> source;
        uint64_t timestampMs;
        uint64_t frameCounter;
        {
            std::lock_guard<std::mutex> lock(m_state->mutex);
            source = m_state->metadata;
            timestampMs = m_state->metadataTimestampMs;
            frameCounter = m_state->metadataFrameCounter;
            
            if(m_state->rtpInfo){
                envelope->rtpInfo = buildRtoInfoDto(*m_state->rtpInfo);
            }
        }


        if(source) {
            switch(source->type) {
                case amviewer::types::metadata::MetadataBase::Type::SADM:
                    envelope->metadata = buildSadmMetadataDto(
                        std::static_pointer_cast<amviewer::types::metadata::sadm::SADMMetadata>(source), 
                        timestampMs,
                        frameCounter
                    );
                    break;
                default:
                    break;
            }
        }
        return envelope;
    }

    static std::string nowIso() {
        const auto now = std::chrono::system_clock::now();
        const auto t = std::chrono::system_clock::to_time_t(now);
        std::tm tm{};
#if defined(_WIN32)
        gmtime_s(&tm, &t);
#else
        gmtime_r(&t, &tm);
#endif
        char buffer[32];
        std::strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%SZ", &tm);
        return buffer;
    }

private:
    std::shared_ptr<AppState> m_state;
};

#include OATPP_CODEGEN_END(ApiController)

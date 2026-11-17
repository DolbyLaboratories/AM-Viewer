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

#include "logging.h"

#include <atomic>
#include <chrono>

#include <spdlog/sinks/stdout_color_sinks.h>

namespace amviewer {
namespace logging {

namespace {

std::atomic<bool> g_initialized{false};

constexpr const char* kLoggerName = "amv";
constexpr const char* kBundleStartMs = "amv.start_ms";

v_int64 now_ms() {
    return static_cast<v_int64>(
        std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::steady_clock::now().time_since_epoch())
            .count());
}

}

void init(spdlog::level::level_enum level) {
    if (g_initialized.exchange(true)) {
        spdlog::set_level(level);
        return;
    }
    auto logger = spdlog::stdout_color_mt(kLoggerName);
    logger->set_pattern("[%Y-%m-%d %H:%M:%S.%e] [%^%l%$] %v");
    logger->set_level(level);
    spdlog::set_default_logger(logger);
    spdlog::set_level(level);

    spdlog::info("Logger initialized with level {}", spdlog::level::to_string_view(spdlog::get_level()));
}

bool parse_level(const std::string& text, spdlog::level::level_enum& out) {
    if (text == "trace") { out = spdlog::level::trace; return true; }
    if (text == "debug") { out = spdlog::level::debug; return true; }
    if (text == "info")  { out = spdlog::level::info;  return true; }
    if (text == "warn" || text == "warning") { out = spdlog::level::warn; return true; }
    if (text == "error" || text == "err")    { out = spdlog::level::err;  return true; }
    if (text == "critical")                  { out = spdlog::level::critical; return true; }
    if (text == "off")                       { out = spdlog::level::off;  return true; }
    return false;
}

std::shared_ptr<RequestLogInterceptor::OutgoingResponse>
RequestLogInterceptor::intercept(const std::shared_ptr<IncomingRequest>& request) {
    if (request) {
        request->putBundleData(oatpp::String(kBundleStartMs), oatpp::Int64(now_ms()));
    }
    return nullptr;
}

std::shared_ptr<ResponseLogInterceptor::OutgoingResponse>
ResponseLogInterceptor::intercept(const std::shared_ptr<IncomingRequest>& request,
                                  const std::shared_ptr<OutgoingResponse>& response) {
    if (!request || !response) {
        return response;
    }

    const auto& startingLine = request->getStartingLine();
    const std::string method = startingLine.method.std_str();
    const std::string path = startingLine.path.std_str();
    const v_int32 statusCode = response->getStatus().code;

    v_int64 elapsedMs = -1;
    auto startWrapper = request->getBundleData<oatpp::Int64>(oatpp::String(kBundleStartMs));
    if (startWrapper) {
        elapsedMs = now_ms() - *startWrapper;
    }

    if (statusCode >= 500) {
        if (elapsedMs >= 0) {
            AMV_LOG_ERROR("rest {} {} -> {} ({}ms)", method, path, statusCode, elapsedMs);
        } else {
            AMV_LOG_ERROR("rest {} {} -> {}", method, path, statusCode);
        }
    } else if (statusCode >= 400) {
        if (elapsedMs >= 0) {
            AMV_LOG_WARN("rest {} {} -> {} ({}ms)", method, path, statusCode, elapsedMs);
        } else {
            AMV_LOG_WARN("rest {} {} -> {}", method, path, statusCode);
        }
    } else {
        if (elapsedMs >= 0) {
            AMV_LOG_INFO("rest {} {} -> {} ({}ms)", method, path, statusCode, elapsedMs);
        } else {
            AMV_LOG_INFO("rest {} {} -> {}", method, path, statusCode);
        }
    }

    return response;
}

}
}

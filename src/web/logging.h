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

#include <memory>
#include <string>

#include <spdlog/spdlog.h>

#include "oatpp/web/server/interceptor/RequestInterceptor.hpp"
#include "oatpp/web/server/interceptor/ResponseInterceptor.hpp"

namespace amviewer {
namespace logging {

void init(spdlog::level::level_enum level);

bool parse_level(const std::string& text, spdlog::level::level_enum& out);

class RequestLogInterceptor
    : public oatpp::web::server::interceptor::RequestInterceptor {
public:
    std::shared_ptr<OutgoingResponse> intercept(
        const std::shared_ptr<IncomingRequest>& request) override;
};

class ResponseLogInterceptor
    : public oatpp::web::server::interceptor::ResponseInterceptor {
public:
    std::shared_ptr<OutgoingResponse> intercept(
        const std::shared_ptr<IncomingRequest>& request,
        const std::shared_ptr<OutgoingResponse>& response) override;
};

}
}

#define AMV_LOG_DEBUG(...) spdlog::debug(__VA_ARGS__)
#define AMV_LOG_INFO(...)  spdlog::info(__VA_ARGS__)
#define AMV_LOG_WARN(...)  spdlog::warn(__VA_ARGS__)
#define AMV_LOG_ERROR(...) spdlog::error(__VA_ARGS__)

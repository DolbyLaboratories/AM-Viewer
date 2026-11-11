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

#include "oatpp-websocket/AsyncWebSocket.hpp"

#include "oatpp/core/async/Lock.hpp"
#include "oatpp/core/async/Executor.hpp"

#include "oatpp/core/macro/component.hpp"

class WebsocketPeer : public oatpp::websocket::AsyncWebSocket::Listener  {
private:
    std::shared_ptr<oatpp::websocket::AsyncWebSocket> m_socket;
    oatpp::async::Lock                                m_writeLock;

    OATPP_COMPONENT(std::shared_ptr<oatpp::async::Executor>, asyncExecutor, "websocketExecutor");
public:
    WebsocketPeer(const std::shared_ptr<oatpp::websocket::AsyncWebSocket>& socket)
        : m_socket(socket) 
    {}

    std::shared_ptr<oatpp::websocket::AsyncWebSocket> getSocket() const {
        return m_socket;
    }


    void sendMessage(const oatpp::String& message) {
        class SendMessageCoroutine : public oatpp::async::Coroutine<SendMessageCoroutine> {
        private:
            oatpp::async::Lock* m_lock;
            std::shared_ptr<oatpp::websocket::AsyncWebSocket> m_websocket;
            oatpp::String m_message;
        public:

            SendMessageCoroutine(oatpp::async::Lock* lock,
                                const std::shared_ptr<oatpp::websocket::AsyncWebSocket>& websocket,
                                const oatpp::String& message)
            : m_lock(lock)
            , m_websocket(websocket)
            , m_message(message)
            {}

            Action act() override {
            return oatpp::async::synchronize(m_lock, m_websocket->sendOneFrameTextAsync(m_message)).next(finish());
            }

        };

        asyncExecutor->execute<SendMessageCoroutine>(&m_writeLock, m_socket, message);
    }

    
public: // WebSocket Listener methods
    oatpp::async::CoroutineStarter onPing(const std::shared_ptr<oatpp::websocket::AsyncWebSocket>& socket, const oatpp::String& message) override { return nullptr; }
    oatpp::async::CoroutineStarter onPong(const std::shared_ptr<oatpp::websocket::AsyncWebSocket>& socket, const oatpp::String& message) override { return nullptr; }
    oatpp::async::CoroutineStarter onClose(const std::shared_ptr<oatpp::websocket::AsyncWebSocket>& socket, v_uint16 code, const oatpp::String& message) override { return nullptr; }
    oatpp::async::CoroutineStarter readMessage(const std::shared_ptr<oatpp::websocket::AsyncWebSocket>& socket, v_uint8 opcode, p_char8 data, oatpp::v_io_size size) override {
        // TODO: Enable receiving messages from the client
        return nullptr;
    }

};

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

#include "./websocket_peer.hpp"
#include "oatpp-websocket/AsyncConnectionHandler.hpp"

#include <functional>
#include <unordered_map>
#include <mutex>

class WebsocketConnectionListener : public oatpp::websocket::AsyncConnectionHandler::SocketInstanceListener {
public:
  using WelcomeHandler = std::function<void(const std::shared_ptr<WebsocketPeer>&)>;

  std::list<std::shared_ptr<WebsocketPeer>> m_peers;
  std::mutex m_peersMutex;

private:
  WelcomeHandler m_welcomeHandler;
  std::mutex m_welcomeMutex;

public:

  WebsocketConnectionListener() = default;

  // Registers a callback invoked once per new peer, right after the socket
  // is wired up. Typical use is to push a snapshot of current state so a
  // freshly-connected client doesn't have to wait for the next delta.
  void setWelcomeHandler(WelcomeHandler handler) {
    std::lock_guard<std::mutex> lock(m_welcomeMutex);
    m_welcomeHandler = std::move(handler);
  }

public:

  /**
   *  Called when socket is created
   */
  void onAfterCreate_NonBlocking(const std::shared_ptr<AsyncWebSocket>& socket, const std::shared_ptr<const ParameterMap>& params) override {
    auto peer = std::make_shared<WebsocketPeer>(socket);
    socket->setListener(peer);
    {
      std::lock_guard<std::mutex> lock(m_peersMutex);
      m_peers.push_back(peer);
    }

    WelcomeHandler handler;
    {
      std::lock_guard<std::mutex> lock(m_welcomeMutex);
      handler = m_welcomeHandler;
    }
    if (handler) {
      try {
        handler(peer);
      } catch (...) {
        // Welcome-handler failures must not take down the connection.
      }
    }
  }

   /**
   *  Called before socket instance is destroyed.
   */  
  void onBeforeDestroy_NonBlocking(const std::shared_ptr<AsyncWebSocket>& socket) override {
    std::lock_guard<std::mutex> lock(m_peersMutex);
    m_peers.remove_if([&](const std::shared_ptr<WebsocketPeer>& peer) {
      return peer->getSocket() == socket;
    });
  };

  void broadcast(const oatpp::String& message) {
    std::lock_guard<std::mutex> lock(m_peersMutex);
    for (const auto& peer : m_peers) {
      peer->sendMessage(message);
    }
  }
};
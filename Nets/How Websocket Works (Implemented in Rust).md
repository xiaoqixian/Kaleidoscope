### How WebSocket Works? (Implemented in Rust)

#### The Opening Handshake

The opening handshake is intended to be compatible with HTTP-based server-side software and intermediaries, so that a single port can be used by both HTTP clients and WebSocket server communicating with the server. To switch to the WebSocket protocol, a client has to send a protocol switching request, it looks like this:

```
GET /chat HTTP/1.1
Host: server.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Origin: http://example.com
Sec-WebSocket-Protocol: chat, superchat
Sec-WebSocket-Version: 13
```

The "Request-URI" of the GET method, which is "server.example.com" in the example request, is used to identify the endpoint of the WebSocket connection, both to allow multiple domains to be served from one IP address and to allow multiple WebSocket endpoints to be served by a single server.

And then the server will send a response to confirm this request:

```
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
Sec-WebSocket-Protocol: chat
```

If the handshake is successful, then the data transfer part starts.

#### Data Transfer

Clients and servers transfer data back and forth in **conceptual units** referred to in this specification as "messages". On the wire, a message is composed of one or more frames. 

A frame has an associated type. Each frame belonging to the same message contains the same type of data. There are types of textual data (which is interpreted as UTF-8 text), binary data, and control frames (which are not intended to carry data as to signal that the connection should be closed).


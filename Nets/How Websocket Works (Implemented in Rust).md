## How WebSocket Works? (Implemented in Rust) 1

Part1 The WebSocket Protocol by IFTF

### Design Philosophy

Conceptually, WebSocket is really just a layer on top of TCP that does the following:

- adds a web origin-based security model for browsers
- adds an addressing and protocol naming mechanism to support multiple services on one port and multiple host names on one IP address.
- layers a framing mechanism on top of TCP to get back to the IP packet mechanism that TCP is built on, but without length limits.
- includes an additional closing handshake in-band that is designed to work in the presence of proxies and other intermediaries.

It's also designed in such a way that its servers can share a port with HTTP servers, by having its handshake be a valid HTTP Upgrade request. 

The intent of WebSocket is to provide a relatively simple protocol that can coexist with HTTP and deployed HTTP infrastructure (such as proxies) and that is as close to TCP as is safe for use with such infrastructure given security considerations, with targeted additions to simplify usage and keep simple things simple. 

### The Opening Handshake

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

Additional header fields are used to select options in the WebSocket protocol. Typical options available in this version are the subprotocol selector (|Sec-WebSocket-Protocol|), list of extensions support by the client (|Sec-WebSocket-Extensions|), |Origin| header field, etc. The |Sec-WebSocket-Protocol|) request-header field can be used to indicate what protocols (application-level protocols layered over the WebSocket protocol) are acceptable to the client. The server selects **one or none** the acceptable protocols and echoes that value in its handshake to indicate that it has selected that protocol.

The |Origin| header field is used to protect against unauthorized cross-origin use of a WebSocket server by scripts using the WebSocket API in a web browser. The server is informed of the script origin generating the WebSocket connection request. If the server does not wish to accept connections from this origin, it can choose to reject the connection by sending an appropriate HTTP error code. This header field is **sent by browser clients**; for non-browser clients, this header field may be sent if it makes sense in the context of those clients.

Finally, the server has to prove to the client that it received the client's WebSocket handshake. To prove that the handshake is received, the server has to take two pieces of information and combine them to form a response. The first piece of information comes from the |Sec-WebSocket-Key| header field in the client handshake. The server has to take the value and concatenate this with the Globally Unique Identifier in string from, which is unlikely to be used by network endpoints that do not understand the WebSocket protocol. A SHA-1 hash, base64-encoded of this concatenation is then returned in the server's handshake. 

#### Client Requirements

To _Establish a WebSocket Connection_, a client opens a connection and sends a handshake. A connection is defined to initially be in a CONNECTING state. A client will need to supply a /host/, /port/, /resource name/, and a /secure/ flag, which are the components of a WebSocket URI, along with a list of /protocols/ and /extensions/ to be used. Additionally, if the client is a web browser, it supplies /origin/. 

The exact requirements of how the connection should be opened, what should be sent in the opening handshake, and how the server's response should be interpreted are as follows:

1. The components of the WebSocket URI passed into this algorithm MUST be valid.

2. If the client already has a WebSocket connection to the remote host (IP address) identified by /host/ and /port/ pair, the client MUST wait until that connection has been established or for that connection to have failed. There MUST be no more than one connection in CONNECTING state. If multiple connections to the same IP address are attempted simultaneously, the client MUST serialize them so that there is no more one connection at a time running through the following steps.

   If the client cannot determine the IP address of the remote host (for example, because all communication is being done through a proxy server that performs DNS queries itself), then the client MUST assume for the purposes of this step that each host name refers to a distinct remote host, and instead the client SHOULD limit the total number (e.g., the client might allow simultaneous pending connections to a.exmaple.com and b.example.com, but if thirty simultaneous connections to a single host are requested, that may not be allowed). For example, in a web browser context, the client needs to consider the number of tabs the user has open in setting a limit to the number of simultaneous pending connections. 

3. _Proxy Usage_: If the client is configured to use a proxy when using the WebSocket Protocol to connect to /host/ and /port/, then the client SHOULD connect (using HTTP CONNECT method) to the that proxy and ask it to open a TCP connection to the host given by /host/ and the port given by /port/.

4. If the connection could not be opened, either because a direct connection failed or because any proxy used returned error, then the client MUST _Fail the WebSocket Connection_ and abort the connection attempt.

5. If /secure/ is true, the client MUST perform a TLS handshake over the connection after opening the connection and before sending the handshake data. If this fails, the client MUST _Fail the WebSocket Connection_ and abort the connection. 

Once the connection has been established, the client MUST send an opening handshake to the server. The requirements for the opening handshake are as follows:

1. The handshake MUST be a valid HTTP request.
2. The method of the request MUST be GET, and the HTTP version MUST be at least 1.1.
3. The "Request-URI" part of the request MUST match the /resource name/ or be an absolute http/https URI that, when parsed, has a /resource name/, /host/, and /port/ that match the corresponding ws/wss URI.
4. The request MUST contain a |Host| header field whose value contains /host/ plus optionally ":" followed by /port/
5. The request MUST contain an |Upgrade| header field whose value MUST include the "websocket" keyword.
6. The request MUST contain a |Connection| header field whose value MUST include the "Upgrade" token.
7. The request MUST include a header field with the name |Sec-WebSocket=Key|
8. The request MUST include a header field with the name |Origin| if the request is coming from a browser client. If the connection is from a non-browser client, the request MAY include this header field if the semantics of that client match the use-case described here for browser clients. The value of this header field is the ASCII serialization of origin of the context in which the code establishing the connection is running. 
9. The request MUST include a header field with the name |Sec-WebSocket-Version|. The value of this header field MUST be 13.
10. The request MAY include a header field with the name |Sec-WebSocket-Protocol|. If present, this value indicates one or more comma-separated subprotocol the client wishes to speak, ordered by preference.
11. The request MAY include a header field with the name |Sec-WebSocket-Extensions|. If present, this value indicates the protocol-level extension(s) the client wishes to speak.
12. The request MAY include any other header fields.

And then the server will send a response to confirm this request:

```
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
Sec-WebSocket-Protocol: chat
```

The client MUST validate the server's response as follows:

1. If the status code received from the server is not 101 (Switching Protocol Code), the client handles the response per HTTP procedures. 
2. If the response lacks an |Upgrade| header field or the |Upgrade| header field contains a value that is not an ASCII case-insensitive match for the value "websocket", the client MUST _Fail the WebSocket Connection_.
3. If the response lacks a |Connection| header field or the |Connection| header field does not contain a token that is an ASCII case-insensitive match for the value "Upgrade", the client MUST _Fail the WebSocket Connection_.
4. If the response lacks a |Sec-WebSocket-Accept| header field or
   the |Sec-WebSocket-Accept| contains a value other than the
   base64-encoded SHA-1 of the concatenation of the |Sec-WebSocket-
   Key| (as a string, not base64-decoded) with the string "258EAFA5-
   E914-47DA-95CA-C5AB0DC85B11" but ignoring any leading and
   trailing whitespace, the client MUST _Fail the WebSocket
   Connection_.
5. If the response includes a |Sec-WebSocket-Extensions| header
   field and this header field indicates the use of an extension
   that was not present in the client’s handshake (the server has
   indicated an extension not requested by the client), the client
   MUST _Fail the WebSocket Connection_. 
6. If the response includes a |Sec-WebSocket-Protocol| header field
   and this header field indicates the use of a subprotocol that was
   not present in the client’s handshake (the server has indicated a
   subprotocol not requested by the client), the client MUST _Fail
   the WebSocket Connection_.

#### Server Requirements



If the handshake is successful, then the data transfer part starts.

### Data Transfer

#### Data Framing

Clients and servers transfer data back and forth in **conceptual units** referred to in this specification as "messages". On the wire, a message is composed of one or more frames. 

To avoid confusing network intermediaries and for security reasons, a client MUST mask all frames that it sends to the server. The server MUST close the connection upon receiving a frame that is not masked. A server MUST NOT mask any frames that it sends to the client. A client MUST close a connection if it detects a masked frame.

A frame has an associated type. Each frame belonging to the same message contains the same type of data. There are types of textual data (which is interpreted as UTF-8 text), binary data, and control frames (which are not intended to carry data as to signal that the connection should be closed).

The base framing protocol defines a frame type with an opcode, a payload length, and designated locations for "Extension data" and "Application data", which together define the "Payload data".

  0			   1               2               3
  0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7
 +-+-+-+-+-------+-+-------------+-------------------------------+
 |F|R|R|R| opcode|M| Payload len |	Extended payload length	|
 |I|S|S|S|   (4) |A|	 (7)	 |         	(16/64)           |
 |N|V|V|V|       |S|             |	(if payload len==126/127)  |
 | |1|2|3|       |K|             |                           	|
 +-+-+-+-+-------+-+-------------+ \- \- \- \- \- \- \- \- \- \- \- \- \- \- \- +
 |	Extended payload length continued, if payload len == 127   |

 \+ \- \- \- \- \- \- \- \- \- \- \- \- \- \- \- +-------------------------------+               

 | 							  | Masking-key, if MASK set to 1 |
 +-------------------------------+-------------------------------+
 | Masking-key (continued)       |			Payload Data       |
 +-------------------------------- \- \- \- \- \- \- \- \- \- \- \- \- \- \- \- +
 :					Payload Data continued ...			     :
 \+ \- \- \- \- \- \- \- \- \- \- \- \- \- \- \- \- \- \- \- \- \- \- \- \- \- \- \- \- \- \- \- +
 |					Payload Data continued ...				 |
 +---------------------------------------------------------------+

Opcode: 4 bits

<div style = "padding-left: 16px">Defines the interpretation of the "Payload data". If an unknown opcode is received, the receiving endpoint MUST <i>Fail the WebSocket Connection.</i> The following values are defined:</div>

- 0x0: denotes a continuous frame
- 0x1: denotes a text frame
- 0x2: denotes a binary frame
- 0x3-7: reserved for further non-control frames
- 0x8: denotes a connection frame
- 0x9: denote a ping
- 0xA: denote a pong
- 0xB-F: reserved for further control frames

Payload length: 7 bits, 7+16 bits, or 7+64 bits

<div style="padding-left:16px">The length of the "Payload data", in bytes: if 0-125, that is the payload length. If 126, the following 2 bytes interpreted as a 16-bit unsigned integer are the payload length. If 127, the following 8 bytes interpreted as a 64-bit (the most significant bit must be 0) are the payload length. Multibyte length quantities are expressed in network byte order. Note that in all cases, the minimal number of bytes MUST be used to encode the length.
</div>

#### Fragmentation

The primary purpose of fragmentation is to allow sending a message that is of unknown size when the message is started without having to buffer that message. If messages couldn't be fragmented, then an endpoint would have to buffer the entire message so its length could be counted before the first byte is sent. 

A secondary use-case for fragmentation is for multiplexing, where it is not desirable for a large message on one logical channel to monopolize the output channel, so the multiplexing needs to be free to split the message into smaller fragments to better share the output channel.

The following rules apply to fragmentation:

- An unfragmented message consists of a single frame with the FIN bit set and an opcode other than 0.
- A fragmented message consists of a single frame with the FIN bit clear and an opcode other than 0, followed by zero or more frames with the FIN bit clear and the opcode set to 0, and terminated by a single frame with the FIN bit set and opcode of 0. 
- Control frames MAY be injected in the middle of a fragmented message. Control frames themselves MUST NOT be fragmented.
- Message fragments MUST be delivered to the recipient in the order sent by the sender.
- The fragment of one message MUST NOT be interleaved between the fragments of another message unless an extension has been negotiated that can interpret the interleaving.
- An endpoint MUST be capable of handling control frames in the middle of a fragmented message.
- As control frames cannot be fragmented, an intermediary MUST NOT attempt to change the fragmentation of a control frame.
- An intermediary MUST NOT change the fragmentation of a message if any reserved bit values are used and the meaning of these values is not known to the intermediary.
- An intermediary MUST NOT change the fragmentation of any message in the context of a connection where extensions have been negotiated and the intermediary is not aware of the semantics of the negotiated extensions. Similarly, an intermediary that didn't see the WebSocket handshake that resulted in a WebSocket connection MUST NOT change the fragmentation of any message of such connection.
- As a consequence of these rules, all fragments of a message are of the same type, as set by the first fragment's opcode. 

#### Control Frames

Control frames are identified by opcodes where the most significant bit of the opcode is 1. Currently defined opcodes for control frames include 0x8 (Close), 0x9 (Ping), and 0xA (Pong).

Control frames are used to communicate state about the WebSocket. All control frames MUST have a payload length of 125 bytes or less and MUST NOT be fragmented. 

##### Close

The Close frame contains an opcode of 0x8.

The Close frame MAY contain a body that indicates a reason for closing. If there is a body, the first two bytes of the body MUST be a 2-byte unsigned integer (in network order) representing a status code. The data is not guaranteed to be human readable, and the client MUST NOT show it end users.

The application MUST NOT send any more data frames after sending a Close frame. If an endpoint receives a Close frame and did not previously send a Close frame, the endpoint MUST send a Close frame in response.

After both sending and receiving a Close message, an endpoint considers the WebSocket connection closed and MUST close the underlying TCP connection. The server MUST close the underlying TCP connection immediately; the client SHOULD wait for the server to close the connection but MAY close the connection at any time after sending and receiving a Close message, e.g., if it has not received a TCP Close from the server in a reasonable time period.

If a client and server both send a Close message at the same time, both endpoints will have sent and received a Close message and should consider the WebSocket connection closed and close the underlying TCP connection.

#### Data Frames

Data frames are identified by opcodes where the most significant bit is 0. Currently defined opcodes for data frames include 0x1 (Text), 0x2 (Binary).

### Closing Handshake

Either peer can send a control frame with data containing a specified control sequence to begin the closing handshake. Upon receiving such a frame, the other peer sends a Close frame in response, if it hasn't already sent one. Upon receiving _that_ control frame, the first peer then closes the connection, safe in the knowledge that no further data is forthcoming. 

After sending a control frame that indicates the connections should be closed, a peer does not send any further data; after receiving a frame indicating the connection should be closed, any further data received will be discarded.

**It is safe for both peers to initiate this handshake simutaneously.**

The closing handshake is intended to complement the TCP closing handshake, on the basis that the TCP closing handshake is not always reliable end-to-end, especially in the presence of intercepting proxies and other intermediaries. For instance, on some platforms, if a socket is closed with data in the receive queue, a RST (Reset) packet is sent, which will then cause `recv()` to fail for the party that received the RST, even if there was data waiting to be read.

### Security Model

The WebSocket Protocol uses the *origin model* used by web browsers to restrict which web pages can contact a WebSocket server when the WebSocket Protocol is used from a web page. Naturally, when the WebSocket Protocol is used by a dedicated client directly (i.e., not from a web page through a web browser), the origin model is not useful, as the client can provide any arbitrary origin string.

This protocol is intended to fail to establish a connection with servers of pre-existing protocols like SMTP and HTTP, while allowing HTTP servers to opt-in to supporting this protocol if desired. This is achieved by having a strict and elaborate handshake and by limiting the data that can be inserted into the connection before the handshake is finished. 

It is similarly intended to fail to establish a connection when data from other protocols, especially HTTP, is sent to a WebSocket server, for example, as might happen if an HTML "form" were submitted to a WebSocket server. This is primarily achieved by requiring that the server prove that it read the handshake, which it can only do if the handshake contains the appropriate parts, which can only be sent by a WebSocket client.

### Relationship to TCP and HTTP

The WebSocket Protocol is an independent TCP-based protocol. Its only relationship to HTTP is that its handshake is interpreted by HTTP servers as an Upgrade request.

By default, the WebSocket Protocol used port 80 for regular WebSocket connections and port 443 for WebSocket connections tunneled over Transport Layer Security (TLS).

### WebSocket URIS

The WebSocket Protocol defines two URI schemes:

<div style="padding-left:40px; font-family: Source Code Pro; font-size: 15px">ws-URI = "ws:" "//" host [ ":" port ] path [ "?" query ]<br>wss-URI = "wss:" "//" host [ ":" port ] path [ "?" query ]</div>

The port component is optional; the default for "ws" is port 80, while the default for "wss" is port 443.


## How WebSocket Works? (Implemented in Rust) 2

Part 2 Implemented in Rust (requirement: familiarity with the WebSocket Protocol)

I selected the WebSocket Protocol implemented by [websocket-rs](https://github.com/websockets-rs/rust-websocket.git), it is featured with both synchronous and asynchronous. It's a rather simple implementation with only 2686 lines of code. This part will only introduce the synchronous part, the asynchronous part will be introduced in part 3.

### Server

The type `Server<S>` is actually the type `Ws<S, TcpListener>`. Type `S` MUST implement the trait `OptionalTlsAcceptor`. This is to support both with and without TLS layer. 

To create a Server instance without TLS, call associated function `bind`, a String type parameter needed as the server's address. To create a Server instance with TLS, call associated function `bind_secure`, an address and a `TlsAcceptor` type parameter is needed. 

A Server instance contains a listener and MAY contain a `TlsAcceptor`, and you can call `filter_map` method to generate an iterator to receive client connections. As `WsServer` already implemented the `Iterator` trait. 

```rust
impl Iterator for WsServer<NoTlsAcceptor, TcpListener> {
	type Item = AcceptResult<TcpStream>;//AcceptResult is actually Result<Upgrade<TcpStream>, InvalidConnection<TcpStream, Buffer>>

	fn next(&mut self) -> Option<<Self as Iterator>::Item> {
		Some(self.accept())
	}
}
```

This is equivalent to calling `TcpListener::accept` method in a loop. 

In `WsServer`, the `accept` method is reimplemented. First accept the TCP connection by calling the `TcpListener::accept` method, which returns a `TcpStream` instance. If with a TLS layer, the `TlsAcceptor::accept` method is called to wrap the `TcpStream` in a `TlsStream`. Then establish a WebSocket by calling `into_ws` method.

`into_ws` is neither an original method of `TcpStream` nor `TlsStream`. But as all generic types that implemented `Stream` trait have implemented `IntoWs` trait. So this method is available for both `TcpStream` and `TlsStream`.

```rust
pub trait IntoWs {
	/// The type of stream this upgrade process is working with (TcpStream, etc.)
	type Stream: Stream;
	/// An error value in case the stream is not asking for a websocket connection
	/// or something went wrong. It is common to also include the stream here.
	type Error;
	/// Attempt to parse the start of a Websocket handshake, later with the  returned
	/// `WsUpgrade` struct, call `accept` to start a websocket client, and `reject` to
	/// send a handshake rejection response.
	fn into_ws(self) -> Result<Upgrade<Self::Stream>, Self::Error>;
}
```

Inside `into_ws`, the request is parsed by hyper (A HTTP lib in Rust), parse result is of `Incoming<(Method, RequestUri)>` type. Then the request is validated in a validate function.

#### `validate` function

The `validate` function is responsible for validating the HTTP request. It receives three parameters

- HTTP method: MUST be GET
- HTTP version: MUST above HTTP1.1
- HTTP headers:
  - WebSocket version MUST be WebSocket13
  - Upgrade fields protocols all MUST be "websocket"
  - Iterate all connection options and one of them MUST be "upgrade"

```rust
#[cfg(any(feature = "sync", feature = "async"))]
/// Check whether an incoming request is a valid WebSocket upgrade attempt.
pub fn validate(
	method: &Method,
	version: HttpVersion,
	headers: &Headers,
) -> Result<(), HyperIntoWsError> {
	if *method != Method::Get {
		return Err(HyperIntoWsError::MethodNotGet);
	}

	if version == HttpVersion::Http09 || version == HttpVersion::Http10 {
		return Err(HyperIntoWsError::UnsupportedHttpVersion);
	}

	if let Some(version) = headers.get::<WebSocketVersion>() {
		if version != &WebSocketVersion::WebSocket13 {
			return Err(HyperIntoWsError::UnsupportedWebsocketVersion);
		}
	}

	if headers.get::<WebSocketKey>().is_none() {
		return Err(HyperIntoWsError::NoSecWsKeyHeader);
	}

	match headers.get() {
		Some(&Upgrade(ref upgrade)) => {
			if upgrade.iter().all(|u| u.name != ProtocolName::WebSocket) {
				return Err(HyperIntoWsError::NoWsUpgradeHeader);
			}
		}
		None => return Err(HyperIntoWsError::NoUpgradeHeader),
	};

	fn check_connection_header(headers: &[ConnectionOption]) -> bool {
		for header in headers {
			if let ConnectionOption::ConnectionHeader(ref h) = *header {
				if UniCase(h as &str) == UniCase("upgrade") {
					return true;
				}
			}
		}
		false
	}

	match headers.get() {
		Some(&Connection(ref connection)) => {
			if !check_connection_header(connection) {
				return Err(HyperIntoWsError::NoWsConnectionHeader);
			}
		}
		None => return Err(HyperIntoWsError::NoConnectionHeader),
	};

	Ok(())
}
```

If the request is validated successfully, a `Upgrade` struct is returned.

`Upgrade` type is actually `WsUpgrade` type, it is the type to process HTTP switching to WebSocket. 

#### `WsUpgrade`

`WsUpgrade` is an intermediate representation of a half created websocket session. It's used to examine the client's handshake, accept the protocols requested, route the path, etc.

Users should then call `accept` or `reject` to complete the handshake and start a session or to reject a connection.

WsUpgrade contains the following fields:

- header: used in the handshake response
- stream: the TCP connection stream, used to read from / write to
- request: filled with useful metadata
- buffer: some buffered data from the stream, if it exists.

Let's see how `WsUpgrade` accepts. 

```rust
	fn internal_accept(mut self, headers: Option<&Headers>) -> Result<Client<S>, (S, io::Error)> {
		let status = self.prepare_headers(headers);

		if let Err(e) = self.send(status) {
			return Err((self.stream, e));
		}

		let stream = match self.buffer {
			Some(Buffer { buf, pos, cap }) => BufReader::from_parts(self.stream, buf, pos, cap),
			None => BufReader::new(self.stream),
		};

		Ok(Client::unchecked(stream, self.headers, false, true))
	}
```

First, prepare a HTTP response according to the WebSocket specification. Then a response is formatted as such:

```rust
	#[cfg(feature = "sync")]
	fn send(&mut self, status: StatusCode) -> io::Result<()> {
		let data = format!(
			"{} {}\r\n{}\r\n",
			self.request.version, status, self.headers
		);
		self.stream.write_all(data.as_bytes())?;
		Ok(())
	}
```

After all this preparation, a WebSocket connection has been established. Subsequent communication will be handled by the `Client` struct.

### Client

A `Client` just wraps around a `Stream` (which is something can be read from / write to) and handles the websocket protocol. 

A `Client` can also be split into a `Reader` and `Writer` which can then be moved to different threads, often using a send loop and receiver loop concurrently. This is only possible for streams that implement the `Splittable` trait, which currently is only TCP streams.

```rust
pub struct Client<S> where S: Stream {
	stream: BufReader<S>,
	headers: Headers,
	sender: Sender,
	receiver: Receiver,
}
```

- stream: stream is a wrapper of `TcpStream` or any other stream that implements the `Stream` trait. But with a `Stream`, you can only read or write, so a `BufReader` is wrapped to record buffer metadata like buffer capacity, current position, etc. 
- sender: sender is an implementation of the trait `Sender`, a sender is able to send data frames and messages. 



#### `Sender`

A `Sender` should be able to send data frames and messages. Sending data frames is defined by the trait `DataFrame`, sending messages is defined by the trait `Message`. 

```rust
/// A trait for sending data frames and messages.
pub trait Sender {
	/// Should the messages sent be masked.
	/// See the [RFC](https://tools.ietf.org/html/rfc6455#section-5.3)
	/// for more detail.
	fn is_masked(&self) -> bool;

	/// Sends a single data frame using this sender.
	fn send_dataframe<D, W>(&mut self, writer: &mut W, dataframe: &D) -> WebSocketResult<()>
	where
		D: DataFrame,
		W: Write,
	{
		dataframe.write_to(writer, self.is_masked())?;
		Ok(())
	}

	/// Sends a single message using this sender.
	fn send_message<M, W>(&mut self, writer: &mut W, message: &M) -> WebSocketResult<()>
	where
		M: Message,
		W: Write,
	{
		message.serialize(writer, self.is_masked())?;
		Ok(())
	}
}
```

#### `DataFrame`

`DataFrame` is a trait, and is an abstraction of a Data Frame. A `DataFrame` should be able to provide the following methods:

```rust
/// A generic DataFrame. Every dataframe should be able to
/// provide these methods. (If the payload is not known in advance then
/// rewrite the write_payload method)
pub trait DataFrame {
	/// Is this dataframe the final dataframe of the message?
	fn is_last(&self) -> bool;
	/// What type of data does this dataframe contain?
	fn opcode(&self) -> u8;
	/// Reserved bits of this dataframe
	fn reserved(&self) -> &[bool; 3];

	/// How long (in bytes) is this dataframe's payload
	fn size(&self) -> usize;

	/// Get's the size of the entire dataframe in bytes,
	/// i.e. header and payload.
	fn frame_size(&self, masked: bool) -> usize;

	/// Write the payload to a writer
	fn write_payload(&self, socket: &mut dyn Write) -> WebSocketResult<()>;

	/// Takes the payload out into a vec
	fn take_payload(self) -> Vec<u8>;

	/// Writes a DataFrame to a Writer.
    /// Writer normally is a Stream.
	fn write_to(&self, writer: &mut dyn Write, mask: bool) -> WebSocketResult<()>;
}
```

Actually both `DataFrame` struct and `Message` struct implement this `DataFrame` trait. And `DataFrame` trait provides a default implementation of the `write_to` method, both `DataFrame` struct and `Message` struct use the default implementation.

```rust
	/// Writes a DataFrame to a Writer.
    /// Writer normally is a Stream.
	fn write_to(&self, writer: &mut dyn Write, mask: bool) -> WebSocketResult<()> {
		let mut flags = dfh::DataFrameFlags::empty();
		if self.is_last() {
			flags.insert(dfh::DataFrameFlags::FIN);
		}
		{
			let reserved = self.reserved();
			if reserved[0] {
				flags.insert(dfh::DataFrameFlags::RSV1);
			}
			if reserved[1] {
				flags.insert(dfh::DataFrameFlags::RSV2);
			}
			if reserved[2] {
				flags.insert(dfh::DataFrameFlags::RSV3);
			}
		}

		let masking_key = if mask { Some(mask::gen_mask()) } else { None };

		let header = dfh::DataFrameHeader {
			flags,
			opcode: self.opcode() as u8,
			mask: masking_key,
			len: self.size() as u64,
		};

		let mut data = Vec::<u8>::new();
		dfh::write_header(&mut data, header)?;

		match masking_key {
			Some(mask) => {
				let mut masker = Masker::new(mask, &mut data);
				self.write_payload(&mut masker)?
			}
			None => self.write_payload(&mut data)?,
		};
		writer.write_all(data.as_slice())?;
		Ok(())
	}
```

So the default implementation does not fragment the message no matter how big the message is. It just write the header and the payload to a buffer called `data`, but how the payload is written to the buffer is implemented by structs that implement `DataFrame`.


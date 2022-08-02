# AWDL 实现

### 帧

802.11 MAC 帧结构：

![img](https://witestlab.poly.edu/blog/content/images/2017/03/wifi-frame-1.svg)

- FC：指示帧类型，包括控制、管理和数据三种类型，并且可以具体提供一些控制信息

- D/I：如果用于表示持续时间，则表示用于传输MAC帧的信道的持续时间；在一些控制帧中，这个字段也可以表示连接

- Addresses：接下来的三个MAC地址分别表示:

  - Receiver Address: MAC帧下一跳的目的地址
  - Transmitter Address: 当前发送主体的MAC地址
  - Destination Address: 最终的目的地址

  比如在同一个WLAN中的两个设备A给B发送报文，由于需要经过AP，因此需要两跳，对于第一跳，Receiver Address 就是AP的MAC地址，Transmitter Address 就是A的MAC地址，Destination Address 就是B的MAC地址。

- SC：包含一个4bit的分段序号，用于分段和重组；和一个12bit的序列号用于在发送者和接收者之间的发送的帧进行编号。

- Address：发送该帧的源地址

- Frame Body：包含一个MSDU或MSDU的一个分段

- CRC：4字节的循环冗余检查。

### AWDL

#### awdl_schedule

设置多个定时器：

- awdl_switch_channel: 更换信道的定时器
- awdl_clean_peers: 清楚其它节点的定时器
- awdl_send_psf: 定时发送PSF(Periodic Synchronization Frame)
- awdl_send_mif: 发送MIF(Master Indication Frame)，这里并不是定时发送，而是在start以后立即发送，并且不重复发送。也就是说，每个AWDL节点在被激活时都会发送一个MIF帧，在AWDL群组创建初期，这个帧有可能使得节点成为主节点，在后期则会收到主节点的更高metric的帧，自动成为从节点。
- awdl_send_unicast: 单播，即单独发送报文给某个节点。
- awdl_send_multicast: 多播，即发送报文给多个节点。

设置多个IO触发器：

- wlan_device_ready: 网卡有数据到达
- host_device_ready: 主机有数据到达

### IO

```c
struct io_state {
	pcap_t *wlan_handle;
	char wlan_ifname[PATH_MAX]; /* name of WLAN iface */
	int wlan_ifindex;     /* index of WLAN iface */
	char host_ifname[IFNAMSIZ]; /* name of host iface */
	int host_ifindex;     /* index of host iface */
	struct ether_addr if_ether_addr; /* MAC address of WLAN and host iface */
	int wlan_fd;
	int host_fd;
	char *dumpfile;
	char wlan_no_monitor_mode;
	int wlan_is_file;
};
```

上面为 io_state 的结构体，主要需要关注的为两个文件描述符，wlan_fd 和 host_fd。由于本程序充当一个代理的作用，一方面需要接收各个进程可能发送到AWDL网络的数据以及接收到达的数据，这需要用到 host_fd; 另一方面需要从网卡接收和发送数据，这需要用到 wlan_fd。

#### Wlan IO State Initialization

wlan_fd 主要通过调用 `open_nonblocking_device` 函数创建，其中主要用到的库为libpcap。在计算机网络管理领域内，pcap 是一套用于实时抓取网络包的接口，其在类Unix系统中的实现就是libpcap库。

`open_nonblocking_device` 函数通过libpcap库设置网卡选项，比如设置混杂模式(Promiscuous Mode)来接收所有经过的数据流，无论目的地址是否是自己。最后通过调用`pcap_get_selectable_fd`获取对应网络设备的文件描述符作为 wlan_fd。

#### Host IO State Initilization

最重要的是 `opentun` 函数，此函数读写Linux的/dev/net/tun 文件，实际设置为 TAP设备，并且非阻塞，mtu为1450字节。

TUN/TAP 设备即为Linux的虚拟网络设备，发送到TAP设备的数据相当于发送到网卡上。

```
+----------------------------------------------------------------+
|                                                                |
|  +--------------------+      +--------------------+            |
|  | User Application A |      | User Application B |<-----+     |
|  +--------------------+      +--------------------+      |     |
|               | 1                    | 5                 |     |
|...............|......................|...................|.....|
|               ↓                      ↓                   |     |
|         +----------+           +----------+              |     |
|         | socket A |           | socket B |              |     |
|         +----------+           +----------+              |     |
|                 | 2               | 6                    |     |
|.................|.................|......................|.....|
|                 ↓                 ↓                      |     |
|             +------------------------+                 4 |     |
|             | Newwork Protocol Stack |                   |     |
|             +------------------------+                   |     |
|                | 7                 | 3                   |     |
|................|...................|.....................|.....|
|                ↓                   ↓                     |     |
|        +----------------+    +----------------+          |     |
|        |      eth0      |    |      tun0      |          |     |
|        +----------------+    +----------------+          |     |
|    10.32.0.11  |                   |   192.168.3.11      |     |
|                | 8                 +---------------------+     |
|                |                                               |
+----------------|-----------------------------------------------+
                 ↓
         Physical Network
```

io_state 的 host_fd 即为 TAP设备的文件描述符。

### Tx

关于发送数据的部分，我们可以从主机有数据到达时的回调函数`host_device_ready`开始分析。

#### host_device_ready

通过 `poll_host_device` 获取主机数据，然后根据目的MAC地址判断是否是多播，是则调用 `awdl_send_multicast` 否则调用 `awdl_send_unicast`。

#### poll_host_device

根据 host_fd 从主机读取报文，如果是单播报文，则直接返回；如果是多播报文，则多次循环获取所有报文直至循环队列溢出。

#### awdl_send_unicast

从buf中读取目的MAC地址：

- 发送给自己的帧：通过`host_send`发送回去并返回
- 地址不在peers中，丢弃帧
- 判断当前是否可以发送数据帧，如果可以，则调用 `awdl_send_data` 发送帧

如果帧没有发送出去，则说明需要等待一段时间才能发送，需要重置定时器；如果已经发送，则调用 `ev_feed_event` 将 `read_host` 重新加入 pending 队列中。

#### awdl_send_multicast

多播需要发送的帧存储在一个循环队列中，当队列非空时，判断是否在多播帧的发送时间内，如果是则发送队列的第一个帧。如果队列仍然非空，则重置定时器；如果空，则将 `read_host` 加入pending队列。

### Rx

同样，接收端从 `wlan_device_ready` 回调函数开始分析，`wlan_device_ready` 实际上也是调用 `pcap_dispatch` 函数，其函数签名为：

```c
int pcap_dispatch(pcap_t *p, int cnt, pcap_handler callback, u_char *user);
```

其接收 `cnt` 个包并通过 `callback` 函数处理后返回，`p` 即对应一个已经创建并初始化的网络设备，`user` 则是一个用户可以在回调函数中使用的指针参数。

这里设置每次处理一个包，回调函数为 `awdl_receive_frame`。

#### awdl_receive_frame

函数签名为：

```c
void awdl_receive_frame(uint8_t* user, const struct pcap_pkthdr* hdr, const uint8_t* buf);
```

该函数负责将AWDL的帧进行处理之后转换为普通的数据链路层的帧之后传给host。

#### awdl_rx

awdl_rx 的函数签名为：

```c
int awdl_rx(const struct buf* frame, struct buf*** data_frame, struct awdl_state* state);
```

`frame` 即为需要处理的帧，`data_frame` 即为数据帧数组的指针引用，`state`即为awdl状态。其主要功能是解析接收到的帧剖析之后去除 ieee80211_radiotap_header, ieee80211_hdr, lcc_hdr, awdl_data 四重头部后转换为以太网帧并覆盖 `data_frame` 数组对应的 buf 指针。

awdl_rx 首先使用 radiotap 库解析frame，得到 RSSI(Received Signal Strength Indicator)和flags 值。flags 可以用于校验FCS值。然后脱去`radiotap_header` 头部。

接下来为 `ieee80211_hdr` 的头部，下图为 IEEE 802.11 的帧结构：

![img](https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/802.11_frame.png/622px-802.11_frame.png)

对应的结构体为：

```c
struct ieee80211_hdr {
	uint16_t frame_control;
	uint16_t duration_id;
	struct ether_addr addr1; /* dst */
	struct ether_addr addr2; /* src */
	struct ether_addr addr3; /* bssid */
	uint16_t seq_ctrl;
} __attribute__((__packed__));
```

然后将 `ieee80211_hdr` 从frame 剥离，根据 frame_control 的值来进行下一步操作：

- IEEE80211_FTYPE_MGMT | IEEE80211_STYPE_ACTION：

  管理帧，调用 `awdl_rx_action`函数进行处理。

- IEEE80211_FTYPE_DATA | IEEE80211_STYPE_DATA | IEEE80211_STYPE_QOS_DATA

  数据帧，可能包括QoS，从frame 读取 qosc，判断是否设置A-MSDU。如果有，则调用 `awdl_rx_data_amsdu` 函数。A-MSDU 即 Aggregate MAC Service Data Unit, 其将多个以太网帧打包成一个 802.11n 帧，由于以太网帧头长度远小于802.11n帧头长度，因此可以提高网络带宽的利用率。

  因此 `awdl_rx_data_amsdu` 函数的逻辑非常好理解，只需要通过一个循环不断从 frame 中取出 subframe, 然后调用 `awdl_rx_data` 函数传输。

- IEEE80211_FTYPE_DATA | IEEE80211_STYPE_DATA

  一般的数据帧，直接调用 `awdl_rx_data` 函数。`awdl_rx_data` 主要负责修改数据帧，首先需要检查源地址是否在peers 中，如果不是则丢弃帧；然后校验LLC header。此时frame 主要包括的头部为逻辑链路层的头部和awdl加的头部。

  ```c
  struct llc_hdr {
  	uint8_t dsap;
  	uint8_t ssap;
  	uint8_t control;
  	/* SNAP extension */
  	struct oui oui;
  	uint16_t pid;
  } __attribute__((__packed__));
  ```

  `llc_header` 的校验包括：

  - dsap, ssap 固定为 0xaa;
  - control 为 0x03;
  - pid: AWDL_LLC_PROTOCOL_ID;

  ```c
  struct awdl_data {
  	uint16_t head; /* AWDL_DATA_HEAD */
  	uint16_t seq;
  	uint16_t pad; /* AWDL_DATA_PAD */
  	uint16_t ethertype;
  } __attribute__((__packed__));
  ```

  `awdl_data` 需要读取 ethertype field, 然后创建一个新的 buf 表示以太网帧，需要写入的内容包括源、目的地址，ethertype和frame中的数据。

#### awdl_rx_action

函数签名为：

```c
int awdl_rx_action(const struct buf* frame, signed char rssi, uint64_t tsft, const struct ether_addr* src, const struct ether_addr* src, const struct ether_addr* dst, struct awdl_state* state);
```

在接收到action 帧之后，首先需要对帧头部进行解析 `awdl_parse_action_hdr`。

```c
struct awdl_action {
	uint8_t category; /* 127 - vendor-specific */
	struct oui oui;
	uint8_t type;
	uint8_t version;
	uint8_t subtype; /* awdl_frame_types */
	uint8_t reserved;
	uint32_t phy_tx;
	uint32_t target_tx;
} __attribute__((__packed__));
```

解析过程中会校验 category, oui, type, version 等字段，并返回subtype字段。

如果有设置 filter_rssi，则需要检验源节点的RSSI(Received Signal Strength Indication)，过小的RSSI的节点的帧不被接受。

随后调用 `awdl_peer_add` 更新路由表邻节点，AWDL节点通过一个hashmap 来管理所有的节点的MAC地址到对应结构体的映射。

```c
struct awdl_peer {
	const struct ether_addr addr;
	uint64_t last_update;
	struct awdl_election_state election;
	struct awdl_chan sequence[AWDL_CHANSEQ_LENGTH];
	uint64_t sync_offset;
	char name[HOST_NAME_LENGTH_MAX + 1]; /* space for trailing zero */
	char country_code[2 + 1];
	struct ether_addr infra_addr;
	uint8_t version;
	uint8_t devclass;
	uint8_t supports_v2 : 1;
	uint8_t sent_mif : 1;
	uint8_t is_valid : 1;
};
```

如果在map中没有找到对应地址的节点，则说明是一个新节点，则需要创建一个peer结构体并添加到map中。

除此之外，添加节点还涉及到内核网络协议栈的操作，通过netlink库分别构造网络层和数据链路层地址，并添加到路由表中构成映射。其中网络层地址是IPv6地址，IPv6的地址可由以太网地址构造得到。具体参考 `rfc4291_addr` 函数，在论文中也有所提到。

上述操作是由 `neighbor_add_rfc4291` 函数完成的，对于macOS和Linux的具体实现并不一致。且该函数的调用并不是硬编码的，而是由回调函数的形式被调用，具体使用哪个回调函数在 `awdl_init` 时决定。

根据action帧结构，在 `sizeof(struct awdl_action)` 之后为多个TLV字段。需要对这些TLV进行解析从而获取action帧的意图。TLV 的类型可以由subtype字段获取。

#### awdl_handle_tlv

根据subtype的值调用不同的处理函数读取并处理TLV。

#### awdl_handle_sync_params_tlv

 #### awdl_handle_chanseq_tlv

函数签名为：

```c
int awdl_handle_chanseq_tlv(struct awdl_peer* src, const struct buf* val, struct awdl_state* state __attribute__((unused)));
```

从buf中读取一段信道序列，此信道序列表示与 `src` 对应的节点通信的信道序列，因此如果接收序列与 `src` 中的信道序列不同，则需要将接收的信道序列复制到 `src` 中。

#### awdl_handle_election_params_tlv

```c
int awdl_handle_election_parames_tlv(struct awdl_peer* src, const struct buf* val, struct awdl_state* state __attribute__((unused)));
```

更新 `src` 的 master_addr, master_metric, self_metric 等字段。

#### awdl_handle_election_params_v2_tlv

```c
int awdl_handle_election_parames_tlv(struct awdl_peer* src, const struct buf* val, struct awdl_state* state __attribute__((unused)));
```

与上一个函数类似，但是读取的字段更多。

#### awdl_handle_data_path_state_tlv

```c
int awdl_handle_election_parames_tlv(struct awdl_peer* src, const struct buf* val, struct awdl_state* state __attribute__((unused)));
```



### 信道

awdl 信道结构体：

```c
struct awdl_chan {
	union {
		uint8_t val[2];
		struct {
			uint8_t chan_num;
		} simple;
		struct {
			uint8_t flags;
			uint8_t chan_num;
		} legacy;
		struct {
			uint8_t chan_num;
			uint8_t opclass;
		} opclass;
	};
};
```

信道状态：

```c
struct awdl_channel_state {
	enum awdl_chan_encoding enc;
	struct awdl_chan sequence[AWDL_CHANSEQ_LENGTH];
	struct awdl_chan master;//主节点信道		
	struct awdl_chan current;//当前信道
};
```

Linux 下设置网络接口频率：

```c
int set_channel(int ifindex, int channel) {
	int err;
	struct nl_msg *m;
	int freq;

	freq = ieee80211_channel_to_frequency(channel);
	if (!freq) {
		log_error("Invalid channel number %d", channel);
		err = -EINVAL;
		goto out;
	}

	m = nlmsg_alloc();
	if (!m) {
		log_error("Could not allocate netlink message");
		err = -ENOMEM;
		goto out;
	}

	if (genlmsg_put(m, 0, 0, nl80211_state.nl80211_id, 0, 0, NL80211_CMD_SET_CHANNEL, 0) == NULL) {
		err = -ENOBUFS;
		goto out;
	}

	NLA_PUT_U32(m, NL80211_ATTR_IFINDEX, ifindex);
	NLA_PUT_U32(m, NL80211_ATTR_WIPHY_FREQ, freq);
	NLA_PUT_U32(m, NL80211_ATTR_WIPHY_CHANNEL_TYPE, NL80211_CHAN_HT40PLUS);

	err = nl_send_auto(nl80211_state.socket, m);
	if (err < 0) {
		log_error("error while sending via netlink");
		goto out;
	}

	err = nl_recvmsgs_default(nl80211_state.socket);
	goto out;

nla_put_failure:
	log_error("building message failed");
	err = -ENOBUFS;
out:
	if (m)
		nlmsg_free(m);
	return err;
}
```

通过创建一个包含了`NL80211_CMD_SET_CHANNEL`命令的message并发送给内核网络协议栈，从而改变网卡的工作频率。

### 同步

```c
struct awdl_sync_state {
	uint16_t aw_counter;
	uint64_t last_update; /* in us */
	uint16_t aw_period; /* in TU */
	uint8_t presence_mode;

	/* statistics */
	uint64_t meas_err;
	uint64_t meas_total;
};
```

### Frame Receive

Frame 的处理流程，首先通过 `awdl_receive_frame` 函数接收，然后通过`awdl_rx` 函数处理成以太网帧之后传给host。


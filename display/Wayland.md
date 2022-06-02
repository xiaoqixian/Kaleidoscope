## Wayland

Wayland 是 Linux 上的一款显示协议，其致力于成为古老的 X 协议的一个更简洁的替代品。目前 KDE 和 Gnome 桌面系统都有计划迁移到 Wayland。

Wayland 即代表了一款协议，也代表了一个实现了该协议的 C 库。

开始前如果你可能有必要了解一下渲染(rendering) 和合成(compositing) 的区别，一个桌面上可能有许多窗口，渲染是相对窗口而言，根据应用程序来决定窗口应该呈现什么样的内容，但是不同窗口可能互相存在堆叠，因此需要将多个窗口的渲染图像合成来组成整的屏幕的图像。

### Wayland 架构

传统的 X 协议的架构：

![](https://wayland.freedesktop.org/x-architecture.png)

1. 内核从输入设备中断中获得一个事件并将其通过 evdev 输入设备驱动发送给 X 服务器。内核需要负责驱动设备并将各种不同输入设备的事件转换成符合 evdev 驱动标准的事件。
2. X 服务器决定该事件影响哪个窗口，并将其发送给该窗口上的相关事件选择的客户端。X 服务器并不知道如何将事件发送给正确的窗口，因为窗口的位置由渲染合成器（Compositer）掌控。
3. 客户端查看事件并决定如何处理，通常处理包括图形界面的变化，比如用户点击一个按钮，客户端则需要将图形界面变化的渲染需求返回给 X 服务器。
4. X 服务器接收到渲染需求之后，其将其发送给相应的显示驱动让其计算渲染缓冲。X 服务器同时还要计算渲染的边界区域并将其以 *毁灭事件(damage event)* 的形式发送给合成器。
5. 毁灭事件意味着窗口发生了改变，合成器需要重新合成该窗口可见部分的屏幕区域。合成器负责渲染整个屏幕区域，包括屏保和各个窗口的内容。但是其必须向 X 服务器请求来在显示器上渲染这些。因此合成器可以看作一个特殊的客户端。
6. X服务器接收来自排字器的渲染请求，或者将排字器的后端缓冲区复制到前端缓冲区，或者进行翻页。在一般情况下，X服务器必须执行这一步，以便考虑重叠的窗口，这可能需要剪切并确定是否可以翻页。然而，对于始终是全屏的排字器，这是另一个不必要的上下文切换。

显然对于 X 协议的显示方法有几点问题。X 服务器既不掌控各个窗口的位置信息，也无法将屏幕坐标转换为窗口内的相对坐标。总的来说，X 服务器只是一个介于程序与合成器，合成器与硬件之间的中间人，它的存在使得双方的交流多了一步。

而在 Wayland 中，只存在一个合成器作为中间人：

![](https://wayland.freedesktop.org/wayland-architecture.png)

1. 内核接收到事件之后直接发送给合成器，这一步与 X 协议相同，同时也是必要的，因为所有驱动都工作在内核态。
2. 合成器扫描其屏幕信息来决定哪个窗口应该接收事件，并且合成器可以直接将屏幕坐标转换为窗口坐标。
3. 在 X 协议中，客户端接收到事件之后，其根据事件更新自己的UI。在 Wayland 中，渲染部分发生在客户端中，再由客户端给合成器发送请求哪部分需要更新。
4. 合成器从客户端中接收 damage requests 并重新合成屏幕图像

### Wayland 客户端渲染

上面没有提到的一点是 Wayland 客户端的渲染方式。

Wayland 客户端采用直接渲染（direct rendering)，直接渲染下，客户端和服务端共用一段 video memory buffer, 客户端通过相应的库对这段缓冲进行渲染然后通知合成器应该使用那个缓冲以及其渲染的时间和区域。

通常客户端在渲染时可以保持两个及以上的buffer用于渲染，因为如果实际如果客户端和合成器真的只共用一段buffer 的话，可能的结果就是合成器还未来得及合成数据就被修改，导致窗口屏幕只渲染了一半。

因此使用两个buffer 是比较常用的做法。

### Wayland 的硬件支持

涉及到更加复杂的计算机图形显示方面的知识，略。
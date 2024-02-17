# typst 技巧合集

#### 前言

typst 作为一个刚诞生不久的、对标 LaTex 的排版语言, 其有很多的创新点. 但是不可避免的有很多的不足之处. 

我觉得目前一个比较大的缺点就是文档的缺失. 虽然 typst 建有一个专门的文档网站, 但是其中的内容写得过于简略, 同时 typst 本身是一门非常偏向函数式编程的语言, 从而导致要实现一些复杂的排版技巧非常困难. 很多时候只能从一些官方以及各路大神写的模板和库中推敲一些比较高级的技巧. 

所以这里我整理了一些可以用到的 typst 技巧.

#### 1. 调整 terms 的格式

例如, 如果我需要对名词及其解释使用不同的字体, 可以借用 show rules 

```typst
#show terms.item: it => [
  #text(font: ("Skia", "Kai"), weight: "bold")[#it.term]
  #h(1em)
  #it.description
]
```

#### 2. 对定理进行标号

有时需要对定理进行标号, 做出类似 “定理 4.2.1” 的效果, 表示这是第4章第2节的第一个定理. 虽然 typst 提供了 counter 类型, 但是无法做出按章节进行计数的效果. 

首先, 需要一个 state 类型用于保存一个数组, 表示当前出现过定理的章节. 当在一个新的章节写下定理时, 我们需要查询该数组, 该章节是否出现过, 没有则存入该数组. 同时初始化一个 counter. 如果章节之前出现过, 则直接对 counter 进行更新.

```typst
#let theorem(
  spacing: 2pt, 
  indent: 1em, 
  name: "定理", 
  level: 2, 
  font: "Hei",
  content
) = locate(loc => {
  let levels = counter(heading).at(loc)
  if level < levels.len() {
    let level = levels.len()
  }

  let cter_id = name + levels.slice(0, level).map(str).join(".")
  entry_map.update(arr => {
    let res = arr.find(x => x == cter_id)
    if res == none {
      // init counter state here.
      let _ = state(cter_id, 0)
      return (..arr, cter_id)
    }
    else {
      return arr
    }
  })

  state(cter_id).update(x => x+1)
  state(cter_id).display(x => {
    let cter_str = cter_id + "." + str(x)
    return [
      #text(font: font, weight: "bold")[
        #h(indent)
        #h(spacing)
        #cter_str
        #h(spacing)
      ]
      #content
    ]
  })
})
```

参数:

- spacing: content 距离标号的长度
- indent: 定理的缩进长度
- name: 使用的定理的名字, 默认是“定理”, 可以是“命题”, “结论” 等.
- level: 标号追踪的最深的章节深度
- font: “定理” 及标号使用的字体(内容使用的字体无影响)

#### 3. 获取当前页面大小

​	首先需要通过一个 `state` 保存页面大小信息,

```typst
#let page_state = state(width: 0pt, height: 0pt)
```

然后通过 `place` 将一个虚拟元素放置到右下角, 此时可通过 `locate` 函数获取到位置信息, 从而对 `page_state` 完成更新.

```typst
#place(bottom+right, locate(loc => {
	page_state.update(s => {
		let pos = loc.position()
		(width: pos.x, height: pos.y)
	})
}))
```



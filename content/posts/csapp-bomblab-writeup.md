---
title: 'CS:APP Bomblab 游玩记录'
date: 2021-08-25T14:52:15+08:00
draft: false
categories: ["题解"]
tags: ["逆向", "ICS"]
featuredImage: 'https://pic.rvalue.moe/2021/08/25/37a9213a8f221.png'
---

假期无聊的自己想起之前读 CS:APP 但是没有仔细做里面的 lab, 于是挑个 (也许) 最好玩的先来玩一玩正好边玩边写

<!--more-->

Bomblab 所用到的资源可以在 [GitHub](https://github.com/Hansimov/csapp/tree/master/_labs/02%20bomb%20lab) 找到.

以下二进制分析基于上述链接中的 `bomb` 文件, x86-64 汇编使用 Intel 语法.

## 初步分析

lab 中包含一个 ELF 格式的 `bomb` 以及一个 `bomb.c`. 其中 `bomb.c` 包含程序的大致逻辑但不包含各个 phase 的具体实现.

先分析下 `bomb` 的信息, 使用 `readelf` 可以得到:

```plain
❯ readelf -h bomb
ELF Header:
  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00
  Class:                             ELF64
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              EXEC (Executable file)
  Machine:                           Advanced Micro Devices X86-64
  Version:                           0x1
  Entry point address:               0x400c90
  Start of program headers:          64 (bytes into file)
  Start of section headers:          18616 (bytes into file)
  Flags:                             0x0
  Size of this header:               64 (bytes)
  Size of program headers:           56 (bytes)
  Number of program headers:         9
  Size of section headers:           64 (bytes)
  Number of section headers:         36
  Section header string table index: 33
```

根据得到的信息可以知道这个可执行文件的指令集是 x86-64 且使用 System V ABI.

`bomb.c` 中的大致逻辑为, 整个 bomb 包含 6 个 phase, 每个 phase 需要用户输入一行字符串. 如果带参数则会优先从文件中读取字符串, EOF 之后自动切换到标准输入读取. 每个 phase 中会将输入的字符串作为参数传递给 `void phase_x(char*)`, 只要该函数正常执行完毕即算该 phase 通过.

P.S.: `bomb.c` 里面有一些很有意思的彩蛋注释

## Phase 1

用 `objdump` 稍微反汇编一下就可以发现是简单的字符串比较.

```asm
0000000000400ee0 <phase_1> (File Offset: 0xee0):
  400ee0:   48 83 ec 08             sub    rsp,0x8
  400ee4:   be 00 24 40 00          mov    esi,0x402400
  400ee9:   e8 4a 04 00 00          call   401338 <strings_not_equal> (File Offset: 0x1338)
  400eee:   85 c0                   test   eax,eax
  400ef0:   74 05                   je     400ef7 <phase_1+0x17> (File Offset: 0xef7)
  400ef2:   e8 43 05 00 00          call   40143a <explode_bomb> (File Offset: 0x143a)
  400ef7:   48 83 c4 08             add    rsp,0x8
  400efb:   c3                      ret
```

根据 x86-64 的 calling convention 可以知道调用 `string_not_equal` 时 `esi` 中的地址 `0x402400` 即为比较目标. `objdump -h` 一下找这个内存地址对应的文件偏移可以得到 `0x2400`, 用 `xxd` 找一下对应的文件偏移 `0x2400` 的位置可以找到:

```plain
00002400: 426f 7264 6572 2072 656c 6174 696f 6e73  Border relations
00002410: 2077 6974 6820 4361 6e61 6461 2068 6176   with Canada hav
00002420: 6520 6e65 7665 7220 6265 656e 2062 6574  e never been bet
00002430: 7465 722e 0000 0000 576f 7721 2059 6f75  ter.....Wow! You
```

所以第一个 phase 的 key 就是

```plain
Border relations with Canada have never been better.
```

## Phase 2

照例先看一下 `phase_2` 的逆向:

```asm
0000000000400efc <phase_2> (File Offset: 0xefc):
  400efc:   55                      push   rbp
  400efd:   53                      push   rbx
  400efe:   48 83 ec 28             sub    rsp,0x28
  400f02:   48 89 e6                mov    rsi,rsp
  400f05:   e8 52 05 00 00          call   40145c <read_six_numbers> (File Offset: 0x145c)
  400f0a:   83 3c 24 01             cmp    DWORD PTR [rsp],0x1
  400f0e:   74 20                   je     400f30 <phase_2+0x34> (File Offset: 0xf30)
  400f10:   e8 25 05 00 00          call   40143a <explode_bomb> (File Offset: 0x143a)
  400f15:   eb 19                   jmp    400f30 <phase_2+0x34> (File Offset: 0xf30)
  400f17:   8b 43 fc                mov    eax,DWORD PTR [rbx-0x4]
  400f1a:   01 c0                   add    eax,eax
  400f1c:   39 03                   cmp    DWORD PTR [rbx],eax
  400f1e:   74 05                   je     400f25 <phase_2+0x29> (File Offset: 0xf25)
  400f20:   e8 15 05 00 00          call   40143a <explode_bomb> (File Offset: 0x143a)
  400f25:   48 83 c3 04             add    rbx,0x4
  400f29:   48 39 eb                cmp    rbx,rbp
  400f2c:   75 e9                   jne    400f17 <phase_2+0x1b> (File Offset: 0xf17)
  400f2e:   eb 0c                   jmp    400f3c <phase_2+0x40> (File Offset: 0xf3c)
  400f30:   48 8d 5c 24 04          lea    rbx,[rsp+0x4]
  400f35:   48 8d 6c 24 18          lea    rbp,[rsp+0x18]
  400f3a:   eb db                   jmp    400f17 <phase_2+0x1b> (File Offset: 0xf17)
  400f3c:   48 83 c4 28             add    rsp,0x28
  400f40:   5b                      pop    rbx
  400f41:   5d                      pop    rbp
  400f42:   c3                      ret
```

~~P.S.: C语言写的炸弹不能直接逆向出函数签名有点难受~~

注意到它在函数 entry sequence 中将 `rsp` 拉低了 `0x28 = 40`, 结合将 `rsp` 的值放在 `rsi` 中传递给 `read_six_number` 可以推测它开辟了一块栈上的未知类型 buffer 并将其首地址作为第二个参数传递给 `read_six_number`. `rdi` 没有被改变, 说明 `read_six_number` 的第一个参数就是 `phase_2` 的第一个参数, 即键入的 key. 跟着 `call` 逆向 `read_six_number` 可以得到:

```asm
000000000040145c <read_six_numbers> (File Offset: 0x145c):
  40145c:   48 83 ec 18             sub    rsp,0x18
  401460:   48 89 f2                mov    rdx,rsi
  401463:   48 8d 4e 04             lea    rcx,[rsi+0x4]
  401467:   48 8d 46 14             lea    rax,[rsi+0x14]
  40146b:   48 89 44 24 08          mov    QWORD PTR [rsp+0x8],rax
  401470:   48 8d 46 10             lea    rax,[rsi+0x10]
  401474:   48 89 04 24             mov    QWORD PTR [rsp],rax
  401478:   4c 8d 4e 0c             lea    r9,[rsi+0xc]
  40147c:   4c 8d 46 08             lea    r8,[rsi+0x8]
  401480:   be c3 25 40 00          mov    esi,0x4025c3
  401485:   b8 00 00 00 00          mov    eax,0x0
  40148a:   e8 61 f7 ff ff          call   400bf0 <__isoc99_sscanf@plt> (File Offset: 0xbf0)
  40148f:   83 f8 05                cmp    eax,0x5
  401492:   7f 05                   jg     401499 <read_six_numbers+0x3d> (File Offset: 0x1499)
  401494:   e8 a1 ff ff ff          call   40143a <explode_bomb> (File Offset: 0x143a)
  401499:   48 83 c4 18             add    rsp,0x18
  40149d:   c3                      ret
```

注意到代码中有调用 PLT 定位的项, 按照名字推测是标准库中的 `sscanf` 函数, 可以以它的参数为突破口观察 `sscanf` 都读取了哪些信息. entry sequence 结束之后, 它将 `rsi` 中上文提到的 buffer 地址和该地址 +4 偏移的值分别加载到 `rdx` 和 `rcx`. 注意到直到 `sscanf` 被调用为止 `rdx` 和 `rcx` 的值都没有变化, 根据 [System V ABI](https://refspecs.linuxbase.org/elf/x86_64-abi-0.99.pdf) 的 calling convention 可知这两个地址分别是 `sscanf` 的第 3/4 个参数. 同理还有 `r8` 和 `r9`, 可知第 5/6 个参数分别是 `rsi+8` 和 `rsi+12`. System V ABI 在寄存器中最多传递 6 个整数参数, 其余两个参数在栈上传递且按照机器字长对齐, 可知 `QWORD PTR [rsp+0x8]` 即为第 8 个参数, `QWORD PTR [rsp]` 为第 7 个. 所以第 3~8 个参数为: `rsi`, `rsi+4`, `rsi+8`, `rsi+12`, `rsi+16`, `rsi+20`.

加载完参数 3~8 后它将一个静态地址 `0x4025c3` 加载进 `esi`, 即 `sscanf` 第 2 个参数的位置. 找一下对应的文件偏移 `0x25c3` 可以找到:

```plain
000025c0: 702e 0025 6420 2564 2025 6420 2564 2025  p..%d %d %d %d %
000025d0: 6420 2564 0045 7272 6f72 3a20 5072 656d  d %d.Error: Prem
```

所以实际上就是串 `%d %d %d %d %d %d`. 同时也可以推测出传进来的 buffer 是 `int` 数组, 读入目标是数组的前 6 个值.

与 `read_six_number` 的参数相同, `rdi` 没有被改变, 可知键入的字符串被一路传递到了 `sscanf` 作为第一个参数, 也就是读入目标.

`sscanf` 返回之后, `read_six_number` 将 `sscanf` 的返回值 (保存在 `eax` 里) 与 5 进行比较, 如果大于 5 则跳转到 `401499` 也就是 exit sequence 的位置返回, 否则会调用 `explode_bomb`. 推测要求 6 个整数全部成功读入.

回到 `phase_2` 中, 先判断 `buffer[0]` 是否为 1, 如果是则跳转到 `400f30` 将 `&buffer[1]` 和 `&buffer[6]` 分别赋给 `rbx` 和 `rbp`, 跳转回 `400f17`, 推断此时 `rbx` 和 `rbp` 都是 `int*`. 接着计算出 `*(rbx - 1) * 2` 的值并和 `*rbx` 比较, 推断要求 `buffer[i+1]=2*buffer[i]`, 然后将 `rbx` 指向下一个 `int` 地址并与 `rbp` 比较判断是否跳出到 exit sequence, 推断是一个循环判断整个长度为 6 的 `buffer` 是否满足 `buffer[i+1]=2*buffer[i]`. 据此构造出 key:

```plain
1 2 4 8 16 32
```

## Phase 3

照例先从入口开始:

```asm
0000000000400f43 <phase_3> (File Offset: 0xf43):
  400f43:   48 83 ec 18             sub    rsp,0x18
  400f47:   48 8d 4c 24 0c          lea    rcx,[rsp+0xc]
  400f4c:   48 8d 54 24 08          lea    rdx,[rsp+0x8]
  400f51:   be cf 25 40 00          mov    esi,0x4025cf
  400f56:   b8 00 00 00 00          mov    eax,0x0
  400f5b:   e8 90 fc ff ff          call   400bf0 <__isoc99_sscanf@plt> (File Offset: 0xbf0)
  400f60:   83 f8 01                cmp    eax,0x1
  400f63:   7f 05                   jg     400f6a <phase_3+0x27> (File Offset: 0xf6a)
  400f65:   e8 d0 04 00 00          call   40143a <explode_bomb> (File Offset: 0x143a)
  400f6a:   83 7c 24 08 07          cmp    DWORD PTR [rsp+0x8],0x7
  400f6f:   77 3c                   ja     400fad <phase_3+0x6a> (File Offset: 0xfad)
  400f71:   8b 44 24 08             mov    eax,DWORD PTR [rsp+0x8]
  400f75:   ff 24 c5 70 24 40 00    jmp    QWORD PTR [rax*8+0x402470]
  400f7c:   b8 cf 00 00 00          mov    eax,0xcf
  400f81:   eb 3b                   jmp    400fbe <phase_3+0x7b> (File Offset: 0xfbe)
  400f83:   b8 c3 02 00 00          mov    eax,0x2c3
  400f88:   eb 34                   jmp    400fbe <phase_3+0x7b> (File Offset: 0xfbe)
  400f8a:   b8 00 01 00 00          mov    eax,0x100
  400f8f:   eb 2d                   jmp    400fbe <phase_3+0x7b> (File Offset: 0xfbe)
  400f91:   b8 85 01 00 00          mov    eax,0x185
  400f96:   eb 26                   jmp    400fbe <phase_3+0x7b> (File Offset: 0xfbe)
  400f98:   b8 ce 00 00 00          mov    eax,0xce
  400f9d:   eb 1f                   jmp    400fbe <phase_3+0x7b> (File Offset: 0xfbe)
  400f9f:   b8 aa 02 00 00          mov    eax,0x2aa
  400fa4:   eb 18                   jmp    400fbe <phase_3+0x7b> (File Offset: 0xfbe)
  400fa6:   b8 47 01 00 00          mov    eax,0x147
  400fab:   eb 11                   jmp    400fbe <phase_3+0x7b> (File Offset: 0xfbe)
  400fad:   e8 88 04 00 00          call   40143a <explode_bomb> (File Offset: 0x143a)
  400fb2:   b8 00 00 00 00          mov    eax,0x0
  400fb7:   eb 05                   jmp    400fbe <phase_3+0x7b> (File Offset: 0xfbe)
  400fb9:   b8 37 01 00 00          mov    eax,0x137
  400fbe:   3b 44 24 0c             cmp    eax,DWORD PTR [rsp+0xc]
  400fc2:   74 05                   je     400fc9 <phase_3+0x86> (File Offset: 0xfc9)
  400fc4:   e8 71 04 00 00          call   40143a <explode_bomb> (File Offset: 0x143a)
  400fc9:   48 83 c4 18             add    rsp,0x18
  400fcd:   c3                      ret
```

第一眼看见里面一车的 `jmp` 感觉有种不祥的预感...

从头开始分析, 最开始是一个普通的开辟栈 buffer 和传参调用 `sscanf` 的过程, 和 `read_six_number` 差不多. 话不多说直接去找 `0x25cf` 写的啥:

```plain
000025c0: 702e 0025 6420 2564 2025 6420 2564 2025  p..%d %d %d %d %
000025d0: 6420 2564 0045 7272 6f72 3a20 5072 656d  d %d.Error: Prem
```

好家伙, 又是这

不过这次是从偏移 F 开始的, 所以只有 `%d %d`. 那就明白了, 输入是俩数, 第一个在 `rsp+0x8` , 第二个在 `rsp+0xc`. 不妨设它们为 `i` 和 `k`.

`sscanf` 返回后是和 `read_six_number` 类似的判断输入合法性的命令. 确认合法后跳转到 `400f6a` 也就是这里的第 11 行.

然后判断了一下如果 `i>7` 就直接爆炸, `i<=7` 则进入一个动态跳转命令, 跳转目标是一个内存引用, 推测是一个跳转表, 基址为 `402470`.

话不多说赶紧找 `0x2470` 都有啥:

```plain
00002470: 7c0f 4000 0000 0000 b90f 4000 0000 0000  |.@.......@.....
00002480: 830f 4000 0000 0000 8a0f 4000 0000 0000  ..@.......@.....
00002490: 910f 4000 0000 0000 980f 4000 0000 0000  ..@.......@.....
000024a0: 9f0f 4000 0000 0000 a60f 4000 0000 0000  ..@.......@.....
```

果然是个跳转表. 注意小端序低位字节在先, 可以列出跳转目标:

```plain
400f7c
400fb9
400f83
400f8a
400f91
400f98
400f9f
400fa6
```

回到对应的地址可以发现, 都是一些形如 `mov eax, ***` 后跳转到同一个 `400fbe` 的指令. 而 `400fbe` 位置的指令将 `k` 和 `eax` 比较, 如果相等才进入 exit sequence 否则引爆炸弹. 推测此处有多解, 8 个值中任意选择一个即可. 所以 key 可以是:

```plain
3 512
```

P.S.: 本来到这里觉得跳转表里可能有些值是非法的或者某些跳转表目标会引到陷阱位置, 仔细一看发现大概只是个普通的 `switch` (

## Phase 4

还是先看入口:

```asm
000000000040100c <phase_4> (File Offset: 0x100c):
  40100c:   48 83 ec 18             sub    rsp,0x18
  401010:   48 8d 4c 24 0c          lea    rcx,[rsp+0xc]
  401015:   48 8d 54 24 08          lea    rdx,[rsp+0x8]
  40101a:   be cf 25 40 00          mov    esi,0x4025cf
  40101f:   b8 00 00 00 00          mov    eax,0x0
  401024:   e8 c7 fb ff ff          call   400bf0 <__isoc99_sscanf@plt> (File Offset: 0xbf0)
  401029:   83 f8 02                cmp    eax,0x2
  40102c:   75 07                   jne    401035 <phase_4+0x29> (File Offset: 0x1035)
  40102e:   83 7c 24 08 0e          cmp    DWORD PTR [rsp+0x8],0xe
  401033:   76 05                   jbe    40103a <phase_4+0x2e> (File Offset: 0x103a)
  401035:   e8 00 04 00 00          call   40143a <explode_bomb> (File Offset: 0x143a)
  40103a:   ba 0e 00 00 00          mov    edx,0xe
  40103f:   be 00 00 00 00          mov    esi,0x0
  401044:   8b 7c 24 08             mov    edi,DWORD PTR [rsp+0x8]
  401048:   e8 81 ff ff ff          call   400fce <func4> (File Offset: 0xfce)
  40104d:   85 c0                   test   eax,eax
  40104f:   75 07                   jne    401058 <phase_4+0x4c> (File Offset: 0x1058)
  401051:   83 7c 24 0c 00          cmp    DWORD PTR [rsp+0xc],0x0
  401056:   74 05                   je     40105d <phase_4+0x51> (File Offset: 0x105d)
  401058:   e8 dd 03 00 00          call   40143a <explode_bomb> (File Offset: 0x143a)
  40105d:   48 83 c4 18             add    rsp,0x18
  401061:   c3                      ret
```

开始几行甚至和 `phase_3` 完全一致, 不用多想了就是输入俩数(

这次设成 `a` 和 `b` 吧.

验证过输入成功之后又判断了一下要求 `a` 不大于 15, 调用了一下 `func4(a, 0, 0xe)`. 跟着看一下 `func4` 都在干嘛:

```asm
0000000000400fce <func4> (File Offset: 0xfce):
  400fce:   48 83 ec 08             sub    rsp,0x8
  400fd2:   89 d0                   mov    eax,edx
  400fd4:   29 f0                   sub    eax,esi
  400fd6:   89 c1                   mov    ecx,eax
  400fd8:   c1 e9 1f                shr    ecx,0x1f
  400fdb:   01 c8                   add    eax,ecx
  400fdd:   d1 f8                   sar    eax,1
  400fdf:   8d 0c 30                lea    ecx,[rax+rsi*1]
  400fe2:   39 f9                   cmp    ecx,edi
  400fe4:   7e 0c                   jle    400ff2 <func4+0x24> (File Offset: 0xff2)
  400fe6:   8d 51 ff                lea    edx,[rcx-0x1]
  400fe9:   e8 e0 ff ff ff          call   400fce <func4> (File Offset: 0xfce)
  400fee:   01 c0                   add    eax,eax
  400ff0:   eb 15                   jmp    401007 <func4+0x39> (File Offset: 0x1007)
  400ff2:   b8 00 00 00 00          mov    eax,0x0
  400ff7:   39 f9                   cmp    ecx,edi
  400ff9:   7d 0c                   jge    401007 <func4+0x39> (File Offset: 0x1007)
  400ffb:   8d 71 01                lea    esi,[rcx+0x1]
  400ffe:   e8 cb ff ff ff          call   400fce <func4> (File Offset: 0xfce)
  401003:   8d 44 00 01             lea    eax,[rax+rax*1+0x1]
  401007:   48 83 c4 08             add    rsp,0x8
  40100b:   c3                      ret
```

后两个参数先叫 `x` 和 `y`, 试着分析一下它的 C 代码:

```c
int func4(int a, int x, int y){
    int eax = y;
    eax -= x;
    if(eax < 0)  // shr 0x1f 之后, 只有当 ecx 是负数时才能得到 1, 否则为 0. 然后加到 eax 上.
        ++eax;
    eax >>= 1;  // eax: (y - x) / 2 向零取整
    int ecx = eax + x;
    if(ecx <= a){
        eax = 0;
        if(ecx >= a)
            return eax;
        else{
            eax = func4(a, ecx + 1, y);
            eax = eax*2 + 1;
            return eax;
        }
    }
    else{
        eax = func4(a, x, ecx - 1);
        eax *= 2;
        return eax;
    }
}
```

看上去 `x` 和 `y` 是类似边界的东西, 还是管它叫 `l`, `r` 比较好.

脑内优化一下可以得到:

```c
int func4(int a, int l, int r){
    int mid = l + (r - l) / 2;
    if(mid <= a){
        if(mid == a)
            return 0;
        else
            return func4(a, mid+1, r) * 2 + 1;
    }
    else
        return func4(a, l, mid-1) * 2;
}
```

看上去它在做的就是一个递归的二分查找, 返回值是二分的历史. 如果取左半区间就在历史低位添一个 `0`, 右半部分就添 `1`. 当中点命中目标时直接返回 `0`.

搞清了 `func4` 之后回去看看 `phase_4` 拿返回值干啥了.

看上去就普通地判断了一下要求 `func4` 的返回值是 `0`, 同时要求 `b` 也是 `0`.

想了想有两种思路, 一个是让它只能取左半区间, 显然让 `a` 是二分左端点也就是 `0` 即可. 另一种思路是, 向左半区间二分的过程中的每一个中点值也是合法的答案, 也就是 `7`, `3`, `1`.

所以合法的 key 可以是:

```plain
7 0
```

## Phase 5

先看入口:

```asm
0000000000401062 <phase_5> (File Offset: 0x1062):
  401062:   53                      push   rbx
  401063:   48 83 ec 20             sub    rsp,0x20
  401067:   48 89 fb                mov    rbx,rdi
  40106a:   64 48 8b 04 25 28 00    mov    rax,QWORD PTR fs:0x28
  401071:   00 00
  401073:   48 89 44 24 18          mov    QWORD PTR [rsp+0x18],rax
  401078:   31 c0                   xor    eax,eax
  40107a:   e8 9c 02 00 00          call   40131b <string_length> (File Offset: 0x131b)
  40107f:   83 f8 06                cmp    eax,0x6
  401082:   74 4e                   je     4010d2 <phase_5+0x70> (File Offset: 0x10d2)
  401084:   e8 b1 03 00 00          call   40143a <explode_bomb> (File Offset: 0x143a)
  401089:   eb 47                   jmp    4010d2 <phase_5+0x70> (File Offset: 0x10d2)
  40108b:   0f b6 0c 03             movzx  ecx,BYTE PTR [rbx+rax*1]
  40108f:   88 0c 24                mov    BYTE PTR [rsp],cl
  401092:   48 8b 14 24             mov    rdx,QWORD PTR [rsp]
  401096:   83 e2 0f                and    edx,0xf
  401099:   0f b6 92 b0 24 40 00    movzx  edx,BYTE PTR [rdx+0x4024b0]
  4010a0:   88 54 04 10             mov    BYTE PTR [rsp+rax*1+0x10],dl
  4010a4:   48 83 c0 01             add    rax,0x1
  4010a8:   48 83 f8 06             cmp    rax,0x6
  4010ac:   75 dd                   jne    40108b <phase_5+0x29> (File Offset: 0x108b)
  4010ae:   c6 44 24 16 00          mov    BYTE PTR [rsp+0x16],0x0
  4010b3:   be 5e 24 40 00          mov    esi,0x40245e
  4010b8:   48 8d 7c 24 10          lea    rdi,[rsp+0x10]
  4010bd:   e8 76 02 00 00          call   401338 <strings_not_equal> (File Offset: 0x1338)
  4010c2:   85 c0                   test   eax,eax
  4010c4:   74 13                   je     4010d9 <phase_5+0x77> (File Offset: 0x10d9)
  4010c6:   e8 6f 03 00 00          call   40143a <explode_bomb> (File Offset: 0x143a)
  4010cb:   0f 1f 44 00 00          nop    DWORD PTR [rax+rax*1+0x0]
  4010d0:   eb 07                   jmp    4010d9 <phase_5+0x77> (File Offset: 0x10d9)
  4010d2:   b8 00 00 00 00          mov    eax,0x0
  4010d7:   eb b2                   jmp    40108b <phase_5+0x29> (File Offset: 0x108b)
  4010d9:   48 8b 44 24 18          mov    rax,QWORD PTR [rsp+0x18]
  4010de:   64 48 33 04 25 28 00    xor    rax,QWORD PTR fs:0x28
  4010e5:   00 00
  4010e7:   74 05                   je     4010ee <phase_5+0x8c> (File Offset: 0x10ee)
  4010e9:   e8 42 fa ff ff          call   400b30 <__stack_chk_fail@plt> (File Offset: 0xb30)
  4010ee:   48 83 c4 20             add    rsp,0x20
  4010f2:   5b                      pop    rbx
  4010f3:   c3                      ret
```

前几行先放了个 stack protector 在 `QWORD PTR [rsp+0x18]`, 然后判断了一下 key 的长度要求为 6.

跳出来把 `eax` 赋成 `0` 了之后又跳回去到一个长得像个循环的地方, 推测 `40108b` 到 `4010ac` 这段是循环体.

观察循环中的操作, 对每个 key 中的字符都取最低 4 位, 然后在基址 `0x4024b0` 处查表并移动到 `rsp+0x10` 处. 果断看 `0x24b0` 有啥:

```plain
000024b0: 6d61 6475 6965 7273 6e66 6f74 7662 796c  maduiersnfotvbyl
```

果然是个表. 再看跳出循环后, 以 `rsp+0x10` 和 `0x40245e` 为参数调用 `strings_not_equal`, 看来目标就在 `0x245e`.

```plain
00002450: 7365 6372 6574 2073 7461 6765 2100 666c  secret stage!.fl
00002460: 7965 7273 0000 0000 0000 0000 0000 0000  yers............
```

目标字符串是 `flyers`, 构造一个低 4 位是 `9FE567` 的字符串即可.

懒得查 ASCII 表了, 直接在 `xxd` 的这段地址附近找低位能对上的字符了(xs

```plain
79  y
6f  o
6e  n
75  u
76  v
77  w
```

所以一个合法的 key 就是:

```plain
yonuvw
```

## Phase 6

Phase 6 的逆向有点长, 一点点看

```asm
00000000004010f4 <phase_6> (File Offset: 0x10f4):
  4010f4:   41 56                   push   r14
  4010f6:   41 55                   push   r13
  4010f8:   41 54                   push   r12
  4010fa:   55                      push   rbp
  4010fb:   53                      push   rbx
  4010fc:   48 83 ec 50             sub    rsp,0x50
  401100:   49 89 e5                mov    r13,rsp
  401103:   48 89 e6                mov    rsi,rsp
  401106:   e8 51 03 00 00          call   40145c <read_six_numbers> (File Offset: 0x145c)
  40110b:   49 89 e6                mov    r14,rsp
  40110e:   41 bc 00 00 00 00       mov    r12d,0x0
  401114:   4c 89 ed                mov    rbp,r13
  401117:   41 8b 45 00             mov    eax,DWORD PTR [r13+0x0]
  40111b:   83 e8 01                sub    eax,0x1
  40111e:   83 f8 05                cmp    eax,0x5
  401121:   76 05                   jbe    401128 <phase_6+0x34> (File Offset: 0x1128)
  401123:   e8 12 03 00 00          call   40143a <explode_bomb> (File Offset: 0x143a)
```

entry sequence 有亿点长, ~~不祥的预感~~

寄存器保存之后又拉了一个 `0x50` 长度的栈帧 buffer

以 `rsp` 为第二个参数调用 `read_six_numbers`, 根据 Phase 2 的分析可以知道它会从输入中读取 6 个整数放在以 `rsp` 为基址的 `int` 数组. 不妨设这个 buffer 为 `buf[]`.

然后来到第一个条件跳转, 将 `r13` 指向的 `int` 值 (此时也是 `rsp` 指向的值 `buf[0]`) 减去 `1` 并与 `5` 作比较, 若大于则引爆.

此时, `rbp = r13 = r14 = rsp`, `r12d = 0`.

继续看下一段

```asm
  401128:   41 83 c4 01             add    r12d,0x1
  40112c:   41 83 fc 06             cmp    r12d,0x6
  401130:   74 21                   je     401153 <phase_6+0x5f> (File Offset: 0x1153)
  401132:   44 89 e3                mov    ebx,r12d
  401135:   48 63 c3                movsxd rax,ebx
  401138:   8b 04 84                mov    eax,DWORD PTR [rsp+rax*4]
  40113b:   39 45 00                cmp    DWORD PTR [rbp+0x0],eax
  40113e:   75 05                   jne    401145 <phase_6+0x51> (File Offset: 0x1145)
  401140:   e8 f5 02 00 00          call   40143a <explode_bomb> (File Offset: 0x143a)
  401145:   83 c3 01                add    ebx,0x1
  401148:   83 fb 05                cmp    ebx,0x5
  40114b:   7e e8                   jle    401135 <phase_6+0x41> (File Offset: 0x1135)
  40114d:   49 83 c5 04             add    r13,0x4
  401151:   eb c1                   jmp    401114 <phase_6+0x20> (File Offset: 0x1114)
  401153:   48 8d 74 24 18          lea    rsi,[rsp+0x18]
  401158:   4c 89 f0                mov    rax,r14
  40115b:   b9 07 00 00 00          mov    ecx,0x7
  401160:   89 ca                   mov    edx,ecx
  401162:   2b 10                   sub    edx,DWORD PTR [rax]
  401164:   89 10                   mov    DWORD PTR [rax],edx
  401166:   48 83 c0 04             add    rax,0x4
  40116a:   48 39 f0                cmp    rax,rsi
  40116d:   75 f1                   jne    401160 <phase_6+0x6c> (File Offset: 0x1160)
```

由上文知 `r12d` 被初始化为 `0`, 可知执行到 `40112c` 的比较语句时 `r12d` 为 `1`, `401130` 永远不会跳转.

接下来的两句可以推断 `ebx = 1`, `rax = 1`.

`401138` 将 `buf[1]` 加载并在接下来与 `buf[0]` 做比较, 判断要求二者不相等.

`ebx` 自增 `1`, 此时 `ebx = 2`, `40114b` 必定跳转, `401135` 到 `40114b` 组成循环<span class="covered">(鈤 怎么打环了)</span>, `ebx` 遍历 `[1,5]`, 即要求后面的字符不能与第一个相等.

循环结束后 `r13` 自增 4, 跳回 `401114` <span class="covered">草 原来是循环</span>. 可知 `r13` 指向 `buf` 的下一个 `int` 位置. 检查这个位置的值大小之后 `r12d` 自增, 可以推知 `r12d` 一直保存着 `r13` 指向的地址在 `buf` 中的下标 `+1` 的值. 推知跳出到 `401153` 之前的代码判断了读入的六个数互不相等且不大于 `6`.

接下来, 由上文知 `r14 = rsp`, `rax` 中保存着一个指向 `buf` 中的一个值的指针. `rsi` 则保存着 `buf[6]` 的地址. 接下来令 `[rax] = 7 - [rax]`, 同时将 `rax` 增加 4 并与 `rsi` 比较, 推断又是一个遍历六个数字的循环, 并将 `buf[i]` 设为 `7 - buf[i]`.

```asm
  40116f:   be 00 00 00 00          mov    esi,0x0
  401174:   eb 21                   jmp    401197 <phase_6+0xa3> (File Offset: 0x1197)
```

将 `esi` 置为 `0` 之后突然跳转, 找到它的目标:

```asm
  401176:   48 8b 52 08             mov    rdx,QWORD PTR [rdx+0x8]
  40117a:   83 c0 01                add    eax,0x1
  40117d:   39 c8                   cmp    eax,ecx
  40117f:   75 f5                   jne    401176 <phase_6+0x82> (File Offset: 0x1176)
  401181:   eb 05                   jmp    401188 <phase_6+0x94> (File Offset: 0x1188)
  401183:   ba d0 32 60 00          mov    edx,0x6032d0
  401188:   48 89 54 74 20          mov    QWORD PTR [rsp+rsi*2+0x20],rdx
  40118d:   48 83 c6 04             add    rsi,0x4
  401191:   48 83 fe 18             cmp    rsi,0x18
  401195:   74 14                   je     4011ab <phase_6+0xb7> (File Offset: 0x11ab)
  401197:   8b 0c 34                mov    ecx,DWORD PTR [rsp+rsi*1]
  40119a:   83 f9 01                cmp    ecx,0x1
  40119d:   7e e4                   jle    401183 <phase_6+0x8f> (File Offset: 0x1183)
  40119f:   b8 01 00 00 00          mov    eax,0x1
  4011a4:   ba d0 32 60 00          mov    edx,0x6032d0
  4011a9:   eb cb                   jmp    401176 <phase_6+0x82> (File Offset: 0x1176)
```

不难发现这一段代码除了 `401195` 跳出了之外是跳转封闭的, 推测是某种循环且结束条件是 `rsi = 0x18`. 附近可以看到 `rsi` 自增 `4` 的命令, 推测是循环状态更新. 结合跳入前 `esi` 初始化为 `0`, 推测这个循环会执行 6 次. 根据步长和范围基本可以确定 `DWORD PTR [rsp+rsi*1]` 就是遍历中的 `buf[]` 位置的值. 如果当前 `buf[i]` 不大于 1 则直接将 `0x6032d0` 加载入 `rsp+0x20` 为基址的 `QWORD` buffer 地址. 若大于 1 则一直循环执行 `rdx = QWORD PTR [rdx+0x8]` (草这怎么回事)

完了 感觉关键在 `0x6032d0`. 查表发现是 `.data` 段且对应文件偏移 `0x32d0`:

```plain
000032d0: 4c01 0000 0100 0000 e032 6000 0000 0000  L........2`.....
000032e0: a800 0000 0200 0000 f032 6000 0000 0000  .........2`.....
000032f0: 9c03 0000 0300 0000 0033 6000 0000 0000  .........3`.....
00003300: b302 0000 0400 0000 1033 6000 0000 0000  .........3`.....
00003310: dd01 0000 0500 0000 2033 6000 0000 0000  ........ 3`.....
00003320: bb01 0000 0600 0000 0000 0000 0000 0000  ................
```

看上去每次 `rdx` 都会指向一段数据, 而 `rdx+0x8` 指向下一个地址. 那么这样的话根据 `401188` 处的保存命令可以知道会将循环 `buf[i]` 次后的地址加载到 `[rsp+0x20]` 的 `QWORD` buffer. 根据上面的数据可以知道大概是指向一个 8 字节的值(且长得像两个 4 字节整数拼一起)

我们可以按 16 字节为一组, 先管它叫一行. 相当于是 `QWORD` buffer 中都是上述某一行数据的地址.

剩下的部分在exit sequence之前的命令如下:

```asm
  4011ab:   48 8b 5c 24 20          mov    rbx,QWORD PTR [rsp+0x20]
  4011b0:   48 8d 44 24 28          lea    rax,[rsp+0x28]
  4011b5:   48 8d 74 24 50          lea    rsi,[rsp+0x50]
  4011ba:   48 89 d9                mov    rcx,rbx
  4011bd:   48 8b 10                mov    rdx,QWORD PTR [rax]
  4011c0:   48 89 51 08             mov    QWORD PTR [rcx+0x8],rdx
  4011c4:   48 83 c0 08             add    rax,0x8
  4011c8:   48 39 f0                cmp    rax,rsi
  4011cb:   74 05                   je     4011d2 <phase_6+0xde> (File Offset: 0x11d2)
  4011cd:   48 89 d1                mov    rcx,rdx
  4011d0:   eb eb                   jmp    4011bd <phase_6+0xc9> (File Offset: 0x11bd)
  4011d2:   48 c7 42 08 00 00 00    mov    QWORD PTR [rdx+0x8],0x0
  4011d9:   00
  4011da:   bd 05 00 00 00          mov    ebp,0x5
  4011df:   48 8b 43 08             mov    rax,QWORD PTR [rbx+0x8]
  4011e3:   8b 00                   mov    eax,DWORD PTR [rax]
  4011e5:   39 03                   cmp    DWORD PTR [rbx],eax
  4011e7:   7d 05                   jge    4011ee <phase_6+0xfa> (File Offset: 0x11ee)
  4011e9:   e8 4c 02 00 00          call   40143a <explode_bomb> (File Offset: 0x143a)
  4011ee:   48 8b 5b 08             mov    rbx,QWORD PTR [rbx+0x8]
  4011f2:   83 ed 01                sub    ebp,0x1
  4011f5:   75 e8                   jne    4011df <phase_6+0xeb> (File Offset: 0x11df)
```

`rbx` 现在是奇怪的 `QWORD` buffer 的第一个值, 先管他叫 `qbuf[0]`. `rax` 是 `&qbuf[1]`, `rsi` 是 `&qbuf[6]`.

`rcx = rbx = qbuf[0]`. `rdx = qbuf[1]`. `*(qbuf[0]+0x8) = rdx = qbuf[1]`, 相当于把 `qbuf[0]` 指向的行中的数据指向的地址改成了 `qbuf[1]` 中保存的地址.

然后将 `rcx` 更改为 `rax` 指向的值, `rax` 自增到下一个 `qbuf` 位置进行循环, 相当于每个循环的操作对象从 `qbuf[0]`/`qbuf[1]` 变成 `qbuf[i]`/`qbuf[i+1]`.

对 `.data` 中的数据进行了一番修改之后进入验证过程. `qbuf[5]` 指向的行的地址段首先被清零, `qbuf[0]` 指向的行的地址被加载到 `rax`, 然后加载 `rax` 指向的值. 验证要求 `qbuf[0]` 指向的行的值大于等于这一行的地址段指向的行的值.

观察发现第二行的值最小, ~~当然是全都写 2 了~~ 然而所有的值必须不相等.

稍微撕烤一下可以意识到只要 `qbuf[]` 中指向的行的地址对应的值依次变小就可以了. 排序可以知道正确的序列是 `3 4 5 6 1 2`.

注意中间有反相的过程, 所以 key 应该是:

```plain
4 3 2 1 6 5
```

## One more thing...

逆向的时候看到 `.rodata` 段里有些奇怪的东西:

```plain
00002430: 7465 722e 0000 0000 576f 7721 2059 6f75  ter.....Wow! You
00002440: 2776 6520 6465 6675 7365 6420 7468 6520  've defused the
00002450: 7365 6372 6574 2073 7461 6765 2100 666c  secret stage!.fl
00002460: 7965 7273 0000 0000 0000 0000 0000 0000  yers............
```

```plain
000024f0: 646f 2079 6f75 3f00 4375 7273 6573 2c20  do you?.Curses,
00002500: 796f 7527 7665 2066 6f75 6e64 2074 6865  you've found the
00002510: 2073 6563 7265 7420 7068 6173 6521 0000   secret phase!..
00002520: 4275 7420 6669 6e64 696e 6720 6974 2061  But finding it a
00002530: 6e64 2073 6f6c 7669 6e67 2069 7420 6172  nd solving it ar
00002540: 6520 7175 6974 6520 6469 6666 6572 656e  e quite differen
00002550: 742e 2e2e 0000 0000 436f 6e67 7261 7475  t.......Congratu
```

看来还有东西在里面...

`0x2438` 对应的 VMA 是 `0x402438`, 找一下哪里有这个的引用:

```asm
  401282:   bf 38 24 40 00          mov    edi,0x402438
  401287:   e8 84 f8 ff ff          call   400b10 <puts@plt> (File Offset: 0xb10)
```

而它所属的函数是:

```asm
0000000000401242 <secret_phase> (File Offset: 0x1242):
  401242:   53                      push   rbx
  401243:   e8 56 02 00 00          call   40149e <read_line> (File Offset: 0x149e)
  401248:   ba 0a 00 00 00          mov    edx,0xa
  40124d:   be 00 00 00 00          mov    esi,0x0
  401252:   48 89 c7                mov    rdi,rax
  401255:   e8 76 f9 ff ff          call   400bd0 <strtol@plt> (File Offset: 0xbd0)
  40125a:   48 89 c3                mov    rbx,rax
  40125d:   8d 40 ff                lea    eax,[rax-0x1]
  401260:   3d e8 03 00 00          cmp    eax,0x3e8
  401265:   76 05                   jbe    40126c <secret_phase+0x2a> (File Offset: 0x126c)
  401267:   e8 ce 01 00 00          call   40143a <explode_bomb> (File Offset: 0x143a)
  40126c:   89 de                   mov    esi,ebx
  40126e:   bf f0 30 60 00          mov    edi,0x6030f0
  401273:   e8 8c ff ff ff          call   401204 <fun7> (File Offset: 0x1204)
  401278:   83 f8 02                cmp    eax,0x2
  40127b:   74 05                   je     401282 <secret_phase+0x40> (File Offset: 0x1282)
  40127d:   e8 b8 01 00 00          call   40143a <explode_bomb> (File Offset: 0x143a)
  401282:   bf 38 24 40 00          mov    edi,0x402438
  401287:   e8 84 f8 ff ff          call   400b10 <puts@plt> (File Offset: 0xb10)
  40128c:   e8 33 03 00 00          call   4015c4 <phase_defused> (File Offset: 0x15c4)
  401291:   5b                      pop    rbx
  401292:   c3                      ret
```

追踪一下引用, 发现在 `phase_defused` 里

```asm
00000000004015c4 <phase_defused> (File Offset: 0x15c4):
  4015c4:   48 83 ec 78             sub    rsp,0x78
  4015c8:   64 48 8b 04 25 28 00    mov    rax,QWORD PTR fs:0x28
  4015cf:   00 00
  4015d1:   48 89 44 24 68          mov    QWORD PTR [rsp+0x68],rax
  4015d6:   31 c0                   xor    eax,eax
  4015d8:   83 3d 81 21 20 00 06    cmp    DWORD PTR [rip+0x202181],0x6        # 603760 <num_input_strings> (File Offset: 0x203760)
  4015df:   75 5e                   jne    40163f <phase_defused+0x7b> (File Offset: 0x163f)
  4015e1:   4c 8d 44 24 10          lea    r8,[rsp+0x10]
  4015e6:   48 8d 4c 24 0c          lea    rcx,[rsp+0xc]
  4015eb:   48 8d 54 24 08          lea    rdx,[rsp+0x8]
  4015f0:   be 19 26 40 00          mov    esi,0x402619
  4015f5:   bf 70 38 60 00          mov    edi,0x603870
  4015fa:   e8 f1 f5 ff ff          call   400bf0 <__isoc99_sscanf@plt> (File Offset: 0xbf0)
  4015ff:   83 f8 03                cmp    eax,0x3
  401602:   75 31                   jne    401635 <phase_defused+0x71> (File Offset: 0x1635)
  401604:   be 22 26 40 00          mov    esi,0x402622
  401609:   48 8d 7c 24 10          lea    rdi,[rsp+0x10]
  40160e:   e8 25 fd ff ff          call   401338 <strings_not_equal> (File Offset: 0x1338)
  401613:   85 c0                   test   eax,eax
  401615:   75 1e                   jne    401635 <phase_defused+0x71> (File Offset: 0x1635)
  401617:   bf f8 24 40 00          mov    edi,0x4024f8
  40161c:   e8 ef f4 ff ff          call   400b10 <puts@plt> (File Offset: 0xb10)
  401621:   bf 20 25 40 00          mov    edi,0x402520
  401626:   e8 e5 f4 ff ff          call   400b10 <puts@plt> (File Offset: 0xb10)
  40162b:   b8 00 00 00 00          mov    eax,0x0
  401630:   e8 0d fc ff ff          call   401242 <secret_phase> (File Offset: 0x1242)
  401635:   bf 58 25 40 00          mov    edi,0x402558
  40163a:   e8 d1 f4 ff ff          call   400b10 <puts@plt> (File Offset: 0xb10)
  40163f:   48 8b 44 24 68          mov    rax,QWORD PTR [rsp+0x68]
  401644:   64 48 33 04 25 28 00    xor    rax,QWORD PTR fs:0x28
  40164b:   00 00
  40164d:   74 05                   je     401654 <phase_defused+0x90> (File Offset: 0x1654)
  40164f:   e8 dc f4 ff ff          call   400b30 <__stack_chk_fail@plt> (File Offset: 0xb30)
  401654:   48 83 c4 78             add    rsp,0x78
  401658:   c3                      ret
  401659:   90                      nop
  40165a:   90                      nop
```

读一下代码, 中间 `4015e1` 到 `40163a` 一大段代码都是在 `num_input_strings = 6` 的时候才会执行. 然后丢了一些地址在参数寄存器调了 `sscanf`, 根据参数顺序知道 `0x402619` 是 format, `0x603870` 是buffer. `0x402619` 在 `.rodata` 段可以直接从文件地址 `0x2619` 读:

```plain
00002610: 746f 6f20 6c6f 6e67 0025 6420 2564 2025  too long.%d %d %
00002620: 7300 4472 4576 696c 0067 7265 6174 7768  s.DrEvil.greatwh
```

格式串是 `%d %d %s` 并且后续验证了是否能读入三个信息. 而 `0x603870` 在 `.bss` 段, 大概是全局静态 buffer. 查一下符号表:

```plain
    65: 00000000006030e0     0 NOTYPE  WEAK   DEFAULT   24 data_start
    66: 0000000000603780  1600 OBJECT  GLOBAL DEFAULT   25 input_strings
    67: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND strcpy@@GLIBC_2.2.5
```

看上去属于一个巨大全局静态 buffer, 根据名字推测大概是保存着所有的输入字符串, `0x603870` 在 buffer 中的下标应该是 `0xe0`.

既然前 6 个 phase 都解完了不如直接上 `gdb` 动态看看对应的是哪段输入, 丢到 `gdb` 里在调用 `sscanf` 的地方也就是 `*0x4015fa` 下个断点直接翻 `0x603870` 附近的内存:

```plain
(gdb) x/64xc 0x603850
0x603850 <input_strings+208>:   0 '\000'        0 '\000'        0 '\000'        0 '\000'   0 '\000' 0 '\000'        0 '\000'        0 '\000'
0x603858 <input_strings+216>:   0 '\000'        0 '\000'        0 '\000'        0 '\000'   0 '\000' 0 '\000'        0 '\000'        0 '\000'
0x603860 <input_strings+224>:   0 '\000'        0 '\000'        0 '\000'        0 '\000'   0 '\000' 0 '\000'        0 '\000'        0 '\000'
0x603868 <input_strings+232>:   0 '\000'        0 '\000'        0 '\000'        0 '\000'   0 '\000' 0 '\000'        0 '\000'        0 '\000'
0x603870 <input_strings+240>:   55 '7'  32 ' '  48 '0'  0 '\000'        0 '\000'        0 '\000'    0 '\000'        0 '\000'
0x603878 <input_strings+248>:   0 '\000'        0 '\000'        0 '\000'        0 '\000'   0 '\000' 0 '\000'        0 '\000'        0 '\000'
0x603880 <input_strings+256>:   0 '\000'        0 '\000'        0 '\000'        0 '\000'   0 '\000' 0 '\000'        0 '\000'        0 '\000'
0x603888 <input_strings+264>:   0 '\000'        0 '\000'        0 '\000'        0 '\000'   0 '\000' 0 '\000'        0 '\000'        0 '\000'
```

`'7', ' ', '0', '\0'`, 显然是 phase 3 的 key. 也就是说大概要在 phase 3 后面加点料(

继续看 `phase_defused` 的逆向, 根据 `r8` 的值知道这段字符串保存在 `rsp+0x10`. 判断是否成功读入之后又把 `rsp+0x10` 和 `0x402622` 一起传给了 `string_not_equal`. 这个静态地址指向的值是 `DrEvil`, 所以我们把 phase 3 的 key 改成:

```plain
7 0 DrEvil
```

再用 `gdb` 跑一下, 提示 `Curses, you've found the secret phase!` 并阻塞等待输入. 大概是成功进 `secret_phase` 了.

然后看 `secret_phase` 的逆向, 读入一行之后直接调用 `strtol`. 查标准库 prototype 可以知道参数含义, 推得语义是将读入的字符串转换为一个整数, 可知 secret phase 输入是一个整数. 先管它叫 `x` 好了.

接下来的判定可以发现要求 `x <= 0x3e8`, 然后将 `0x6030f0` 和 `x` 作参数调用 `fun7`. 这个地址在 `.data` 段, 看一下符号信息:

```plain
   109: 0000000000400fce    62 FUNC    GLOBAL DEFAULT   13 func4
   110: 00000000006030f0    24 OBJECT  GLOBAL DEFAULT   24 n1
   111: 000000000040131b    29 FUNC    GLOBAL DEFAULT   13 string_length
```

一个大小为 24 字节的东西, 看一下对应的数据:

```plain
000030f0: 2400 0000 0000 0000 1031 6000 0000 0000  $........1`.....
00003100: 3031 6000 0000 0000 0000 0000 0000 0000  01`.............
```

`0x24`, `0x603110`, `0x603130`. 感觉又是俩地址, 找下符号:

```plain
   151: 0000000000603110    24 OBJECT  GLOBAL DEFAULT   24 n21
   107: 0000000000603130    24 OBJECT  GLOBAL DEFAULT   24 n22
```

又是俩 24 字节的东西, 继续找数据:

```plain
00003110: 0800 0000 0000 0000 9031 6000 0000 0000  .........1`.....
00003120: 5031 6000 0000 0000 0000 0000 0000 0000  P1`.............
00003130: 3200 0000 0000 0000 7031 6000 0000 0000  2.......p1`.....
00003140: b031 6000 0000 0000 0000 0000 0000 0000  .1`.............
```

`0x8`, `0x603190`, `0x603150` 和 `0x32`, `0x603170`, `0x6031b0`

啊↑西↓, 又递归出俩地址, 你这tm是个树吧...

```plain
    61: 0000000000603190    24 OBJECT  GLOBAL DEFAULT   24 n31
   116: 0000000000603150    24 OBJECT  GLOBAL DEFAULT   24 n32
    68: 0000000000603170    24 OBJECT  GLOBAL DEFAULT   24 n33
   115: 00000000006031b0    24 OBJECT  GLOBAL DEFAULT   24 n34
```

```plain
00003150: 1600 0000 0000 0000 7032 6000 0000 0000  ........p2`.....
00003160: 3032 6000 0000 0000 0000 0000 0000 0000  02`.............
00003170: 2d00 0000 0000 0000 d031 6000 0000 0000  -........1`.....
00003180: 9032 6000 0000 0000 0000 0000 0000 0000  .2`.............
00003190: 0600 0000 0000 0000 f031 6000 0000 0000  .........1`.....
000031a0: 5032 6000 0000 0000 0000 0000 0000 0000  P2`.............
000031b0: 6b00 0000 0000 0000 1032 6000 0000 0000  k........2`.....
000031c0: b032 6000 0000 0000 0000 0000 0000 0000  .2`.............
```

彳亍口巴, 又炸出一堆地址...

不多 bb 了直接查符号找数据了

```plain
    73: 0000000000603230    24 OBJECT  GLOBAL DEFAULT   24 n44
    74: 0000000000603290    24 OBJECT  GLOBAL DEFAULT   24 n46
    75: 0000000000603250    24 OBJECT  GLOBAL DEFAULT   24 n42
    76: 00000000006032b0    24 OBJECT  GLOBAL DEFAULT   24 n48
   126: 0000000000603210    24 OBJECT  GLOBAL DEFAULT   24 n47
   127: 0000000000603270    24 OBJECT  GLOBAL DEFAULT   24 n43
   128: 00000000006031f0    24 OBJECT  GLOBAL DEFAULT   24 n41
   130: 00000000006031d0    24 OBJECT  GLOBAL DEFAULT   24 n45
```

一段连续的空间的样子...

```plain
000031d0: 2800 0000 0000 0000 0000 0000 0000 0000  (...............
000031e0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000031f0: 0100 0000 0000 0000 0000 0000 0000 0000  ................
00003200: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00003210: 6300 0000 0000 0000 0000 0000 0000 0000  c...............
00003220: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00003230: 2300 0000 0000 0000 0000 0000 0000 0000  #...............
00003240: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00003250: 0700 0000 0000 0000 0000 0000 0000 0000  ................
00003260: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00003270: 1400 0000 0000 0000 0000 0000 0000 0000  ................
00003280: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00003290: 2f00 0000 0000 0000 0000 0000 0000 0000  /...............
000032a0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000032b0: e903 0000 0000 0000 0000 0000 0000 0000  ................
000032c0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

大概这一层应该是叶子了...以前是地址的地方现在是空指针...

感觉大概可以推测出这个结构体的定义:

```c
struct Node{
    int val;
    Node* lch;
    Node* rch;
};
```

找一下 `fun7` 的逆向:

```asm
0000000000401204 <fun7> (File Offset: 0x1204):
  401204:   48 83 ec 08             sub    rsp,0x8
  401208:   48 85 ff                test   rdi,rdi
  40120b:   74 2b                   je     401238 <fun7+0x34> (File Offset: 0x1238)
  40120d:   8b 17                   mov    edx,DWORD PTR [rdi]
  40120f:   39 f2                   cmp    edx,esi
  401211:   7e 0d                   jle    401220 <fun7+0x1c> (File Offset: 0x1220)
  401213:   48 8b 7f 08             mov    rdi,QWORD PTR [rdi+0x8]
  401217:   e8 e8 ff ff ff          call   401204 <fun7> (File Offset: 0x1204)
  40121c:   01 c0                   add    eax,eax
  40121e:   eb 1d                   jmp    40123d <fun7+0x39> (File Offset: 0x123d)
  401220:   b8 00 00 00 00          mov    eax,0x0
  401225:   39 f2                   cmp    edx,esi
  401227:   74 14                   je     40123d <fun7+0x39> (File Offset: 0x123d)
  401229:   48 8b 7f 10             mov    rdi,QWORD PTR [rdi+0x10]
  40122d:   e8 d2 ff ff ff          call   401204 <fun7> (File Offset: 0x1204)
  401232:   8d 44 00 01             lea    eax,[rax+rax*1+0x1]
  401236:   eb 05                   jmp    40123d <fun7+0x39> (File Offset: 0x123d)
  401238:   b8 ff ff ff ff          mov    eax,0xffffffff
  40123d:   48 83 c4 08             add    rsp,0x8
  401241:   c3                      ret
```

看上去有递归, 尝试改写成 C 代码:

```c
int fun7(Node* ptr, int x){
    if(ptr == 0)
        return 0xffffffff;
    else{
        int edx = ptr->val;
        if(edx <= x){
            if(edx == x)
                return 0;
            else
                return fun7(ptr->rch, x) * 2 + 1;
        }
        else
            return fun7(ptr->lch, x) * 2;
    }
}
```

看上去是个普通的 BST 搜索并记录路径.

回到 `secret_phase` 可以知道这个 phase 要求 `fun7` 返回值为 `2`, 需要给定 `x` 让它得到正确的搜索路径. 将硬编码的搜索树画出来可以得到:

{{< mermaid >}}
graph TB;
0x24 --> 0x08
0x24 --> 0x32
0x08 --> 0x06
0x08 --> 0x16
0x32 --> 0x2d
0x32 --> 0x6b
0x06 --> 0x01
0x06 --> 0x07
0x16 --> 0x14
0x16 --> 0x23
0x2d --> 0x28
0x2d --> 0x2f
0x6b --> 0x63
0x6b --> 0x3e9
{{< /mermaid >}}

如果要让返回值为 `2` 的话, 可以是 `0x16` 或者 `0x14`. 也就是十进制的 22 或 20.

于是最终答案就是:

```plain
❯ cat bomb.key
Border relations with Canada have never been better.
1 2 4 8 16 32
3 256
7 0 DrEvil
yonuvw
4 3 2 1 6 5
20
❯ ./bomb bomb.key
Welcome to my fiendish little bomb. You have 6 phases with
which to blow yourself up. Have a nice day!
Phase 1 defused. How about the next one?
That's number 2.  Keep going!
Halfway there!
So you got that one.  Try this one.
Good work!  On to the next...
Curses, you've found the secret phase!
But finding it and solving it are quite different...
Wow! You've defused the secret stage!
Congratulations! You've defused the bomb!
```

<span class="covered">感觉好像没有想像的那么难</span>

~~P.S.: 按 Ctrl-C 还可以体验 Dr. Evil 的特制 signal handler(~~

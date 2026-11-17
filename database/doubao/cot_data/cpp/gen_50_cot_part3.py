import json

entries = []

def add(instr, output):
    entries.append({"instruction": instr, "input": "", "output": output})

# 21. 责任链模式
add("实现责任链设计模式，创建一个请求处理链，每个处理器决定是否处理请求或传递给下一个处理器，实现不同级别的日志处理器（DEBUG、INFO、ERROR），类似日志框架的过滤机制。",
"""### 需求分析
责任链模式：
1. 多个处理器组成链
2. 请求沿链传递直到被处理
3. 每个处理器决定处理或传递
4. 实现多级日志处理
5. 可以动态添加/移除处理器

### 设计思路
1. Handler抽象类，持有next指针
2. setNext设置下一个处理器
3. handleRequest模板方法：自己处理或传给next
4. 具体处理器：DebugHandler, InfoHandler, ErrorHandler
5. 客户端组装链并发起请求

### 关键问题
- 链的构建：客户端负责组装链顺序
- 请求不一定被处理：链末端可以有默认处理器或丢弃
- vs装饰器：装饰器是层层包装添加行为，责任链是传递请求
- 性能：链太长会有遍历开销

### 代码实现
```cpp
#include <iostream>
#include <string>
#include <memory>

enum class LogLevel { DEBUG, INFO, WARNING, ERROR };

class LogHandler {
protected:
    std::shared_ptr<LogHandler> next_;
    LogLevel level_;
public:
    LogHandler(LogLevel level) : level_(level) {}
    virtual ~LogHandler() = default;

    void setNext(std::shared_ptr<LogHandler> next) {
        next_ = std::move(next);
    }

    void log(LogLevel level, const std::string& msg) {
        if (level >= level_) {
            write(msg);
        }
        if (next_) {
            next_->log(level, msg);
        }
    }

protected:
    virtual void write(const std::string& msg) = 0;
};

class ConsoleHandler : public LogHandler {
public:
    ConsoleHandler(LogLevel level) : LogHandler(level) {}
protected:
    void write(const std::string& msg) override {
        std::cout << "[Console] " << msg << std::endl;
    }
};

class FileHandler : public LogHandler {
    std::string filename_;
public:
    FileHandler(LogLevel level, std::string file) : LogHandler(level), filename_(std::move(file)) {}
protected:
    void write(const std::string& msg) override {
        std::cout << "[File:" << filename_ << "] " << msg << std::endl;
    }
};

class ErrorHandler : public LogHandler {
public:
    ErrorHandler(LogLevel level) : LogHandler(level) {}
protected:
    void write(const std::string& msg) override {
        std::cerr << "[ERROR] " << msg << std::endl;
    }
};

int main() {
    auto console = std::make_shared<ConsoleHandler>(LogLevel::DEBUG);
    auto file = std::make_shared<FileHandler>(LogLevel::INFO, "app.log");
    auto error = std::make_shared<ErrorHandler>(LogLevel::ERROR);

    console->setNext(file);
    file->setNext(error);

    std::cout << "=== Logging DEBUG message ===" << std::endl;
    console->log(LogLevel::DEBUG, "This is a debug message");

    std::cout << "\\n=== Logging ERROR message ===" << std::endl;
    console->log(LogLevel::ERROR, "Critical error occurred!");

    return 0;
}
```""")

# 22. 目录遍历
add("实现目录遍历功能，在Windows系统下递归遍历指定目录下的所有文件和子目录，统计每种文件类型的数量，计算总文件大小，输出目录树结构。",
"""### 需求分析
目录遍历：
1. 递归遍历目录和子目录
2. 列出文件和文件夹
3. 统计文件类型（按扩展名）
4. 计算总大小
5. 输出树形结构
6. Windows平台使用FindFirstFile/FindNextFile

### 设计思路
1. 使用WIN32_FIND_DATAA和FindFirstFile/FindNextFile
2. 递归函数遍历子目录
3. 用map统计扩展名计数和大小
4. 传递缩进字符串表示层级
5. 跳过"."和".."目录
6. 正确关闭查找句柄FindClose

### 关键问题
- 路径拼接：Windows用反斜杠\
- 符号链接/快捷方式：可能导致循环
- 权限：某些目录可能无法访问
- Unicode：本示例用ANSI版本，实际应用考虑宽字符

### 代码实现
```cpp
#include <windows.h>
#include <iostream>
#include <string>
#include <map>
#include <iomanip>

struct FileStats {
    std::map<std::string, int> typeCount;
    std::map<std::string, unsigned long long> typeSize;
    unsigned long long totalSize = 0;
    int totalFiles = 0;
    int totalDirs = 0;
};

void traverse(const std::string& path, const std::string& indent, FileStats& stats) {
    std::string searchPath = path + "\\*";
    WIN32_FIND_DATAA findData;
    HANDLE hFind = FindFirstFileA(searchPath.c_str(), &findData);

    if (hFind == INVALID_HANDLE_VALUE) return;

    do {
        std::string name = findData.cFileName;
        if (name == "." || name == "..") continue;

        std::string fullPath = path + "\\" + name;
        bool isDir = (findData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) != 0;

        std::cout << indent << (isDir ? "[DIR]  " : "[FILE] ") << name;

        if (isDir) {
            stats.totalDirs++;
            std::cout << "\\";
            std::cout << std::endl;
            traverse(fullPath, indent + "  ", stats);
        } else {
            stats.totalFiles++;
            ULARGE_INTEGER size;
            size.LowPart = findData.nFileSizeLow;
            size.HighPart = findData.nFileSizeHigh;
            unsigned long long fileSize = size.QuadPart;
            stats.totalSize += fileSize;
            std::cout << " (" << fileSize << " bytes)";

            std::string ext = "no_extension";
            size_t dot = name.find_last_of('.');
            if (dot != std::string::npos && dot > 0) {
                ext = name.substr(dot);
            }
            stats.typeCount[ext]++;
            stats.typeSize[ext] += fileSize;
            std::cout << std::endl;
        }
    } while (FindNextFileA(hFind, &findData));

    FindClose(hFind);
}

int main() {
    FileStats stats;
    std::string startPath = ".";
    std::cout << "Directory tree of " << startPath << ":" << std::endl;
    std::cout << startPath << "\\" << std::endl;
    traverse(startPath, "  ", stats);

    std::cout << "\n=== Statistics ===" << std::endl;
    std::cout << "Total directories: " << stats.totalDirs << std::endl;
    std::cout << "Total files: " << stats.totalFiles << std::endl;
    std::cout << "Total size: " << stats.totalSize << " bytes ("
              << std::fixed << std::setprecision(2)
              << (stats.totalSize / 1024.0 / 1024.0) << " MB)" << std::endl;

    std::cout << "\nFile types:" << std::endl;
    for (const auto& [ext, count] : stats.typeCount) {
        std::cout << "  " << std::left << std::setw(12) << ext
                  << " count: " << std::setw(5) << count
                  << " size: " << stats.typeSize[ext] << " bytes" << std::endl;
    }

    return 0;
}
```""")

# 23. 异步任务管道
add("使用std::future和std::promise实现异步任务管道，将多个处理步骤串联成流水线，每个步骤异步执行并将结果传递给下一步，实现一个简单的图像处理/文本处理管道。",
"""### 需求分析
异步任务管道：
1. 多个处理阶段串联
2. 每个阶段异步执行
3. 阶段之间通过future/promise传递数据
4. 数据流动：输入 -> stage1 -> stage2 -> ... -> 输出
5. 文本处理示例：读取->分词->过滤->统计

### 设计思路
1. 每个stage函数接收前一个future，返回新future
2. 使用std::async启动异步任务
3. 在lambda中get前一个future的结果，处理后set_value
4. 或者使用then连续性（C++20有std::future::then，本示例手动实现）
5. 管道末尾get最终结果

### 关键问题
- 异常处理：一个阶段抛异常需要沿链传播
- 阻塞：get会阻塞等待，确保在需要结果时才调用
- 启动策略：std::launch::async vs deferred
- 链式调用：可以封装operator|实现函数式管道风格

### 代码实现
```cpp
#include <iostream>
#include <future>
#include <string>
#include <vector>
#include <sstream>
#include <algorithm>
#include <cctype>

std::vector<std::string> split(const std::string& s) {
    std::vector<std::string> tokens;
    std::istringstream iss(s);
    std::string token;
    while (iss >> token) {
        tokens.push_back(token);
    }
    return tokens;
}

std::vector<std::string> filterShortWords(const std::vector<std::string>& words) {
    std::vector<std::string> result;
    for (const auto& w : words) {
        if (w.size() >= 3) result.push_back(w);
    }
    return result;
}

std::vector<std::string> toLower(const std::vector<std::string>& words) {
    std::vector<std::string> result;
    for (auto w : words) {
        std::transform(w.begin(), w.end(), w.begin(), ::tolower);
        result.push_back(w);
    }
    return result;
}

template<typename Func>
auto then(std::future<std::string> inputFuture, Func&& func) {
    return std::async(std::launch::async, [prev = std::move(inputFuture), f = std::forward<Func>(func)]() mutable {
        std::string input = prev.get();
        return f(input);
    });
}

template<typename T, typename Func>
auto then(std::future<std::vector<T>> inputFuture, Func&& func) {
    return std::async(std::launch::async, [prev = std::move(inputFuture), f = std::forward<Func>(func)]() mutable {
        auto input = prev.get();
        return f(input);
    });
}

int main() {
    std::string text = "The quick brown fox jumps over the lazy dog. C++ is powerful!";
    std::cout << "Input text: " << text << std::endl;

    auto stage1 = std::async(std::launch::async, [&text] {
        std::cout << "[Stage 1] Splitting text into words..." << std::endl;
        return split(text);
    });

    auto stage2 = then(std::move(stage1), [](std::vector<std::string> words) {
        std::cout << "[Stage 2] Converting to lowercase..." << std::endl;
        return toLower(words);
    });

    auto stage3 = then(std::move(stage2), [](std::vector<std::string> words) {
        std::cout << "[Stage 3] Filtering short words..." << std::endl;
        return filterShortWords(words);
    });

    auto result = stage3.get();

    std::cout << "\\nFinal result: " << result.size() << " words" << std::endl;
    for (const auto& w : result) {
        std::cout << "  - " << w << std::endl;
    }

    return 0;
}
```""")

# 24. thread_local线程局部存储
add("演示C++ thread_local关键字的使用，为每个线程创建独立的变量副本，实现线程独立的随机数生成器和线程ID缓存，对比thread_local与局部变量、全局变量的区别。",
"""### 需求分析
thread_local存储：
1. 每个线程有独立副本
2. 线程启动时构造，线程结束时析构
3. 与static结合使用
4. 避免线程间数据竞争（因为不共享）
5. 对比全局/静态/局部变量

### 设计思路
1. thread_local变量声明演示
2. 每个线程生成自己的随机数序列（互不干扰）
3. 线程入口缓存自己的线程ID
4. RAII对象演示构造/析构时机
5. 多线程同时访问验证独立性

### 关键问题
- 初始化时机：C++11保证首次使用前初始化
- 性能：比真正的局部变量稍慢，但比加锁快
- DLL/共享库：动态库中的thread_local变量注意事项
- 析构顺序：线程结束时按逆序析构thread_local对象

### 代码实现
```cpp
#include <iostream>
#include <thread>
#include <random>
#include <vector>
#include <string>

thread_local std::mt19937 tl_generator{std::random_device{}()};
thread_local std::string tl_threadName;
thread_local int tl_callCount = 0;

void setThreadName(const std::string& name) {
    tl_threadName = name;
}

int generateRandom() {
    tl_callCount++;
    std::uniform_int_distribution<int> dist(1, 100);
    return dist(tl_generator);
}

void threadWork(const std::string& name) {
    setThreadName(name);
    std::cout << "[" << tl_threadName << "] started" << std::endl;
    for (int i = 0; i < 3; ++i) {
        int val = generateRandom();
        std::cout << "[" << tl_threadName << "] random #" << tl_callCount << ": " << val << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    std::cout << "[" << tl_threadName << "] total generateRandom() calls: " << tl_callCount << std::endl;
}

int main() {
    std::cout << "=== Main thread ===" << std::endl;
    setThreadName("Main");
    std::cout << "Main random: " << generateRandom() << std::endl;
    std::cout << "Main call count: " << tl_callCount << std::endl;

    std::cout << "\\n=== Spawning worker threads ===" << std::endl;
    std::vector<std::thread> threads;
    threads.emplace_back(threadWork, "Worker-1");
    threads.emplace_back(threadWork, "Worker-2");
    threads.emplace_back(threadWork, "Worker-3");
    for (auto& t : threads) t.join();

    std::cout << "\\n=== Back to main ===" << std::endl;
    std::cout << "Main call count unchanged: " << tl_callCount << std::endl;

    return 0;
}
```""")

# 25. TCP粘包处理
add("解决TCP粘包/拆包问题，实现自定义协议帧格式（消息头+消息体），消息头包含消息长度字段，发送端按帧发送，接收端根据长度字段正确分割消息，演示多线程客户端同时发送时的完整接收。",
"""### 需求分析
TCP粘包处理：
1. TCP是流协议，没有消息边界
2. 多次send可能被一次recv收到（粘包）
3. 一次send可能被多次recv拆分（拆包）
4. 需要应用层协议界定消息边界
5. 长度字段法：[4字节长度][消息体]

### 设计思路
1. 协议格式：固定4字节uint32_t长度 + 变长消息体
2. 发送：先发送长度（网络字节序），再发送消息
3. 接收：先完整读4字节获取长度，再循环读满指定字节
4. 使用recv_n辅助函数确保读满指定字节
5. 处理分包：缓冲区中残留数据留到下次处理

### 关键问题
- recv返回值：可能返回0（连接关闭）、SOCKET_ERROR、实际收到字节数
- 循环读取：一次recv可能不够，要循环直到读满
- 字节序：长度字段用htonl/ntohl转换为网络字节序
- 缓冲区管理：接收缓冲区需要保存未处理完的数据

### 代码实现
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <thread>
#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib, "ws2_32.lib")

const uint16_t PORT = 8888;

bool recvAll(SOCKET sock, char* buf, int len) {
    int total = 0;
    while (total < len) {
        int r = recv(sock, buf + total, len - total, 0);
        if (r <= 0) return false;
        total += r;
    }
    return true;
}

bool sendAll(SOCKET sock, const char* buf, int len) {
    int total = 0;
    while (total < len) {
        int s = send(sock, buf + total, len - total, 0);
        if (s <= 0) return false;
        total += s;
    }
    return true;
}

bool sendMessage(SOCKET sock, const std::string& msg) {
    uint32_t len = htonl(msg.size());
    if (!sendAll(sock, (const char*)&len, sizeof(len))) return false;
    if (!sendAll(sock, msg.data(), msg.size())) return false;
    return true;
}

bool recvMessage(SOCKET sock, std::string& msg) {
    uint32_t len_net;
    if (!recvAll(sock, (char*)&len_net, sizeof(len_net))) return false;
    uint32_t len = ntohl(len_net);
    msg.resize(len);
    if (!recvAll(sock, msg.data(), len)) return false;
    return true;
}

void server() {
    SOCKET listenSock = socket(AF_INET, SOCK_STREAM, 0);
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(PORT);
    bind(listenSock, (sockaddr*)&addr, sizeof(addr));
    listen(listenSock, SOMAXCONN);

    SOCKET client = accept(listenSock, nullptr, nullptr);
    std::string msg;
    int count = 0;
    while (recvMessage(client, msg)) {
        std::cout << "[Server] Received message #" << ++count << " (len=" << msg.size() << "): "
                  << msg.substr(0, 50) << (msg.size() > 50 ? "..." : "") << std::endl;
    }
    closesocket(client);
    closesocket(listenSock);
}

void client(int id) {
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    SOCKET sock = socket(AF_INET, SOCK_STREAM, 0);
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(PORT);
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);
    connect(sock, (sockaddr*)&addr, sizeof(addr));

    for (int i = 0; i < 5; ++i) {
        std::string m = "Client-" + std::to_string(id) + " message-" + std::to_string(i) + " " + std::string(100 + i * 10, 'x');
        sendMessage(sock, m);
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
    }
    closesocket(sock);
}

int main() {
    WSADATA wsa;
    WSAStartup(MAKEWORD(2, 2), &wsa);

    std::thread srv(server);
    std::this_thread::sleep_for(std::chrono::milliseconds(200));

    std::vector<std::thread> clients;
    clients.emplace_back(client, 1);
    clients.emplace_back(client, 2);

    for (auto& t : clients) t.join();
    srv.join();

    WSACleanup();
    return 0;
}
```""")

# 26. 抽象工厂模式
add("实现抽象工厂设计模式，创建产品族（UI组件：Button、Checkbox、TextField），支持不同风格的产品族（Windows风格、Mac风格），客户端使用抽象接口操作，无需知道具体实现。",
"""### 需求分析
抽象工厂模式：
1. 多个相关产品组成产品族
2. 一个工厂生产一整个产品族
3. 切换工厂即切换整套产品风格
4. 产品：Button、Checkbox、TextField
5. 产品族：WindowsUIFactory、MacUIFactory

### 设计思路
1. 抽象产品接口：Button/Checkbox/TextField，定义render()方法
2. 具体产品：WinButton、MacButton等
3. 抽象工厂UIFactory：createButton()/createCheckbox()/createTextField()
4. 具体工厂：WinFactory、MacFactory创建对应产品族
5. Application类使用抽象工厂创建UI

### 关键问题
- 产品族一致性：保证一起使用的对象属于同一产品族
- 新增产品vs新增产品族：增加新产品需要修改所有工厂接口（开闭原则倾斜性）
- vs工厂方法：工厂方法是一个方法创建一个产品；抽象工厂是多个方法创建产品族

### 代码实现
```cpp
#include <iostream>
#include <memory>
#include <string>

class Button {
public:
    virtual void render() const = 0;
    virtual void onClick() = 0;
    virtual ~Button() = default;
};

class Checkbox {
public:
    virtual void render() const = 0;
    virtual void toggle() = 0;
    virtual ~Checkbox() = default;
};

class TextField {
public:
    virtual void render() const = 0;
    virtual void setText(const std::string&) = 0;
    virtual ~TextField() = default;
};

class WinButton : public Button {
public:
    void render() const override { std::cout << "Rendering Windows-style Button" << std::endl; }
    void onClick() override { std::cout << "WinButton clicked!" << std::endl; }
};

class MacButton : public Button {
public:
    void render() const override { std::cout << "Rendering Mac-style Button" << std::endl; }
    void onClick() override { std::cout << "MacButton clicked!" << std::endl; }
};

class WinCheckbox : public Checkbox {
    bool checked = false;
public:
    void render() const override { std::cout << "Rendering Windows Checkbox (checked=" << checked << ")" << std::endl; }
    void toggle() override { checked = !checked; }
};

class MacCheckbox : public Checkbox {
    bool checked = false;
public:
    void render() const override { std::cout << "Rendering Mac Checkbox (checked=" << checked << ")" << std::endl; }
    void toggle() override { checked = !checked; }
};

class WinTextField : public TextField {
    std::string text;
public:
    void render() const override { std::cout << "Rendering Windows TextField: " << text << std::endl; }
    void setText(const std::string& t) override { text = t; }
};

class MacTextField : public TextField {
    std::string text;
public:
    void render() const override { std::cout << "Rendering Mac TextField: " << text << std::endl; }
    void setText(const std::string& t) override { text = t; }
};

class UIFactory {
public:
    virtual std::unique_ptr<Button> createButton() = 0;
    virtual std::unique_ptr<Checkbox> createCheckbox() = 0;
    virtual std::unique_ptr<TextField> createTextField() = 0;
    virtual ~UIFactory() = default;
};

class WinFactory : public UIFactory {
public:
    std::unique_ptr<Button> createButton() override { return std::make_unique<WinButton>(); }
    std::unique_ptr<Checkbox> createCheckbox() override { return std::make_unique<WinCheckbox>(); }
    std::unique_ptr<TextField> createTextField() override { return std::make_unique<WinTextField>(); }
};

class MacFactory : public UIFactory {
public:
    std::unique_ptr<Button> createButton() override { return std::make_unique<MacButton>(); }
    std::unique_ptr<Checkbox> createCheckbox() override { return std::make_unique<MacCheckbox>(); }
    std::unique_ptr<TextField> createTextField() override { return std::make_unique<MacTextField>(); }
};

class Application {
    std::unique_ptr<Button> button;
    std::unique_ptr<Checkbox> checkbox;
    std::unique_ptr<TextField> textfield;
public:
    Application(UIFactory& factory) {
        button = factory.createButton();
        checkbox = factory.createCheckbox();
        textfield = factory.createTextField();
    }
    void render() {
        button->render();
        checkbox->render();
        textfield->render();
    }
    void interact() {
        button->onClick();
        checkbox->toggle();
        textfield->setText("Hello World");
        textfield->render();
    }
};

int main() {
    std::cout << "=== Windows UI ===" << std::endl;
    WinFactory winFactory;
    Application winApp(winFactory);
    winApp.render();
    winApp.interact();

    std::cout << "\\n=== Mac UI ===" << std::endl;
    MacFactory macFactory;
    Application macApp(macFactory);
    macApp.render();

    return 0;
}
```""")

# 27. select IO多路复用
add("使用select函数实现IO多路复用，在单线程中同时处理多个客户端连接，实现一个简单的echo服务器，对比多线程模型和IO多路复用模型的差异。",
"""### 需求分析
select IO多路复用：
1. 单线程管理多个socket
2. select等待一组socket就绪
3. 同时处理accept和多个client的recv
4. echo服务器：收到什么发回什么
5. 理解fd_set的使用

### 设计思路
1. 创建监听socket
2. 维护一个所有活跃socket的集合
3. FD_ZERO/FD_SET/FD_ISSET宏操作fd_set
4. select阻塞等待有socket就绪
5. 遍历检查：监听socket有新连接，client socket有数据
6. Windows平台select第一个参数忽略（兼容用0）

### 关键问题
- fd_set大小限制：FD_SETSIZE默认64
- 每次调用select前必须重新设置fd_set（select会修改它）
- timeout：NULL永久阻塞，0立即返回，或指定时间
- 跨平台：Linux下nfds是maxfd+1
- 性能：大量连接时select效率低（O(n)遍历），用epoll/IOCP替代

### 代码实现
```cpp
#include <iostream>
#include <string>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <vector>
#include <algorithm>

#pragma comment(lib, "ws2_32.lib")

const int PORT = 9090;
const int BUF_SIZE = 1024;

int main() {
    WSADATA wsa;
    WSAStartup(MAKEWORD(2, 2), &wsa);

    SOCKET listenSock = socket(AF_INET, SOCK_STREAM, 0);
    BOOL reuse = TRUE;
    setsockopt(listenSock, SOL_SOCKET, SO_REUSEADDR, (const char*)&reuse, sizeof(reuse));

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(PORT);
    bind(listenSock, (sockaddr*)&addr, sizeof(addr));
    listen(listenSock, SOMAXCONN);

    std::vector<SOCKET> clients;
    std::cout << "Echo server with select() running on port " << PORT << std::endl;

    while (true) {
        fd_set readfds;
        FD_ZERO(&readfds);
        FD_SET(listenSock, &readfds);
        for (SOCKET s : clients) FD_SET(s, &readfds);

        timeval timeout{0, 100000};
        int activity = select(0, &readfds, nullptr, nullptr, &timeout);
        if (activity == SOCKET_ERROR) break;

        if (FD_ISSET(listenSock, &readfds)) {
            SOCKET client = accept(listenSock, nullptr, nullptr);
            clients.push_back(client);
            std::cout << "New client connected, total: " << clients.size() << std::endl;
        }

        std::vector<SOCKET> toRemove;
        for (SOCKET s : clients) {
            if (FD_ISSET(s, &readfds)) {
                char buf[BUF_SIZE];
                int recvLen = recv(s, buf, BUF_SIZE - 1, 0);
                if (recvLen <= 0) {
                    toRemove.push_back(s);
                    closesocket(s);
                } else {
                    buf[recvLen] = '\0';
                    send(s, buf, recvLen, 0);
                }
            }
        }

        for (SOCKET s : toRemove) {
            clients.erase(std::remove(clients.begin(), clients.end(), s), clients.end());
        }
        if (!toRemove.empty()) {
            std::cout << "Client disconnected, total: " << clients.size() << std::endl;
        }
    }

    for (SOCKET s : clients) closesocket(s);
    closesocket(listenSock);
    WSACleanup();
    return 0;
}
```""")

# 28. 文件复制带进度
add("实现带进度显示的大文件复制功能，使用大缓冲区分块读取和写入，实时显示复制进度百分比、已复制大小、复制速度，支持取消操作。",
"""### 需求分析
带进度文件复制：
1. 大文件分块复制，避免一次性加载到内存
2. 实时显示进度百分比
3. 计算复制速度（MB/s）
4. 显示已复制/总大小
5. Windows平台用Win32 API或C++文件流
6. 支持二进制文件复制

### 设计思路
1. 先GetFileSizeEx获取源文件总大小
2. 用固定大小缓冲区（如64KB）循环ReadFile/WriteFile
3. 记录开始时间，计算已用时间和速度
4. 每复制一定块数输出进度
5. 可以用CreateEvent/原子变量检查取消标志
6. 正确错误处理和资源清理

### 关键问题
- 缓冲区大小：太小速度慢，太大占用内存多，64KB-1MB合适
- 时间计算：使用std::chrono计算速度
- 刷新输出：\r回到行首覆盖显示
- 磁盘缓存：写入速度可能显示虚假快（系统缓存）
- 大文件支持：使用LARGE_INTEGER处理超过4GB文件

### 代码实现
```cpp
#include <windows.h>
#include <iostream>
#include <iomanip>
#include <chrono>
#include <string>

bool copyFileWithProgress(const std::string& src, const std::string& dst) {
    HANDLE hSrc = CreateFileA(src.c_str(), GENERIC_READ, FILE_SHARE_READ, nullptr,
        OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (hSrc == INVALID_HANDLE_VALUE) {
        std::cerr << "Cannot open source file" << std::endl;
        return false;
    }

    LARGE_INTEGER fileSize;
    GetFileSizeEx(hSrc, &fileSize);

    HANDLE hDst = CreateFileA(dst.c_str(), GENERIC_WRITE, 0, nullptr,
        CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (hDst == INVALID_HANDLE_VALUE) {
        CloseHandle(hSrc);
        return false;
    }

    const DWORD BUF_SIZE = 1024 * 64;
    char* buffer = new char[BUF_SIZE];
    LARGE_INTEGER totalCopied;
    totalCopied.QuadPart = 0;

    auto startTime = std::chrono::high_resolution_clock::now();
    DWORD read, written;
    bool success = true;

    std::cout << std::fixed << std::setprecision(2);

    while (ReadFile(hSrc, buffer, BUF_SIZE, &read, nullptr) && read > 0) {
        if (!WriteFile(hDst, buffer, read, &written, nullptr) || written != read) {
            success = false;
            break;
        }
        totalCopied.QuadPart += read;

        auto now = std::chrono::high_resolution_clock::now();
        auto elapsed = std::chrono::duration<double>(now - startTime).count();
        double progress = (double)totalCopied.QuadPart / fileSize.QuadPart * 100;
        double speed = elapsed > 0 ? totalCopied.QuadPart / 1024.0 / 1024.0 / elapsed : 0;

        std::cout << "\rProgress: " << std::setw(6) << progress << "% | "
                  << std::setw(8) << (totalCopied.QuadPart / 1024.0 / 1024.0) << " / "
                  << std::setw(8) << (fileSize.QuadPart / 1024.0 / 1024.0) << " MB | "
                  << std::setw(7) << speed << " MB/s";
        std::cout.flush();
    }

    auto endTime = std::chrono::high_resolution_clock::now();
    auto totalTime = std::chrono::duration<double>(endTime - startTime).count();

    delete[] buffer;
    CloseHandle(hSrc);
    CloseHandle(hDst);

    std::cout << std::endl;
    if (success) {
        std::cout << "Copy completed in " << totalTime << "s" << std::endl;
    }
    return success;
}

int main() {
    const std::string srcFile = "source.bin";
    const std::string dstFile = "destination.bin";

    HANDLE hTest = CreateFileA(srcFile.c_str(), GENERIC_WRITE, 0, nullptr,
        CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (hTest != INVALID_HANDLE_VALUE) {
        const int testSize = 50 * 1024 * 1024;
        char* buf = new char[4096];
        for (int i = 0; i < 4096; i++) buf[i] = (char)(i % 256);
        DWORD written;
        for (int i = 0; i < testSize / 4096; i++) {
            WriteFile(hTest, buf, 4096, &written, nullptr);
        }
        delete[] buf;
        CloseHandle(hTest);
    }

    copyFileWithProgress(srcFile, dstFile);

    DeleteFileA(srcFile.c_str());
    DeleteFileA(dstFile.c_str());
    return 0;
}
```""")

# 29. 并行for_each
add("实现并行版本的std::for_each算法，将数据范围分块交给多个线程并行处理，使用std::thread硬件并发数决定线程数，对比并行和串行执行的性能差异。",
"""### 需求分析
并行for_each：
1. 对区间内每个元素应用函数
2. 多线程并行执行
3. 根据硬件核心数自动选择线程数
4. 分块处理负载均衡
5. 等待所有线程完成
6. 对比串行性能

### 设计思路
1. 获取std::thread::hardware_concurrency()
2. 计算每个线程处理的元素范围
3. 创建线程处理各自块
4. join所有线程
5. 处理元素数不能整除线程数的边界情况
6. 对随机访问迭代器优化（可直接计算偏移）

### 关键问题
- 迭代器类型：本实现要求随机访问迭代器（vector/array）
- 异常安全：一个线程抛异常需要传播
- 虚假共享：避免相邻元素被不同线程频繁写（缓存行对齐）
- 粒度：分块太小线程开销大，太大负载不均衡

### 代码实现
```cpp
#include <iostream>
#include <vector>
#include <thread>
#include <future>
#include <chrono>
#include <algorithm>
#include <numeric>

template<typename Iterator, typename Func>
void parallelForEach(Iterator begin, Iterator end, Func func) {
    const size_t length = std::distance(begin, end);
    if (length == 0) return;

    const size_t minPerThread = 25;
    const size_t hardwareThreads = std::thread::hardware_concurrency();
    const size_t numThreads = std::min(hardwareThreads != 0 ? hardwareThreads : 2,
                                       (length + minPerThread - 1) / minPerThread);
    const size_t blockSize = length / numThreads;

    std::vector<std::future<void>> futures;
    Iterator blockStart = begin;

    for (size_t i = 0; i < numThreads - 1; ++i) {
        Iterator blockEnd = blockStart;
        std::advance(blockEnd, blockSize);
        futures.push_back(std::async(std::launch::async, [blockStart, blockEnd, &func] {
            std::for_each(blockStart, blockEnd, func);
        }));
        blockStart = blockEnd;
    }

    std::for_each(blockStart, end, func);

    for (auto& f : futures) {
        f.get();
    }
}

int main() {
    const size_t N = 10000000;
    std::vector<double> data(N);
    std::iota(data.begin(), data.end(), 0.0);

    auto start1 = std::chrono::high_resolution_clock::now();
    std::for_each(data.begin(), data.end(), [](double& x) {
        x = std::sqrt(x) * std::sin(x) / (std::cos(x) + 0.001);
    });
    auto end1 = std::chrono::high_resolution_clock::now();
    auto serial = std::chrono::duration<double>(end1 - start1).count();
    std::cout << "Serial for_each: " << serial << "s" << std::endl;

    std::iota(data.begin(), data.end(), 0.0);

    auto start2 = std::chrono::high_resolution_clock::now();
    parallelForEach(data.begin(), data.end(), [](double& x) {
        x = std::sqrt(x) * std::sin(x) / (std::cos(x) + 0.001);
    });
    auto end2 = std::chrono::high_resolution_clock::now();
    auto parallel = std::chrono::duration<double>(end2 - start2).count();
    std::cout << "Parallel for_each: " << parallel << "s" << std::endl;
    std::cout << "Speedup: " << serial / parallel << "x" << std::endl;

    return 0;
}
```""")

# 30. 死锁避免
add("演示多线程编程中的死锁场景，使用std::scoped_lock（C++17）或std::lock同时锁定多个互斥锁来避免死锁，对比不同加锁顺序导致的死锁情况。",
"""### 需求分析
死锁避免：
1. 死锁四个必要条件：互斥、占有等待、不可剥夺、循环等待
2. 经典场景：两个线程各持有一个锁并等待对方的锁
3. 解决方案：固定加锁顺序、std::scoped_lock、std::lock
4. 演示错误场景和正确做法
5. 使用RAII锁管理

### 设计思路
1. 创建两个互斥锁A和B
2. 错误示例：线程1锁A再锁B，线程2锁B再锁A -> 死锁（注释掉避免真死锁）
3. 正确示例1：两个线程都按A->B顺序加锁
4. 正确示例2：使用std::scoped_lock同时锁定多个锁
5. 使用std::lock+adopt_lock方式

### 关键问题
- 调试死锁：死锁时程序挂起，可通过调试器查看线程等待链
- 预防策略：破坏四个必要条件之一
- std::scoped_lock（C++17）：可变参数，同时锁定多个mutex，避免死锁
- std::adopt_lock：告知lock_guard mutex已被锁定，只需接管所有权

### 代码实现
```cpp
#include <iostream>
#include <thread>
#include <mutex>
#include <chrono>

std::mutex mutexA;
std::mutex mutexB;

void badThread1() {
    std::cout << "[Bad-Thread1] Trying to lock A..." << std::endl;
    std::lock_guard<std::mutex> lockA(mutexA);
    std::cout << "[Bad-Thread1] Locked A, sleeping..." << std::endl;
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    std::cout << "[Bad-Thread1] Trying to lock B..." << std::endl;
    std::lock_guard<std::mutex> lockB(mutexB);
    std::cout << "[Bad-Thread1] Locked B, working..." << std::endl;
}

void badThread2() {
    std::cout << "[Bad-Thread2] Trying to lock B..." << std::endl;
    std::lock_guard<std::mutex> lockB(mutexB);
    std::cout << "[Bad-Thread2] Locked B, sleeping..." << std::endl;
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    std::cout << "[Bad-Thread2] Trying to lock A..." << std::endl;
    std::lock_guard<std::mutex> lockA(mutexA);
    std::cout << "[Bad-Thread2] Locked A, working..." << std::endl;
}

void goodThread1() {
    std::cout << "[Good-Thread1] Using scoped_lock..." << std::endl;
    std::scoped_lock lock(mutexA, mutexB);
    std::cout << "[Good-Thread1] Acquired both locks, working..." << std::endl;
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    std::cout << "[Good-Thread1] Done" << std::endl;
}

void goodThread2() {
    std::cout << "[Good-Thread2] Using scoped_lock..." << std::endl;
    std::scoped_lock lock(mutexA, mutexB);
    std::cout << "[Good-Thread2] Acquired both locks, working..." << std::endl;
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    std::cout << "[Good-Thread2] Done" << std::endl;
}

int main() {
    std::cout << "=== Deadlock avoidance demo ===" << std::endl;
    std::cout << "(Bad example is commented out to prevent actual deadlock)\\n" << std::endl;

    std::cout << "--- Bad ordering (would deadlock) ---" << std::endl;
    std::cout << "Thread1: lock A -> lock B" << std::endl;
    std::cout << "Thread2: lock B -> lock A" << std::endl;
    std::cout << "This causes circular wait!\\n" << std::endl;

    std::cout << "--- Good: using std::scoped_lock ---" << std::endl;
    std::thread t1(goodThread1);
    std::thread t2(goodThread2);
    t1.join();
    t2.join();

    std::cout << "\\nBoth threads completed without deadlock" << std::endl;
    return 0;
}
```""")

# 保存这10条
with open("f:/数据集/doubao/cot_data/cpp/cpp_cot_3_part3a.json", "w", encoding="utf-8") as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)
print(f"Generated {len(entries)} entries in part3a")

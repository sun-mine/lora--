
import json
import os

entries = []

def add(instr, output):
    entries.append({"instruction": instr, "input": "", "output": output})

# 1. 单例模式（线程安全）
add("实现线程安全的单例模式，讨论Meyers Singleton、call_once、双重检查锁定等多种实现方式及其优劣",
"""思考单例模式的各种实现方式。

单例模式确保一个类只有一个实例，并提供全局访问点。在C++中实现线程安全的单例有几种方式：

1. 局部静态变量（Meyers Singleton）：C++11保证函数内静态变量初始化是线程安全的，最简单最推荐。
2. std::call_once + std::once_flag：可以延迟初始化，配合unique_ptr使用。
3. 双重检查锁定（DCLP）：C++11前常用，但C++11前没有内存模型会有问题；C++11后用atomic可以正确实现但没必要了。

我来实现几种并对比：

Meyers Singleton为什么线程安全？C++11标准规定：如果变量初始化时并发进入，初始化只发生一次，其他线程等待。这是编译器/标准库实现的，不用我们写锁。

双重检查锁定为什么容易错？因为new一个对象实际上分三步：分配内存、构造对象、赋值给指针。如果没有内存序约束，编译器/CPU可能重排，导致其他线程拿到未构造完的对象。C++11用atomic的acquire/release可以解决。

我写代码演示三种方式：

```cpp
#include <iostream>
#include <memory>
#include <mutex>
#include <thread>

// 方法1：Meyers Singleton（推荐）
class Singleton1 {
public:
    static Singleton1& getInstance() {
        static Singleton1 instance;
        return instance;
    }
    void doWork() { std::cout << "Singleton1 working\\n"; }
private:
    Singleton1() { std::cout << "Singleton1 构造\\n"; }
    ~Singleton1() = default;
    Singleton1(const Singleton1&) = delete;
    Singleton1& operator=(const Singleton1&) = delete;
};

// 方法2：call_once
class Singleton2 {
    static std::unique_ptr<Singleton2> instance;
    static std::once_flag flag;
public:
    static Singleton2& getInstance() {
        std::call_once(flag, []{ instance.reset(new Singleton2); });
        return *instance;
    }
    void doWork() { std::cout << "Singleton2 working\\n"; }
private:
    Singleton2() { std::cout << "Singleton2 构造\\n"; }
};
std::unique_ptr<Singleton2> Singleton2::instance;
std::once_flag Singleton2::flag;

// 方法3：DCLP with atomic（C++11 才正确）
class Singleton3 {
    static std::atomic<Singleton3*> instance;
    static std::mutex mtx;
public:
    static Singleton3* getInstance() {
        Singleton3* p = instance.load(std::memory_order_acquire);
        if (p == nullptr) {
            std::lock_guard<std::mutex> lock(mtx);
            p = instance.load(std::memory_order_relaxed);
            if (p == nullptr) {
                p = new Singleton3();
                instance.store(p, std::memory_order_release);
            }
        }
        return p;
    }
private:
    Singleton3() { std::cout << "Singleton3 构造\\n"; }
};
std::atomic<Singleton3*> Singleton3::instance{nullptr};
std::mutex Singleton3::mtx;

int main() {
    std::vector<std::thread> threads;
    for (int i = 0; i < 5; ++i) {
        threads.emplace_back([]{
            Singleton1::getInstance().doWork();
            Singleton2::getInstance().doWork();
            Singleton3::getInstance()->doWork();
        });
    }
    for (auto& t : threads) t.join();
    return 0;
}
```

总结：优先用Meyers Singleton，最简单最不容易错。DCLP虽然高效但复杂，不推荐手写。""")

# 2. 装饰器模式
add("使用装饰器模式实现IO流：可以组合压缩、加密、缓冲等功能，动态添加职责而不修改原类",
"""思考装饰器模式如何实现功能的动态组合。

装饰器模式：动态地给对象添加额外职责，比继承更灵活。装饰器和被装饰对象实现同一个接口，装饰器持有一个接口指针，在调用前后添加自己的行为。

经典例子：C++标准库的iostream其实就是装饰器模式。我来实现类似Java IO流的装饰：基础文件流，可以包一层缓冲流，再包一层压缩流，再包一层加密流...

关键：装饰器继承同一个抽象基类，构造时传入同类型对象。层层包裹。

先定义抽象组件Stream：
class Stream {
public:
    virtual ~Stream() = default;
    virtual void write(const std::string& data) = 0;
    virtual std::string read() = 0;
};

具体组件FileStream，然后装饰器基类Decorator继承Stream，持有Stream*。然后各种具体装饰器BufferedStream、CompressedStream、EncryptedStream继承Decorator。

```cpp
#include <iostream>
#include <string>
#include <memory>
#include <sstream>
#include <algorithm>

class Stream {
public:
    virtual ~Stream() = default;
    virtual void write(const std::string& data) = 0;
    virtual std::string read(size_t n) = 0;
};

class FileStream : public Stream {
    std::string content;
    size_t pos = 0;
public:
    void write(const std::string& data) override {
        content += data;
        std::cout << "[文件] 写入" << data.size() << "字节\\n";
    }
    std::string read(size_t n) override {
        size_t take = std::min(n, content.size() - pos);
        std::string res = content.substr(pos, take);
        pos += take;
        return res;
    }
};

class StreamDecorator : public Stream {
protected:
    std::unique_ptr<Stream> inner;
public:
    explicit StreamDecorator(std::unique_ptr<Stream> s) : inner(std::move(s)) {}
};

class BufferedStream : public StreamDecorator {
    std::string buffer;
    static const size_t BUF_SIZE = 4096;
public:
    using StreamDecorator::StreamDecorator;
    void write(const std::string& data) override {
        buffer += data;
        std::cout << "[缓冲] 加入缓冲区, 大小=" << buffer.size() << "\\n";
        if (buffer.size() >= BUF_SIZE) flush();
    }
    void flush() {
        if (!buffer.empty()) {
            std::cout << "[缓冲] 刷新" << buffer.size() << "字节\\n";
            inner->write(buffer);
            buffer.clear();
        }
    }
    std::string read(size_t n) override {
        flush();
        return inner->read(n);
    }
    ~BufferedStream() { flush(); }
};

class EncryptedStream : public StreamDecorator {
    char key;
    std::string encrypt(const std::string& s) {
        std::string res;
        for (char c : s) res += c ^ key;
        return res;
    }
public:
    EncryptedStream(std::unique_ptr<Stream> s, char k = 0x5A) : StreamDecorator(std::move(s)), key(k) {}
    void write(const std::string& data) override {
        std::string enc = encrypt(data);
        std::cout << "[加密] 加密后写入\\n";
        inner->write(enc);
    }
    std::string read(size_t n) override {
        return encrypt(inner->read(n));
    }
};

class CompressedStream : public StreamDecorator {
public:
    using StreamDecorator::StreamDecorator;
    void write(const std::string& data) override {
        std::string comp;
        for (size_t i = 0; i < data.size(); ) {
            char c = data[i];
            size_t cnt = 0;
            while (i < data.size() && data[i] == c && cnt < 255) { ++cnt; ++i; }
            comp += (char)cnt;
            comp += c;
        }
        std::cout << "[压缩] RLE压缩 " << data.size() << "->" << comp.size() << "字节\\n";
        inner->write(comp);
    }
    std::string read(size_t n) override {
        std::string comp = inner->read(n * 2);
        std::string res;
        for (size_t i = 0; i + 1 < comp.size(); i += 2) {
            res.append((unsigned char)comp[i], comp[i+1]);
        }
        return res;
    }
};

int main() {
    std::cout << "=== 文件 -> 压缩 -> 加密 -> 缓冲 ===\\n";
    auto stream = std::make_unique<BufferedStream>(
                   std::make_unique<EncryptedStream>(
                     std::make_unique<CompressedStream>(
                       std::make_unique<FileStream>(), 0x42
                     ), 'K')
                  );
    stream->write("Hello World Hello World Hello World");
    stream.reset();
    return 0;
}
```

装饰器模式优势：可以任意组合功能，比继承爆炸（N种功能需要2^N个子类）好太多。""")

# 3. 适配器模式
add("实现适配器模式：将一个不兼容的第三方日志接口适配成我们自己的Logger接口，演示类适配器和对象适配器",
"""思考适配器模式解决什么问题。

适配器模式把一个类的接口转换成客户期望的另一个接口，让原本不兼容的类可以合作。就像旅行插头转换器。

两种实现：
1. 对象适配器：组合方式，适配器持有被适配对象，实现目标接口。更灵活。
2. 类适配器：多继承同时继承目标接口和被适配类。在C++中可行但耦合度高。

场景：假设我们有一个老版本的第三方日志库ThirdPartyLogger，方法名是Print(int level, const char*)，而我们系统期望Logger接口有debug/info/warn/error方法。写个适配器。

```cpp
#include <iostream>
#include <string>
#include <memory>

class Logger {
public:
    virtual ~Logger() = default;
    virtual void debug(const std::string& msg) = 0;
    virtual void info(const std::string& msg) = 0;
    virtual void warn(const std::string& msg) = 0;
    virtual void error(const std::string& msg) = 0;
};

class ThirdPartyLogger {
public:
    enum Level { L_DEBUG=0, L_INFO=1, L_WARN=2, L_ERROR=3 };
    void Print(int level, const char* msg) {
        const char* names[] = {"DEBUG", "INFO", "WARN", "ERROR"};
        std::cout << "[" << names[level] << "] " << msg << "\\n";
    }
};

// 对象适配器（组合方式，推荐）
class LoggerAdapter : public Logger {
    ThirdPartyLogger& logger;
public:
    explicit LoggerAdapter(ThirdPartyLogger& l) : logger(l) {}
    void debug(const std::string& msg) override { logger.Print(ThirdPartyLogger::L_DEBUG, msg.c_str()); }
    void info(const std::string& msg) override { logger.Print(ThirdPartyLogger::L_INFO, msg.c_str()); }
    void warn(const std::string& msg) override { logger.Print(ThirdPartyLogger::L_WARN, msg.c_str()); }
    void error(const std::string& msg) override { logger.Print(ThirdPartyLogger::L_ERROR, msg.c_str()); }
};

// 类适配器（多继承方式）
class ClassLoggerAdapter : public Logger, private ThirdPartyLogger {
public:
    void debug(const std::string& msg) override { Print(L_DEBUG, msg.c_str()); }
    void info(const std::string& msg) override { Print(L_INFO, msg.c_str()); }
    void warn(const std::string& msg) override { Print(L_WARN, msg.c_str()); }
    void error(const std::string& msg) override { Print(L_ERROR, msg.c_str()); }
};

void useLogger(Logger& logger) {
    logger.info("系统启动");
    logger.debug("调试信息");
    logger.warn("警告");
    logger.error("错误发生");
}

int main() {
    std::cout << "=== 对象适配器 ===\\n";
    ThirdPartyLogger thirdParty;
    LoggerAdapter adapter(thirdParty);
    useLogger(adapter);

    std::cout << "\\n=== 类适配器 ===\\n";
    ClassLoggerAdapter adapter2;
    useLogger(adapter2);
    return 0;
}
```

要点：优先用对象适配器（组合优于继承）。适配器模式是典型的"事后"补救，当你不能修改已有代码时用它。""")

# 4. 命令模式
add("使用命令模式实现撤销/重做功能：简单的文本编辑器支持添加文字、删除文字，可以undo/redo",
"""思考命令模式如何支持撤销重做。

命令模式把请求封装成对象，从而可以参数化不同请求、排队请求、记录日志、支持撤销。每个命令有execute()和undo()。

文本编辑器例子：维护两个栈——undo栈和redo栈。执行命令时压入undo栈，清空redo栈。undo时弹出执行undo压入redo栈；redo时弹出执行execute压入undo栈。

设计：
- Command抽象类：execute()、undo()
- AddTextCommand：添加文字，undo时删除对应长度
- DeleteTextCommand：删除文字，undo时把文字加回去
- Editor类：维护文本、caret位置、两个栈

```cpp
#include <iostream>
#include <string>
#include <stack>
#include <memory>
#include <vector>

class Command {
public:
    virtual ~Command() = default;
    virtual void execute() = 0;
    virtual void undo() = 0;
};

class Editor {
    std::string content;
    size_t caret = 0;
    std::stack<std::unique_ptr<Command>> undoStack;
    std::stack<std::unique_ptr<Command>> redoStack;
public:
    void insert(char c) { content.insert(caret++, 1, c); }
    void insert(const std::string& s) { content.insert(caret, s); caret += s.size(); }
    void erase(size_t n) {
        if (n > caret) n = caret;
        content.erase(caret - n, n);
        caret -= n;
    }
    std::string getLastN(size_t n) {
        if (n > caret) n = caret;
        return content.substr(caret - n, n);
    }
    size_t getCaret() const { return caret; }
    const std::string& getText() const { return content; }

    void exec(std::unique_ptr<Command> cmd) {
        cmd->execute();
        undoStack.push(std::move(cmd));
        while (!redoStack.empty()) redoStack.pop();
    }
    void undo() {
        if (undoStack.empty()) return;
        auto cmd = std::move(undoStack.top()); undoStack.pop();
        cmd->undo();
        redoStack.push(std::move(cmd));
    }
    void redo() {
        if (redoStack.empty()) return;
        auto cmd = std::move(redoStack.top()); redoStack.pop();
        cmd->execute();
        undoStack.push(std::move(cmd));
    }
};

class TypeCommand : public Command {
    Editor& editor;
    std::string text;
public:
    TypeCommand(Editor& e, std::string t) : editor(e), text(std::move(t)) {}
    void execute() override { editor.insert(text); }
    void undo() override { editor.erase(text.size()); }
};

class BackspaceCommand : public Command {
    Editor& editor;
    std::string deleted;
    size_t n;
public:
    BackspaceCommand(Editor& e, size_t cnt = 1) : editor(e), n(cnt) {}
    void execute() override {
        deleted = editor.getLastN(n);
        editor.erase(n);
    }
    void undo() override { editor.insert(deleted); }
};

int main() {
    Editor ed;
    ed.exec(std::make_unique<TypeCommand>(ed, "Hello"));
    ed.exec(std::make_unique<TypeCommand>(ed, " World"));
    std::cout << "输入后: " << ed.getText() << "\\n";

    ed.undo();
    std::cout << "撤销一次: " << ed.getText() << "\\n";

    ed.exec(std::make_unique<TypeCommand>(ed, " C++"));
    std::cout << "输入C++后: " << ed.getText() << "\\n";

    ed.undo(); ed.undo();
    std::cout << "两次撤销: " << ed.getText() << "\\n";

    ed.redo();
    std::cout << "重做: " << ed.getText() << "\\n";
    return 0;
}
```

命令模式核心：把"操作"变成对象，可以存储、传递、排队、撤销。这是很多GUI框架、事务系统的基础。""")

# 5. 责任链模式
add("实现责任链模式：一个HTTP请求处理链（认证→日志→权限检查→业务处理），每个处理器决定处理或传给下一个",
"""思考责任链模式的应用。

责任链模式：多个处理器对象连成一条链，请求沿链传递，直到有对象处理它。每个处理器持有下一个处理器的引用。

典型场景：HTTP中间件、事件冒泡、日志处理、审批流程。

我实现一个HTTP请求处理管道：
1. AuthenticationHandler：检查token
2. LoggingHandler：记录请求
3. AuthorizationHandler：检查权限
4. BusinessHandler：实际处理

如果某一步失败，返回错误响应，不再往下传。

```cpp
#include <iostream>
#include <string>
#include <memory>
#include <unordered_map>

struct HttpRequest {
    std::string path;
    std::string method;
    std::unordered_map<std::string, std::string> headers;
    std::string body;
    bool authenticated = false;
    std::string userRole;
};

struct HttpResponse {
    int code;
    std::string body;
    HttpResponse(int c, std::string b) : code(c), body(std::move(b)) {}
};

class Handler {
protected:
    std::unique_ptr<Handler> next;
public:
    virtual ~Handler() = default;
    void setNext(std::unique_ptr<Handler> n) { next = std::move(n); }
    virtual HttpResponse handle(HttpRequest& req) {
        if (next) return next->handle(req);
        return HttpResponse(404, "Not Found");
    }
};

class AuthHandler : public Handler {
public:
    HttpResponse handle(HttpRequest& req) override {
        auto it = req.headers.find("Authorization");
        if (it == req.headers.end() || it->second != "Bearer valid_token") {
            return HttpResponse(401, "Unauthorized");
        }
        req.authenticated = true;
        req.userRole = "admin";
        std::cout << "[认证] 通过\\n";
        return Handler::handle(req);
    }
};

class LogHandler : public Handler {
public:
    HttpResponse handle(HttpRequest& req) override {
        std::cout << "[日志] " << req.method << " " << req.path << "\\n";
        return Handler::handle(req);
    }
};

class PermissionHandler : public Handler {
public:
    HttpResponse handle(HttpRequest& req) override {
        if (req.path == "/admin" && req.userRole != "admin") {
            return HttpResponse(403, "Forbidden");
        }
        std::cout << "[权限检查] 通过\\n";
        return Handler::handle(req);
    }
};

class BusinessHandler : public Handler {
public:
    HttpResponse handle(HttpRequest& req) override {
        std::cout << "[业务] 处理 " << req.path << "\\n";
        return HttpResponse(200, "Hello from " + req.path);
    }
};

int main() {
    auto chain = std::make_unique<AuthHandler>();
    auto* auth = chain.get();
    auto log = std::make_unique<LogHandler>();
    auto perm = std::make_unique<PermissionHandler>();
    auto biz = std::make_unique<BusinessHandler>();

    perm->setNext(std::move(biz));
    log->setNext(std::move(perm));
    auth->setNext(std::move(log));

    auto testRequest = [&](bool withAuth, const std::string& path) {
        HttpRequest req;
        req.method = "GET"; req.path = path;
        if (withAuth) req.headers["Authorization"] = "Bearer valid_token";
        std::cout << "\\n--- 请求 " << path << (withAuth ? " 带认证" : " 无认证") << " ---\\n";
        auto resp = chain->handle(req);
        std::cout << "响应: " << resp.code << " " << resp.body << "\\n";
    };

    testRequest(false, "/home");
    testRequest(true, "/home");
    testRequest(true, "/admin");
    return 0;
}
```

责任链要点：每个处理器只关心自己的责任，可以灵活添加/删除/重排处理器，符合开闭原则。""")

print(f"Added {len(entries)} entries, building more...")

with open("cot3_entries.json", "w", encoding="utf-8") as f:
    json.dump(entries, f, ensure_ascii=False)

print(f"Saved {len(entries)} entries to cot3_entries.json")

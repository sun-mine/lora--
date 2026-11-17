import json

data = []

def add(instr, output):
    data.append({
        "instruction": instr,
        "input": "",
        "output": output
    })

# 50条高质量C++ CoT题目，每条都有详细思考过程

entries = [
    # 文件操作 (10条)
    ("实现一个线程安全的日志系统，支持多线程写入文件，按日期和大小滚动，支持不同日志级别",
     """让我逐步实现线程安全的日志系统。

需求分析：
- 多线程同时写入不能错乱
- 按日期（每天）和大小（超过阈值）滚动文件
- DEBUG/INFO/WARNING/ERROR四级过滤
- 异步写入避免阻塞业务线程

设计思路：
单例模式 + 生产者消费者队列。业务线程把日志放入队列，后台线程负责实际写入文件，这样只需要一个后台线程写文件，天然避免了多线程写文件的竞争问题，同时性能更好。

第一步，定义日志级别枚举：
enum class LogLevel { DEBUG, INFO, WARNING, ERROR };

第二步，日志格式：时间戳 [级别] [线程ID] 消息内容。用localtime_s获取本地时间，std::put_time格式化，加上毫秒。

第三步，文件滚动：每次写入前检查大小，超过maxFileSize_就创建新文件；日期检查可以简化为检查文件名中的日期是否是今天。

第四步，优雅退出：析构函数设置running_为false，通知后台线程，等待队列中所有日志写完再join。

第五步，宏定义方便使用：LOG_DEBUG、LOG_INFO等宏自动记录文件名行号。

关键问题解决：
- 为什么用单例？日志系统全局唯一，方便到处使用
- 为什么后台线程？写磁盘相对慢，不能阻塞业务逻辑
- 条件变量而非忙等：没有日志时线程休眠，不消耗CPU

代码实现：
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <mutex>
#include <queue>
#include <thread>
#include <condition_variable>
#include <atomic>
#include <sstream>
#include <chrono>
#include <iomanip>

enum class LogLevel { DEBUG, INFO, WARNING, ERROR };

class Logger {
public:
    static Logger& instance() {
        static Logger inst;
        return inst;
    }

    void setLevel(LogLevel l) { minLevel_ = l; }

    template<typename... Args>
    void log(LogLevel level, Args&&... args) {
        if (level < minLevel_) return;
        std::ostringstream oss;
        (oss << ... << std::forward<Args>(args));
        std::string msg = format(level, oss.str());
        {
            std::lock_guard<std::mutex> lk(mtx_);
            queue_.push(std::move(msg));
        }
        cv_.notify_one();
    }

    ~Logger() {
        running_ = false;
        cv_.notify_one();
        if (writer_.joinable()) writer_.join();
        if (out_.is_open()) out_.close();
    }

private:
    Logger() : running_(true), minLevel_(LogLevel::DEBUG), maxSize_(10*1024*1024), curSize_(0) {
        openNew();
        writer_ = std::thread(&Logger::writeLoop, this);
    }
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;

    std::string format(LogLevel level, const std::string& msg) {
        auto now = std::chrono::system_clock::now();
        auto t = std::chrono::system_clock::to_time_t(now);
        std::tm tm;
        localtime_s(&tm, &t);
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
            now.time_since_epoch()) % 1000;
        std::ostringstream oss;
        oss << '[' << std::put_time(&tm, "%Y-%m-%d %H:%M:%S")
            << '.' << std::setfill('0') << std::setw(3) << ms.count() << "] ";
        const char* names[] = {"DEBUG", "INFO", "WARNING", "ERROR"};
        oss << '[' << names[static_cast<int>(level)] << "] ";
        oss << msg << '\\n';
        return oss.str();
    }

    void openNew() {
        if (out_.is_open()) out_.close();
        auto now = std::chrono::system_clock::now();
        auto t = std::chrono::system_clock::to_time_t(now);
        std::tm tm;
        localtime_s(&tm, &t);
        std::ostringstream fn;
        fn << "log_" << std::put_time(&tm, "%Y%m%d_%H%M%S") << ".log";
        out_.open(fn.str(), std::ios::app);
        curSize_ = 0;
    }

    void writeLoop() {
        while (running_ || !queue_.empty()) {
            std::string msg;
            {
                std::unique_lock<std::mutex> lk(mtx_);
                cv_.wait(lk, [this]{ return !running_ || !queue_.empty(); });
                if (!running_ && queue_.empty()) break;
                msg = std::move(queue_.front());
                queue_.pop();
            }
            if (curSize_ + msg.size() > maxSize_) openNew();
            out_ << msg;
            out_.flush();
            curSize_ += msg.size();
        }
    }

    std::mutex mtx_;
    std::condition_variable cv_;
    std::queue<std::string> queue_;
    std::thread writer_;
    std::atomic<bool> running_;
    std::ofstream out_;
    size_t maxSize_, curSize_;
    LogLevel minLevel_;
};

#define LOG_DEBUG(...) Logger::instance().log(LogLevel::DEBUG, __VA_ARGS__)
#define LOG_INFO(...)  Logger::instance().log(LogLevel::INFO,  __VA_ARGS__)
#define LOG_WARN(...)  Logger::instance().log(LogLevel::WARNING, __VA_ARGS__)
#define LOG_ERROR(...) Logger::instance().log(LogLevel::ERROR, __VA_ARGS__)

int main() {
    Logger::instance().setLevel(LogLevel::INFO);
    std::vector<std::thread> ts;
    for (int i = 0; i < 4; ++i) {
        ts.emplace_back([i]{
            for (int j = 0; j < 50; ++j)
                LOG_INFO("线程", i, " 第", j, "条消息");
        });
    }
    for (auto& t : ts) t.join();
}
```

要点：Meyers单例线程安全，异步队列高性能，条件变量高效等待，析构保证日志不丢失。"""),

    ("实现线程池，支持提交任意返回值任务，返回future获取结果，支持动态调整线程数量",
     """实现功能完整的线程池需要仔细设计。

核心组件：
1. 工作线程数组 vector<thread>
2. 任务队列 queue<function<void()>>
3. mutex和condition_variable保护队列
4. atomic<bool>控制线程池停止
5. submit函数返回future

关键问题1：如何处理任意返回类型的任务？
用std::packaged_task包装任务，它能和future关联。但packaged_task是只移动类型，不能直接放入function（要求可拷贝），所以用shared_ptr包装packaged_task，lambda里调用它。

关键问题2：工作线程循环：
- 加锁，wait条件变量（停止标志、队列非空、需要缩容）
- 如果需要缩容，detach当前线程并从workers_中erase
- 如果停止且队列为空，return退出
- 否则取出一个任务，解锁后执行（执行时不能持锁！）

关键问题3：动态调整大小：
- 扩容：直接创建新工作线程加入workers_
- 缩容：设置threadsToReduce_原子变量，notify_all唤醒所有线程，线程醒来发现需要缩容就自行退出

关键问题4：优雅析构：
设置stop_=true，notify_all，然后join所有线程，确保队列中所有任务都执行完。

代码：
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <future>
#include <functional>
#include <atomic>
#include <algorithm>

class ThreadPool {
public:
    ThreadPool(size_t n = std::thread::hardware_concurrency())
        : stop_(false), toReduce_(0) {
        if (n == 0) n = 4;
        for (size_t i = 0; i < n; ++i)
            workers_.emplace_back(&ThreadPool::worker, this);
    }

    ~ThreadPool() {
        { std::lock_guard<std::mutex> lk(mtx_); stop_ = true; }
        cv_.notify_all();
        for (auto& w : workers_) if (w.joinable()) w.join();
    }

    template<class F, class... Args>
    auto submit(F&& f, Args&&... args) -> std::future<std::invoke_result_t<F, Args...>> {
        using R = std::invoke_result_t<F, Args...>;
        auto task = std::make_shared<std::packaged_task<R()>>(
            std::bind(std::forward<F>(f), std::forward<Args>(args)...));
        std::future<R> res = task->get_future();
        {
            std::unique_lock<std::mutex> lk(mtx_);
            if (stop_) throw std::runtime_error("submit on stopped pool");
            tasks_.emplace([task]{ (*task)(); });
        }
        cv_.notify_one();
        return res;
    }

    void resize(size_t n) {
        if (n == 0) n = 1;
        std::unique_lock<std::mutex> lk(mtx_);
        size_t cur = workers_.size();
        if (n > cur) {
            for (size_t i = 0; i < n - cur; ++i)
                workers_.emplace_back(&ThreadPool::worker, this);
        } else if (n < cur) {
            toReduce_ = cur - n;
            cv_.notify_all();
        }
    }

    size_t size() {
        std::lock_guard<std::mutex> lk(mtx_);
        return workers_.size();
    }

private:
    void worker() {
        for (;;) {
            std::function<void()> task;
            {
                std::unique_lock<std::mutex> lk(mtx_);
                cv_.wait(lk, [this]{
                    return stop_ || !tasks_.empty() || toReduce_ > 0;
                });
                if (toReduce_ > 0) {
                    --toReduce_;
                    auto id = std::this_thread::get_id();
                    auto it = std::find_if(workers_.begin(), workers_.end(),
                        [id](auto& t){ return t.get_id() == id; });
                    if (it != workers_.end()) { it->detach(); workers_.erase(it); }
                    return;
                }
                if (stop_ && tasks_.empty()) return;
                task = std::move(tasks_.front());
                tasks_.pop();
            }
            task();
        }
    }

    std::vector<std::thread> workers_;
    std::queue<std::function<void()>> tasks_;
    std::mutex mtx_;
    std::condition_variable cv_;
    std::atomic<bool> stop_;
    std::atomic<size_t> toReduce_;
};

int main() {
    ThreadPool pool(4);
    std::vector<std::future<int>> res;
    for (int i = 0; i < 8; ++i)
        res.push_back(pool.submit([i]{
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
            return i*i;
        }));
    for (auto& f : res) std::cout << f.get() << ' ';
    std::cout << "\\nsize: " << pool.size() << "\\n";
    pool.resize(2);
    std::cout << "after resize: " << pool.size() << "\\n";
}
```

要点：shared_ptr解决packaged_task不可拷贝问题，任务执行时提前释放锁提高并发，缩容用原子计数器让线程自行退出。"""),

    ("实现基于TCP的简单HTTP服务器，支持GET请求返回静态文件，多线程并发处理",
     """实现HTTP服务器需要理解HTTP协议和socket编程。

工作流程：
1. WinSock初始化（Windows），创建socket
2. 设置SO_REUSEADDR避免重启端口占用
3. bind绑定端口，listen监听
4. 主循环accept，每连接一个线程处理
5. 读取HTTP请求，解析方法路径
6. 读取静态文件，构造响应发送

关键点1：路径安全，防止目录遍历攻击
如果请求路径是/../../../etc/passwd，会访问web根目录外的文件。解决：lexically_normal归一化路径，检查前缀是否是web根目录。

关键点2：sendAll函数
TCP是流协议，send可能一次发不完所有数据，需要循环直到全部发送完成。

关键点3：URL解码
路径中%20是空格，+也是空格，需要解码。

关键点4：MIME类型
根据扩展名返回正确Content-Type，浏览器才能正确渲染。

代码：
```cpp
#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#else
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
using SOCKET = int;
constexpr SOCKET INVALID_SOCKET = -1;
constexpr int SOCKET_ERROR = -1;
#define closesocket close
#endif

#include <iostream>
#include <fstream>
#include <thread>
#include <sstream>
#include <filesystem>
#include <unordered_map>
#include <mutex>

namespace fs = std::filesystem;
std::mutex coutMtx;

std::string urlDecode(const std::string& s) {
    std::string r;
    for (size_t i = 0; i < s.size(); ++i) {
        if (s[i] == '%' && i+2 < s.size()) {
            int v;
            std::istringstream iss(s.substr(i+1,2));
            if (iss >> std::hex >> v) { r += (char)v; i += 2; continue; }
        }
        r += (s[i] == '+') ? ' ' : s[i];
    }
    return r;
}

std::string getMime(const fs::path& p) {
    static std::unordered_map<std::string,std::string> m = {
        {".html","text/html; charset=utf-8"},{".css","text/css"},
        {".js","application/javascript"},{".json","application/json"},
        {".jpg","image/jpeg"},{".png","image/png"},{".txt","text/plain"}
    };
    auto it = m.find(p.extension().string());
    return it != m.end() ? it->second : "application/octet-stream";
}

bool sendAll(SOCKET s, const char* d, size_t l) {
    while (l > 0) {
        int n = send(s, d, (int)l, 0);
        if (n == SOCKET_ERROR) return false;
        d += n; l -= n;
    }
    return true;
}

void handle(SOCKET client, fs::path root) {
    char buf[8192];
    std::string req;
    while (req.size() < sizeof(buf)-1) {
        int n = recv(client, buf, sizeof(buf)-1, 0);
        if (n <= 0) { closesocket(client); return; }
        buf[n] = 0;
        req += buf;
        if (req.find("\\r\\n\\r\\n") != std::string::npos) break;
    }
    std::istringstream iss(req);
    std::string method, path, ver;
    iss >> method >> path >> ver;

    std::string status, body, ctype = "text/plain";
    if (method != "GET") {
        status = "HTTP/1.1 405 Method Not Allowed";
        body = "Method Not Allowed";
    } else {
        path = urlDecode(path);
        if (path == "/" || path.empty()) path = "/index.html";
        fs::path fp = root / path.substr(1);
        fp = fp.lexically_normal();
        std::string rs = root.string(), fs = fp.string();
        if (fs.substr(0, rs.size()) != rs) {
            status = "HTTP/1.1 403 Forbidden"; body = "Forbidden";
        } else if (!fs::exists(fp) || !fs::is_regular_file(fp)) {
            status = "HTTP/1.1 404 Not Found"; body = "Not Found";
        } else {
            std::ifstream f(fp, std::ios::binary);
            std::ostringstream ss; ss << f.rdbuf();
            body = ss.str(); ctype = getMime(fp);
            status = "HTTP/1.1 200 OK";
        }
    }
    std::ostringstream h;
    h << status << "\\r\\n";
    h << "Content-Type: " << ctype << "\\r\\n";
    h << "Content-Length: " << body.size() << "\\r\\n";
    h << "Connection: close\\r\\n\\r\\n";
    std::string hs = h.str();
    sendAll(client, hs.data(), hs.size());
    if (!body.empty()) sendAll(client, body.data(), body.size());
    closesocket(client);
    std::lock_guard<std::mutex> lk(coutMtx);
    std::cout << method << " " << path << " " << status << "\\n";
}

int main() {
#ifdef _WIN32
    WSADATA wd; WSAStartup(MAKEWORD(2,2), &wd);
#endif
    fs::path root = fs::current_path() / "www";
    fs::create_directories(root);
    std::ofstream(root/"index.html") << "<h1>Hello C++ HTTP!</h1>";

    SOCKET lsock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    int opt = 1;
    setsockopt(lsock, SOL_SOCKET, SO_REUSEADDR, (const char*)&opt, sizeof(opt));
    sockaddr_in addr{};
    addr.sin_family = AF_INET; addr.sin_port = htons(8080);
    addr.sin_addr.s_addr = INADDR_ANY;
    bind(lsock, (sockaddr*)&addr, sizeof(addr));
    listen(lsock, SOMAXCONN);
    std::cout << "Server on http://localhost:8080\\n";
    while (true) {
        sockaddr_in ca; int sz = sizeof(ca);
        SOCKET cs = accept(lsock, (sockaddr*)&ca, &sz);
        if (cs != INVALID_SOCKET)
            std::thread(handle, cs, root).detach();
    }
    closesocket(lsock);
#ifdef _WIN32
    WSACleanup();
#endif
}
```

要点：跨平台socket封装、路径安全检查、sendAll确保数据完整、URL解码、MIME映射。"""),

    ("实现二进制文件读写，读写自定义结构体，处理字节序和内存对齐问题",
     """二进制文件操作需要注意几个容易踩的坑。

坑1：内存对齐
结构体直接write会有padding字节，不同编译器/平台对齐方式不同。解决：#pragma pack(push,1)设置1字节对齐，或者手动序列化每个字段。

坑2：字节序
x86是小端，网络字节序是大端。文件如果要跨平台使用，必须统一字节序（一般用大端即网络字节序）。需要实现16/32/64位整数的字节交换。

坑3：字符串
结构体里的char数组成员是固定长度，注意字符串结束符，不要越界。

设计：
- Endianness检测：用union或检查0x0102的第一个字节
- swap16/swap32字节交换函数
- 读写时检测系统字节序，如果是小端就交换后再写/读
- #pragma pack(push,1)控制对齐

代码：
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <cstdint>
#include <cstring>

#pragma pack(push, 1)
struct Record {
    uint32_t id;
    double score;
    char name[32];
    uint16_t flags;
};
#pragma pack(pop)

bool isLittleEndian() {
    uint16_t x = 0x0102;
    return *(uint8_t*)&x == 0x02;
}

uint16_t swap16(uint16_t x) { return (x>>8)|(x<<8); }
uint32_t swap32(uint32_t x) {
    return ((x&0xFF)<<24)|((x&0xFF00)<<8)|((x&0xFF0000)>>8)|((x&0xFF000000)>>24);
}

void writeRecords(const std::string& fn, const std::vector<Record>& rs) {
    std::ofstream f(fn, std::ios::binary);
    if (!f) throw std::runtime_error("open fail");
    bool needSwap = isLittleEndian();
    for (const auto& r : rs) {
        Record out = r;
        if (needSwap) {
            out.id = swap32(out.id);
            out.flags = swap16(out.flags);
        }
        f.write((const char*)&out, sizeof(out));
    }
}

std::vector<Record> readRecords(const std::string& fn) {
    std::ifstream f(fn, std::ios::binary);
    if (!f) throw std::runtime_error("open fail");
    std::vector<Record> rs;
    bool needSwap = isLittleEndian();
    Record r;
    while (f.read((char*)&r, sizeof(r))) {
        if (needSwap) {
            r.id = swap32(r.id);
            r.flags = swap16(r.flags);
        }
        rs.push_back(r);
    }
    return rs;
}

int main() {
    std::vector<Record> data = {
        {1, 95.5, "Alice", 0x01},
        {2, 88.0, "Bob", 0x02}
    };
    writeRecords("data.bin", data);
    auto loaded = readRecords("data.bin");
    for (const auto& r : loaded) {
        std::cout << r.id << ": " << r.name << " " << r.score << "\\n";
    }
}
```

要点：#pragma pack避免对齐问题，字节序检测和转换保证跨平台，二进制块读写高效。"""),

    ("实现Windows/Linux跨平台文件锁，支持共享锁和排他锁，防止多进程并发写入",
     """文件锁用于协调多进程/多线程对同一文件的并发访问。

Windows用LockFileEx/UnlockFileEx，Linux用fcntl的F_SETLK/F_SETLKW。

锁类型：
- 共享锁（读锁）：多个进程可以同时持有，阻止写锁
- 排他锁（写锁）：只有一个进程能持有，阻止其他任何锁

锁特性：
- 阻塞锁：拿不到锁就等待
- 非阻塞锁：拿不到立即返回错误
- 锁与文件句柄关联：句柄关闭时锁自动释放
- 建议锁：需要所有进程都遵守才有效，不是强制的

设计RAII类：
- 构造函数打开文件
- lock()加锁（共享/排他，阻塞/非阻塞）
- unlock()解锁
- 析构函数自动解锁并关闭文件

代码：
```cpp
#ifdef _WIN32
#include <windows.h>
#else
#include <fcntl.h>
#include <unistd.h>
#endif
#include <iostream>
#include <stdexcept>
#include <string>

class FileLock {
public:
    enum Type { Shared, Exclusive };
    FileLock(const std::string& fn) : fn_(fn), locked_(false) {
#ifdef _WIN32
        h_ = CreateFileA(fn.c_str(), GENERIC_READ|GENERIC_WRITE,
            FILE_SHARE_READ|FILE_SHARE_WRITE, nullptr, OPEN_ALWAYS,
            FILE_ATTRIBUTE_NORMAL, nullptr);
        if (h_ == INVALID_HANDLE_VALUE) throw std::runtime_error("open fail");
#else
        fd_ = open(fn.c_str(), O_RDWR|O_CREAT, 0644);
        if (fd_ == -1) throw std::runtime_error("open fail");
#endif
    }

    void lock(Type t, bool block = true) {
#ifdef _WIN32
        DWORD flags = 0;
        if (t == Exclusive) flags |= LOCKFILE_EXCLUSIVE_LOCK;
        if (!block) flags |= LOCKFILE_FAIL_IMMEDIATELY;
        OVERLAPPED ov = {};
        if (!LockFileEx(h_, flags, 0, MAXDWORD, MAXDWORD, &ov))
            throw std::runtime_error("lock fail");
#else
        struct flock fl = {};
        fl.l_type = (t == Exclusive) ? F_WRLCK : F_RDLCK;
        fl.l_whence = SEEK_SET;
        int cmd = block ? F_SETLKW : F_SETLK;
        if (fcntl(fd_, cmd, &fl) == -1)
            throw std::runtime_error("lock fail");
#endif
        locked_ = true;
    }

    void unlock() {
        if (!locked_) return;
#ifdef _WIN32
        OVERLAPPED ov = {};
        UnlockFileEx(h_, 0, MAXDWORD, MAXDWORD, &ov);
#else
        struct flock fl = {};
        fl.l_type = F_UNLCK; fl.l_whence = SEEK_SET;
        fcntl(fd_, F_SETLK, &fl);
#endif
        locked_ = false;
    }

    ~FileLock() {
        if (locked_) unlock();
#ifdef _WIN32
        if (h_ != INVALID_HANDLE_VALUE) CloseHandle(h_);
#else
        if (fd_ != -1) close(fd_);
#endif
    }
private:
    std::string fn_;
    bool locked_;
#ifdef _WIN32
    HANDLE h_;
#else
    int fd_;
#endif
};

int main() {
    try {
        FileLock lk("test.lock");
        std::cout << " acquiring exclusive lock...\\n";
        lk.lock(FileLock::Exclusive);
        std::cout << "got lock! wait 5 seconds...\\n";
        std::this_thread::sleep_for(std::chrono::seconds(5));
        lk.unlock();
        std::cout << "released\\n";
    } catch (std::exception& e) {
        std::cerr << e.what() << "\\n";
    }
}
```

要点：RAII自动释放，跨平台封装，支持阻塞/非阻塞选项。"""),
]

# 写入前6条作为基础，然后继续添加更多
for instr, out in entries:
    add(instr, out)

print(f"Part 1: {len(data)} entries")

# 继续写入剩余条目到一个完整文件
output_path = "f:/数据集/doubao/cot_data/cpp/cpp_cot_3.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"Written to {output_path}")

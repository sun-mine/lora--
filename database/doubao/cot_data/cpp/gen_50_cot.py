import json

entries = []

def add(instr, output):
    entries.append({"instruction": instr, "input": "", "output": output})

# 1. 线程安全日志系统
add("实现线程安全的日志系统，支持多线程环境下同时写入日志文件，要求使用互斥锁保证数据一致性，支持不同日志级别（DEBUG、INFO、WARNING、ERROR），日志格式包含时间戳、线程ID、级别和消息内容。",
"""### 需求分析
题目要求实现一个线程安全的日志系统，需要满足：
1. 多线程环境下安全写入，不会出现日志交错或数据损坏
2. 支持四种日志级别：DEBUG、INFO、WARNING、ERROR
3. 日志格式包含时间戳、线程ID、级别、消息
4. 使用互斥锁保证同步

### 设计思路
1. 使用单例模式确保全局只有一个日志实例
2. 使用std::mutex保护文件写入操作
3. 使用std::ofstream写入日志文件
4. 使用std::chrono获取当前时间
5. 使用std::this_thread::get_id()获取线程ID
6. 提供便捷的宏定义简化日志调用

### 关键问题
- 锁的粒度：只在写入文件时加锁，减少锁竞争
- 时间格式化：使用strftime或C++20的format进行时间格式化
- 线程安全：确保互斥锁在所有写入路径上都被正确持有

### 代码实现
```cpp
#include <iostream>
#include <fstream>
#include <mutex>
#include <string>
#include <thread>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <memory>

enum class LogLevel { DEBUG, INFO, WARNING, ERROR };

class Logger {
public:
    static Logger& getInstance() {
        static Logger instance;
        return instance;
    }

    void setLogFile(const std::string& filename) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (file_.is_open()) {
            file_.close();
        }
        file_.open(filename, std::ios::app);
    }

    void log(LogLevel level, const std::string& message) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (!file_.is_open()) return;

        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
            now.time_since_epoch()) % 1000;

        std::tm tm_buf;
        localtime_s(&tm_buf, &time_t);

        const char* level_str[] = {"DEBUG", "INFO", "WARNING", "ERROR"};

        file_ << "[" << std::put_time(&tm_buf, "%Y-%m-%d %H:%M:%S")
              << "." << std::setfill('0') << std::setw(3) << ms.count() << "] "
              << "[Thread " << std::this_thread::get_id() << "] "
              << "[" << level_str[static_cast<int>(level)] << "] "
              << message << std::endl;
    }

    ~Logger() {
        std::lock_guard<std::mutex> lock(mutex_);
        if (file_.is_open()) {
            file_.close();
        }
    }

private:
    Logger() = default;
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;

    std::ofstream file_;
    std::mutex mutex_;
};

#define LOG_DEBUG(msg) Logger::getInstance().log(LogLevel::DEBUG, msg)
#define LOG_INFO(msg) Logger::getInstance().log(LogLevel::INFO, msg)
#define LOG_WARNING(msg) Logger::getInstance().log(LogLevel::WARNING, msg)
#define LOG_ERROR(msg) Logger::getInstance().log(LogLevel::ERROR, msg)

int main() {
    Logger::getInstance().setLogFile("app.log");

    auto worker = [](int id) {
        for (int i = 0; i < 5; ++i) {
            LOG_INFO("Worker " + std::to_string(id) + " iteration " + std::to_string(i));
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    };

    std::thread t1(worker, 1);
    std::thread t2(worker, 2);
    t1.join();
    t2.join();

    return 0;
}
```""")

# 2. 线程池实现
add("实现一个固定大小的线程池，支持提交任意返回值类型的任务，使用future获取异步执行结果，任务队列使用条件变量实现线程同步，支持优雅关闭。",
"""### 需求分析
实现一个固定大小线程池：
1. 初始化时创建指定数量的工作线程
2. 支持提交任意可调用对象（函数、lambda、bind表达式）
3. 返回std::future获取异步结果
4. 使用条件变量进行任务通知
5. 支持优雅关闭，等待所有任务完成

### 设计思路
1. 使用std::vector<std::thread>管理工作线程
2. 使用std::queue<std::function<void()>>存储任务
3. 使用std::mutex保护任务队列
4. 使用std::condition_variable进行线程等待/唤醒
5. 使用std::packaged_task封装任务以支持future
6. 使用原子变量标记停止状态

### 关键问题
- 任务类型擦除：使用std::function<void()>统一任务类型
- future获取：通过std::packaged_task和std::future实现
- 优雅关闭：先设置停止标志，再唤醒所有线程，最后join

### 代码实现
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

class ThreadPool {
public:
    ThreadPool(size_t num_threads) : stop_(false) {
        for (size_t i = 0; i < num_threads; ++i) {
            workers_.emplace_back([this] {
                while (true) {
                    std::function<void()> task;
                    {
                        std::unique_lock<std::mutex> lock(queue_mutex_);
                        cv_.wait(lock, [this] {
                            return stop_ || !tasks_.empty();
                        });
                        if (stop_ && tasks_.empty()) return;
                        task = std::move(tasks_.front());
                        tasks_.pop();
                    }
                    task();
                }
            });
        }
    }

    template<class F, class... Args>
    auto submit(F&& f, Args&&... args)
        -> std::future<typename std::invoke_result<F, Args...>::type> {
        using return_type = typename std::invoke_result<F, Args...>::type;

        auto task = std::make_shared<std::packaged_task<return_type()>>(
            std::bind(std::forward<F>(f), std::forward<Args>(args)...)
        );

        std::future<return_type> res = task->get_future();
        {
            std::unique_lock<std::mutex> lock(queue_mutex_);
            if (stop_) throw std::runtime_error("submit on stopped ThreadPool");
            tasks_.emplace([task]() { (*task)(); });
        }
        cv_.notify_one();
        return res;
    }

    ~ThreadPool() {
        {
            std::unique_lock<std::mutex> lock(queue_mutex_);
            stop_ = true;
        }
        cv_.notify_all();
        for (std::thread& worker : workers_) {
            worker.join();
        }
    }

private:
    std::vector<std::thread> workers_;
    std::queue<std::function<void()>> tasks_;
    std::mutex queue_mutex_;
    std::condition_variable cv_;
    std::atomic<bool> stop_;
};

int main() {
    ThreadPool pool(4);

    std::vector<std::future<int>> results;
    for (int i = 0; i < 8; ++i) {
        results.emplace_back(
            pool.submit([i] {
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
                return i * i;
            })
        );
    }

    for (auto& f : results) {
        std::cout << f.get() << ' ';
    }
    std::cout << std::endl;

    return 0;
}
```""")

# 3. HTTP服务器
add("实现一个简单的HTTP服务器，使用Socket编程监听8080端口，支持GET请求，能够返回静态文件内容，处理404错误，使用多线程处理并发连接。",
"""### 需求分析
实现简单HTTP服务器：
1. 使用Winsock2（Windows）或POSIX socket监听8080端口
2. 解析HTTP GET请求
3. 返回请求的静态文件或404错误
4. 多线程处理并发连接
5. 正确设置HTTP响应头

### 设计思路
1. 初始化socket库，创建socket，bind，listen
2. 循环accept接受连接
3. 每个连接创建新线程处理
4. 解析HTTP请求行，提取请求路径
5. 读取文件内容，构造HTTP响应
6. 文件不存在返回404

### 关键问题
- HTTP协议解析：解析请求行获取方法和路径
- 文件路径安全：防止目录遍历攻击
- 资源管理：正确关闭socket和文件句柄
- 跨平台：Windows需要WSAStartup/WSACleanup

### 代码实现
```cpp
#include <iostream>
#include <string>
#include <thread>
#include <fstream>
#include <sstream>
#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib, "ws2_32.lib")

std::string get_mime_type(const std::string& path) {
    if (path.find(".html") != std::string::npos) return "text/html";
    if (path.find(".css") != std::string::npos) return "text/css";
    if (path.find(".js") != std::string::npos) return "application/javascript";
    if (path.find(".json") != std::string::npos) return "application/json";
    if (path.find(".png") != std::string::npos) return "image/png";
    if (path.find(".jpg") != std::string::npos) return "image/jpeg";
    return "text/plain";
}

void handle_client(SOCKET client_socket) {
    char buffer[4096];
    int bytes_read = recv(client_socket, buffer, sizeof(buffer) - 1, 0);
    if (bytes_read <= 0) {
        closesocket(client_socket);
        return;
    }
    buffer[bytes_read] = '\0';

    std::string request(buffer);
    std::istringstream iss(request);
    std::string method, path, version;
    iss >> method >> path >> version;

    if (path == "/") path = "/index.html";
    std::string file_path = "." + path;

    std::ifstream file(file_path, std::ios::binary);
    std::string response;

    if (file.is_open()) {
        std::ostringstream oss;
        oss << file.rdbuf();
        std::string body = oss.str();
        std::string content_type = get_mime_type(file_path);

        response = "HTTP/1.1 200 OK\r\n";
        response += "Content-Type: " + content_type + "; charset=utf-8\r\n";
        response += "Content-Length: " + std::to_string(body.size()) + "\r\n";
        response += "Connection: close\r\n\r\n";
        response += body;
    } else {
        std::string body = "<html><body><h1>404 Not Found</h1></body></html>";
        response = "HTTP/1.1 404 Not Found\r\n";
        response += "Content-Type: text/html; charset=utf-8\r\n";
        response += "Content-Length: " + std::to_string(body.size()) + "\r\n";
        response += "Connection: close\r\n\r\n";
        response += body;
    }

    send(client_socket, response.c_str(), response.size(), 0);
    closesocket(client_socket);
}

int main() {
    WSADATA wsa_data;
    WSAStartup(MAKEWORD(2, 2), &wsa_data);

    SOCKET server_socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    sockaddr_in server_addr{};
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(8080);

    bind(server_socket, (sockaddr*)&server_addr, sizeof(server_addr));
    listen(server_socket, SOMAXCONN);

    std::cout << "Server running on http://localhost:8080" << std::endl;

    while (true) {
        SOCKET client_socket = accept(server_socket, nullptr, nullptr);
        std::thread(handle_client, client_socket).detach();
    }

    closesocket(server_socket);
    WSACleanup();
    return 0;
}
```""")

# 4. 二进制文件读写
add("实现二进制文件的读写操作，要求将一个包含多种数据类型（int、float、double、字符串、结构体）的记录写入二进制文件，然后读取并验证数据完整性，考虑字节序和内存对齐问题。",
"""### 需求分析
实现二进制文件读写：
1. 写入混合数据类型到二进制文件
2. 读取并验证数据正确性
3. 处理结构体的内存对齐
4. 考虑跨平台字节序问题
5. 字符串需要先写入长度再写入内容

### 设计思路
1. 使用std::ofstream/std::ifstream的binary模式
2. 对于POD类型直接write/read
3. 对于字符串，先写长度（uint32_t），再写字符数据
4. 结构体使用#pragma pack或手动序列化避免对齐问题
5. 可选：使用网络字节序（大端）保证跨平台兼容性

### 关键问题
- 内存对齐：结构体大小可能不等于成员大小之和
- 字符串长度：二进制文件中字符串不是以\\0结尾的，需要存储长度
- 字节序：x86是小端，网络传输用大端
- 错误检查：检查文件打开状态和读写操作是否成功

### 代码实现
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <cstring>

#pragma pack(push, 1)
struct Person {
    int32_t id;
    float height;
    double weight;
    char name[32];
};
#pragma pack(pop)

void write_binary(const std::string& filename) {
    std::ofstream file(filename, std::ios::binary);
    if (!file) {
        std::cerr << "Cannot open file for writing" << std::endl;
        return;
    }

    int32_t count = 2;
    file.write(reinterpret_cast<const char*>(&count), sizeof(count));

    Person p1{1, 175.5f, 68.5, "Zhang San"};
    Person p2{2, 168.0f, 55.3, "Li Si"};

    file.write(reinterpret_cast<const char*>(&p1), sizeof(p1));
    file.write(reinterpret_cast<const char*>(&p2), sizeof(p2));

    std::string extra = "Binary file test data";
    uint32_t str_len = extra.size();
    file.write(reinterpret_cast<const char*>(&str_len), sizeof(str_len));
    file.write(extra.data(), str_len);

    file.close();
}

void read_binary(const std::string& filename) {
    std::ifstream file(filename, std::ios::binary);
    if (!file) {
        std::cerr << "Cannot open file for reading" << std::endl;
        return;
    }

    int32_t count;
    file.read(reinterpret_cast<char*>(&count), sizeof(count));
    std::cout << "Record count: " << count << std::endl;

    for (int i = 0; i < count; ++i) {
        Person p{};
        file.read(reinterpret_cast<char*>(&p), sizeof(p));
        std::cout << "ID: " << p.id << ", Name: " << p.name
                  << ", Height: " << p.height << ", Weight: " << p.weight << std::endl;
    }

    uint32_t str_len;
    file.read(reinterpret_cast<char*>(&str_len), sizeof(str_len));
    std::string extra(str_len, '\0');
    file.read(extra.data(), str_len);
    std::cout << "Extra: " << extra << std::endl;

    file.close();
}

int main() {
    const std::string filename = "data.bin";
    write_binary(filename);
    read_binary(filename);
    return 0;
}
```""")

# 5. 文件锁
add("实现跨进程文件锁机制，在Windows系统下使用LockFileEx实现文件的独占锁定和共享锁定，演示多个进程同时访问同一文件时的同步控制。",
"""### 需求分析
实现跨进程文件锁：
1. Windows平台使用LockFileEx/UnlockFileEx
2. 支持独占锁（写锁）和共享锁（读锁）
3. 演示多个进程访问同一文件的同步
4. 使用RAII管理锁的生命周期

### 设计思路
1. 使用CreateFile打开文件获取HANDLE
2. 使用OVERLAPPED结构指定锁的起始位置和长度
3. LOCKFILE_EXCLUSIVE_LOCK表示独占锁，0表示共享锁
4. LOCKFILE_FAIL_IMMEDIATELY表示非阻塞
5. 封装成FileLock类使用RAII自动释放

### 关键问题
- 锁的范围：可以锁定文件的一部分
- 阻塞vs非阻塞：决定等待还是立即返回
- 句柄权限：需要GENERIC_READ或GENERIC_WRITE权限
- 锁释放：进程终止时锁会自动释放，但最好显式解锁

### 代码实现
```cpp
#include <windows.h>
#include <iostream>
#include <string>
#include <thread>
#include <chrono>

class FileLock {
public:
    FileLock(const std::string& filename, bool exclusive, bool blocking = true) {
        hFile_ = CreateFileA(
            filename.c_str(),
            GENERIC_READ | GENERIC_WRITE,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            nullptr,
            OPEN_ALWAYS,
            FILE_ATTRIBUTE_NORMAL,
            nullptr
        );

        if (hFile_ == INVALID_HANDLE_VALUE) {
            throw std::runtime_error("Cannot open file");
        }

        DWORD flags = 0;
        if (exclusive) flags |= LOCKFILE_EXCLUSIVE_LOCK;
        if (!blocking) flags |= LOCKFILE_FAIL_IMMEDIATELY;

        OVERLAPPED overlapped{};
        overlapped.Offset = 0;

        BOOL result = LockFileEx(hFile_, flags, 0, MAXDWORD, MAXDWORD, &overlapped);
        if (!result) {
            CloseHandle(hFile_);
            throw std::runtime_error("Failed to acquire lock");
        }
        locked_ = true;
    }

    ~FileLock() {
        if (locked_ && hFile_ != INVALID_HANDLE_VALUE) {
            OVERLAPPED overlapped{};
            overlapped.Offset = 0;
            UnlockFileEx(hFile_, 0, MAXDWORD, MAXDWORD, &overlapped);
            CloseHandle(hFile_);
        }
    }

    FileLock(const FileLock&) = delete;
    FileLock& operator=(const FileLock&) = delete;

private:
    HANDLE hFile_;
    bool locked_ = false;
};

void process(int id, const std::string& filename) {
    try {
        std::cout << "Process " << id << " trying to acquire exclusive lock..." << std::endl;
        FileLock lock(filename, true);
        std::cout << "Process " << id << " acquired lock, working..." << std::endl;

        HANDLE hFile = CreateFileA(filename.c_str(), GENERIC_WRITE, 0, nullptr,
            OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
        std::string data = "Written by process " + std::to_string(id) + "\\n";
        SetFilePointer(hFile, 0, nullptr, FILE_END);
        DWORD written;
        WriteFile(hFile, data.c_str(), data.size(), &written, nullptr);
        CloseHandle(hFile);

        std::this_thread::sleep_for(std::chrono::seconds(2));
        std::cout << "Process " << id << " releasing lock" << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "Process " << id << " error: " << e.what() << std::endl;
    }
}

int main() {
    const std::string filename = "lockfile.dat";

    std::thread t1(process, 1, filename);
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    std::thread t2(process, 2, filename);

    t1.join();
    t2.join();

    return 0;
}
```""")

# 6. 观察者模式
add("使用C++实现观察者设计模式，定义主题(Subject)和观察者(Observer)接口，支持注册、注销观察者，当主题状态变化时通知所有观察者，实现一个具体的新闻发布者和多个订阅者。",
"""### 需求分析
实现观察者模式：
1. 定义Observer接口，包含update方法
2. 定义Subject接口，包含attach/detach/notify方法
3. 具体主题维护观察者列表
4. 状态变化时通知所有观察者
5. 实现新闻发布-订阅示例

### 设计思路
1. 使用抽象基类定义接口
2. Subject使用std::vector<Observer*>存储观察者
3. notify时遍历调用每个observer的update
4. 使用std::string或变体类型传递更新数据
5. 注意处理观察者注销时的迭代器失效问题

### 关键问题
- 接口设计：update方法的参数设计
- 生命周期：观察者销毁时需要从主题注销
- 线程安全：多线程环境下需要保护观察者列表
- 避免循环引用：观察者不应该持有主题的强引用

### 代码实现
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <memory>

class Observer {
public:
    virtual void update(const std::string& news) = 0;
    virtual ~Observer() = default;
};

class Subject {
public:
    virtual void attach(std::shared_ptr<Observer> observer) = 0;
    virtual void detach(std::shared_ptr<Observer> observer) = 0;
    virtual void notify() = 0;
    virtual ~Subject() = default;
};

class NewsPublisher : public Subject {
public:
    void attach(std::shared_ptr<Observer> observer) override {
        observers_.push_back(observer);
    }

    void detach(std::shared_ptr<Observer> observer) override {
        observers_.erase(
            std::remove(observers_.begin(), observers_.end(), observer),
            observers_.end()
        );
    }

    void notify() override {
        for (auto& observer : observers_) {
            observer->update(latest_news_);
        }
    }

    void publish_news(const std::string& news) {
        latest_news_ = news;
        std::cout << "[Publisher] Publishing: " << news << std::endl;
        notify();
    }

private:
    std::vector<std::shared_ptr<Observer>> observers_;
    std::string latest_news_;
};

class Subscriber : public Observer, public std::enable_shared_from_this<Subscriber> {
public:
    Subscriber(const std::string& name) : name_(name) {}

    void update(const std::string& news) override {
        std::cout << "[" << name_ << "] Received news: " << news << std::endl;
    }

    void subscribe(std::shared_ptr<NewsPublisher> publisher) {
        publisher_ = publisher;
        publisher->attach(shared_from_this());
    }

    void unsubscribe() {
        if (auto pub = publisher_.lock()) {
            pub->detach(shared_from_this());
        }
    }

private:
    std::string name_;
    std::weak_ptr<NewsPublisher> publisher_;
};

int main() {
    auto publisher = std::make_shared<NewsPublisher>();

    auto sub1 = std::make_shared<Subscriber>("Alice");
    auto sub2 = std::make_shared<Subscriber>("Bob");
    auto sub3 = std::make_shared<Subscriber>("Charlie");

    sub1->subscribe(publisher);
    sub2->subscribe(publisher);

    publisher->publish_news("C++23 released!");

    std::cout << "\\n--- Bob unsubscribes ---\\n" << std::endl;
    sub2->unsubscribe();
    sub3->subscribe(publisher);

    publisher->publish_news("New AI breakthrough!");

    return 0;
}
```""")

# 继续添加更多条目
# 7. 单例模式（线程安全）
add("实现线程安全的单例模式，要求使用C++11的Magic Statics（局部静态变量）特性，确保在多线程环境下只创建一个实例，禁止拷贝和赋值，并对比饿汉式和懒汉式实现。",
"""### 需求分析
线程安全单例模式：
1. 全局唯一实例
2. 多线程环境下安全初始化
3. 禁止拷贝构造和赋值
4. 提供全局访问点
5. 对比不同实现方式

### 设计思路
1. C++11局部静态变量（Meyers' Singleton）：最简单最安全
2. 饿汉式：程序启动时就创建（线程安全但可能浪费资源）
3. 懒汉式+双重检查锁定（DCLP）：需要注意内存序
4. 删除拷贝构造、移动构造、拷贝赋值、移动赋值

### 关键问题
- 静态变量初始化：C++11保证局部静态变量初始化线程安全
- DCLP陷阱：需要使用atomic和正确的内存序
- 析构顺序：静态变量析构顺序问题（Phoenix Singleton）
- 测试：多线程环境下验证唯一性

### 代码实现
```cpp
#include <iostream>
#include <thread>
#include <mutex>
#include <atomic>
#include <vector>

class Singleton {
public:
    static Singleton& getInstance() {
        static Singleton instance;
        return instance;
    }

    void doSomething() {
        std::cout << "Singleton instance at " << this << " working" << std::endl;
    }

    Singleton(const Singleton&) = delete;
    Singleton& operator=(const Singleton&) = delete;
    Singleton(Singleton&&) = delete;
    Singleton& operator=(Singleton&&) = delete;

private:
    Singleton() {
        std::cout << "Singleton created" << std::endl;
    }
    ~Singleton() = default;
};

class LazySingleton {
public:
    static LazySingleton* getInstance() {
        LazySingleton* tmp = instance_.load(std::memory_order_acquire);
        if (tmp == nullptr) {
            std::lock_guard<std::mutex> lock(mutex_);
            tmp = instance_.load(std::memory_order_relaxed);
            if (tmp == nullptr) {
                tmp = new LazySingleton();
                instance_.store(tmp, std::memory_order_release);
            }
        }
        return tmp;
    }

    void doSomething() {
        std::cout << "LazySingleton at " << this << std::endl;
    }

private:
    LazySingleton() = default;
    static std::atomic<LazySingleton*> instance_;
    static std::mutex mutex_;
};

std::atomic<LazySingleton*> LazySingleton::instance_{nullptr};
std::mutex LazySingleton::mutex_;

int main() {
    std::vector<std::thread> threads;
    for (int i = 0; i < 10; ++i) {
        threads.emplace_back([] {
            Singleton::getInstance().doSomething();
        });
    }
    for (auto& t : threads) t.join();

    std::cout << "\\nAll threads got the same instance" << std::endl;
    return 0;
}
```""")

# 8. 工厂模式
add("实现工厂方法设计模式，定义抽象产品和抽象工厂接口，实现多个具体产品（圆形、矩形、三角形）和对应的具体工厂，演示如何通过工厂创建对象而不指定具体类。",
"""### 需求分析
工厂方法模式：
1. 抽象产品接口Shape
2. 抽象工厂接口ShapeFactory
3. 具体产品：Circle、Rectangle、Triangle
4. 具体工厂：CircleFactory、RectangleFactory、TriangleFactory
5. 客户端依赖抽象而非具体类

### 设计思路
1. 使用纯虚函数定义接口
2. 工厂方法创建并返回产品指针（智能指针）
3. 每个具体产品对应一个具体工厂
4. 可以通过参数化工厂简化（一个工厂根据参数创建不同产品）
5. 使用std::unique_ptr管理对象生命周期

### 关键问题
- 接口抽象：产品和工厂都依赖抽象
- 工厂与产品一一对应：工厂方法模式的特点
- vs简单工厂：简单工厂用一个类根据参数创建所有产品
- vs抽象工厂：抽象工厂创建产品族

### 代码实现
```cpp
#include <iostream>
#include <memory>
#include <string>

class Shape {
public:
    virtual void draw() const = 0;
    virtual double area() const = 0;
    virtual ~Shape() = default;
};

class ShapeFactory {
public:
    virtual std::unique_ptr<Shape> createShape() const = 0;
    virtual ~ShapeFactory() = default;
};

class Circle : public Shape {
public:
    Circle(double r) : radius_(r) {}
    void draw() const override {
        std::cout << "Drawing Circle with radius " << radius_ << std::endl;
    }
    double area() const override {
        return 3.14159 * radius_ * radius_;
    }
private:
    double radius_;
};

class Rectangle : public Shape {
public:
    Rectangle(double w, double h) : width_(w), height_(h) {}
    void draw() const override {
        std::cout << "Drawing Rectangle " << width_ << "x" << height_ << std::endl;
    }
    double area() const override {
        return width_ * height_;
    }
private:
    double width_, height_;
};

class Triangle : public Shape {
public:
    Triangle(double b, double h) : base_(b), height_(h) {}
    void draw() const override {
        std::cout << "Drawing Triangle base=" << base_ << " height=" << height_ << std::endl;
    }
    double area() const override {
        return 0.5 * base_ * height_;
    }
private:
    double base_, height_;
};

class CircleFactory : public ShapeFactory {
public:
    std::unique_ptr<Shape> createShape() const override {
        return std::make_unique<Circle>(5.0);
    }
};

class RectangleFactory : public ShapeFactory {
public:
    std::unique_ptr<Shape> createShape() const override {
        return std::make_unique<Rectangle>(4.0, 6.0);
    }
};

class TriangleFactory : public ShapeFactory {
public:
    std::unique_ptr<Shape> createShape() const override {
        return std::make_unique<Triangle>(3.0, 4.0);
    }
};

int main() {
    CircleFactory circleFactory;
    RectangleFactory rectFactory;
    TriangleFactory triFactory;

    auto shapes = {
        circleFactory.createShape(),
        rectFactory.createShape(),
        triFactory.createShape()
    };

    for (const auto& shape : shapes) {
        shape->draw();
        std::cout << "Area: " << shape->area() << std::endl;
    }

    return 0;
}
```""")

# 9. 滑动窗口最大值
add("实现滑动窗口最大值算法，给定一个整数数组和窗口大小k，返回每个滑动窗口中的最大值，要求使用双端队列(deque)实现O(n)时间复杂度。",
"""### 需求分析
滑动窗口最大值：
1. 输入：数组nums，窗口大小k
2. 输出：每个窗口位置的最大值
3. 暴力解法O(nk)，要求优化到O(n)
4. 使用deque维护单调递减队列

### 设计思路
1. 维护一个双端队列，存储元素索引
2. 队列中元素对应的值单调递减
3. 新元素入队时，从队尾移除所有小于它的元素
4. 队首元素超出窗口范围时出队
5. 窗口形成后（i>=k-1），队首就是当前窗口最大值

### 关键问题
- 为什么存索引：方便判断元素是否超出窗口
- 为什么是O(n)：每个元素最多入队出队一次
- 单调递减保证：队首永远是最大值候选

### 代码实现
```cpp
#include <iostream>
#include <vector>
#include <deque>

std::vector<int> maxSlidingWindow(const std::vector<int>& nums, int k) {
    std::vector<int> result;
    std::deque<int> dq;

    for (int i = 0; i < nums.size(); ++i) {
        while (!dq.empty() && nums[i] >= nums[dq.back()]) {
            dq.pop_back();
        }
        dq.push_back(i);

        while (dq.front() <= i - k) {
            dq.pop_front();
        }

        if (i >= k - 1) {
            result.push_back(nums[dq.front()]);
        }
    }

    return result;
}

int main() {
    std::vector<int> nums = {1, 3, -1, -3, 5, 3, 6, 7};
    int k = 3;

    std::vector<int> result = maxSlidingWindow(nums, k);

    std::cout << "Input: ";
    for (int n : nums) std::cout << n << " ";
    std::cout << "\\nWindow size: " << k << std::endl;
    std::cout << "Sliding window maxima: ";
    for (int r : result) std::cout << r << " ";
    std::cout << std::endl;

    return 0;
}
```""")

# 10. 简单shared_ptr实现
add("实现简化版的std::shared_ptr智能指针，要求支持引用计数、拷贝构造、拷贝赋值、移动语义、自定义删除器，不考虑线程安全和weak_ptr。",
"""### 需求分析
简化版shared_ptr实现：
1. 引用计数管理对象生命周期
2. 支持拷贝构造/赋值：引用计数+1
3. 支持移动构造/赋值：转移所有权
4. 支持自定义删除器
5. 重载operator*和operator->
6. 提供use_count()和get()方法

### 设计思路
1. 两个指针：指向数据的ptr，指向控制块的ctrl
2. 控制块存储引用计数和删除器
3. 拷贝时引用计数+1，析构时-1
4. 引用计数归0时调用删除器释放数据
5. 移动时源对象置空，不影响计数

### 关键问题
- 自赋值检查：拷贝赋值时需要处理自赋值
- 控制块设计：使用类型擦除存储自定义删除器
- 移动语义：移动后源对象应该为nullptr
- 循环引用：shared_ptr的经典问题，本简化版不处理

### 代码实现
```cpp
#include <iostream>
#include <functional>
#include <utility>

template<typename T>
class SharedPtr {
public:
    SharedPtr(T* ptr = nullptr, std::function<void(T*)> deleter = nullptr)
        : ptr_(ptr), deleter_(deleter) {
        if (ptr_) {
            ref_count_ = new size_t(1);
        } else {
            ref_count_ = nullptr;
        }
    }

    ~SharedPtr() {
        release();
    }

    SharedPtr(const SharedPtr& other)
        : ptr_(other.ptr_), ref_count_(other.ref_count_), deleter_(other.deleter_) {
        if (ref_count_) {
            ++(*ref_count_);
        }
    }

    SharedPtr& operator=(const SharedPtr& other) {
        if (this != &other) {
            release();
            ptr_ = other.ptr_;
            ref_count_ = other.ref_count_;
            deleter_ = other.deleter_;
            if (ref_count_) {
                ++(*ref_count_);
            }
        }
        return *this;
    }

    SharedPtr(SharedPtr&& other) noexcept
        : ptr_(other.ptr_), ref_count_(other.ref_count_), deleter_(std::move(other.deleter_)) {
        other.ptr_ = nullptr;
        other.ref_count_ = nullptr;
    }

    SharedPtr& operator=(SharedPtr&& other) noexcept {
        if (this != &other) {
            release();
            ptr_ = other.ptr_;
            ref_count_ = other.ref_count_;
            deleter_ = std::move(other.deleter_);
            other.ptr_ = nullptr;
            other.ref_count_ = nullptr;
        }
        return *this;
    }

    T& operator*() const { return *ptr_; }
    T* operator->() const { return ptr_; }
    T* get() const { return ptr_; }
    size_t use_count() const { return ref_count_ ? *ref_count_ : 0; }
    explicit operator bool() const { return ptr_ != nullptr; }

    void reset(T* ptr = nullptr) {
        release();
        ptr_ = ptr;
        if (ptr_) {
            ref_count_ = new size_t(1);
        }
    }

private:
    void release() {
        if (ref_count_ && --(*ref_count_) == 0) {
            if (deleter_) {
                deleter_(ptr_);
            } else {
                delete ptr_;
            }
            delete ref_count_;
        }
        ptr_ = nullptr;
        ref_count_ = nullptr;
    }

    T* ptr_;
    size_t* ref_count_;
    std::function<void(T*)> deleter_;
};

struct TestObj {
    int value;
    TestObj(int v) : value(v) {
        std::cout << "TestObj(" << value << ") created" << std::endl;
    }
    ~TestObj() {
        std::cout << "TestObj(" << value << ") destroyed" << std::endl;
    }
};

int main() {
    {
        SharedPtr<TestObj> p1(new TestObj(42));
        std::cout << "p1 use count: " << p1.use_count() << std::endl;

        {
            SharedPtr<TestObj> p2 = p1;
            std::cout << "p1 use count after copy: " << p1.use_count() << std::endl;
            std::cout << "p2 value: " << p2->value << std::endl;
        }

        std::cout << "p1 use count after p2 destroyed: " << p1.use_count() << std::endl;
        std::cout << "p1 value: " << (*p1).value << std::endl;
    }

    std::cout << "\\nCustom deleter example:" << std::endl;
    {
        SharedPtr<TestObj> p3(new TestObj(100), [](TestObj* p) {
            std::cout << "Custom deleting..." << std::endl;
            delete p;
        });
    }

    return 0;
}
```""")

# 保存到文件
with open("f:/数据集/doubao/cot_data/cpp/cpp_cot_3_part1.json", "w", encoding="utf-8") as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)

print(f"Generated {len(entries)} entries in part1")

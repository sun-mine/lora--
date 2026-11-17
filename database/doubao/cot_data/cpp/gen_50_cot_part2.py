import json

entries = []

def add(instr, output):
    entries.append({"instruction": instr, "input": "", "output": output})

# 11. 生产者消费者模型
add("实现经典的生产者-消费者模型，使用一个固定大小的缓冲区，多个生产者线程生产数据放入缓冲区，多个消费者线程从缓冲区取出数据消费，使用条件变量实现线程同步，防止缓冲区溢出或下溢。",
"""### 需求分析
生产者消费者模型：
1. 固定大小的循环缓冲区（队列）
2. 多个生产者线程put数据
3. 多个消费者线程take数据
4. 缓冲区满时生产者等待
5. 缓冲区空时消费者等待
6. 使用mutex+condition_variable同步

### 设计思路
1. 使用std::queue作为缓冲区，size_t capacity限制大小
2. std::mutex保护队列操作
3. 两个条件变量：not_full_和not_empty_
4. 生产者：wait not_full，push，notify not_empty
5. 消费者：wait not_empty，pop，notify not_full
6. 使用std::atomic<bool>标记停止生产

### 关键问题
- 虚假唤醒：wait必须使用predicate形式
- notify选择：notify_one还是notify_all（单生产者单消费者用one，多用all）
- 优雅关闭：设置stop标志后需要notify所有等待线程
- 锁的持有时间：notify可以在锁外执行减少竞争

### 代码实现
```cpp
#include <iostream>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <vector>

template<typename T>
class BoundedBuffer {
public:
    BoundedBuffer(size_t capacity) : capacity_(capacity) {}

    void put(T item) {
        std::unique_lock<std::mutex> lock(mutex_);
        not_full_.wait(lock, [this] { return queue_.size() < capacity_ || stop_; });
        if (stop_) return;
        queue_.push(std::move(item));
        lock.unlock();
        not_empty_.notify_one();
    }

    bool take(T& item) {
        std::unique_lock<std::mutex> lock(mutex_);
        not_empty_.wait(lock, [this] { return !queue_.empty() || stop_; });
        if (stop_ && queue_.empty()) return false;
        item = std::move(queue_.front());
        queue_.pop();
        lock.unlock();
        not_full_.notify_one();
        return true;
    }

    void stop() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            stop_ = true;
        }
        not_full_.notify_all();
        not_empty_.notify_all();
    }

private:
    std::queue<T> queue_;
    size_t capacity_;
    std::mutex mutex_;
    std::condition_variable not_full_;
    std::condition_variable not_empty_;
    bool stop_ = false;
};

int main() {
    BoundedBuffer<int> buffer(10);
    std::atomic<int> produced{0};
    std::atomic<int> consumed{0};

    auto producer = [&](int id) {
        for (int i = 0; i < 20; ++i) {
            int item = id * 100 + i;
            buffer.put(item);
            produced++;
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    };

    auto consumer = [&](int id) {
        int item;
        while (buffer.take(item)) {
            std::cout << "Consumer " << id << " got: " << item << std::endl;
            consumed++;
            std::this_thread::sleep_for(std::chrono::milliseconds(20));
        }
    };

    std::vector<std::thread> producers;
    std::vector<std::thread> consumers;
    for (int i = 0; i < 2; ++i) producers.emplace_back(producer, i);
    for (int i = 0; i < 3; ++i) consumers.emplace_back(consumer, i);

    for (auto& t : producers) t.join();
    buffer.stop();
    for (auto& t : consumers) t.join();

    std::cout << "Produced: " << produced << ", Consumed: " << consumed << std::endl;
    return 0;
}
```""")

# 12. 读写锁
add("使用std::shared_mutex实现读写锁机制，允许多个线程同时读共享数据，但写操作必须独占访问。实现一个线程安全的键值存储，支持并发读和独占写，对比读写锁和普通互斥锁的性能差异。",
"""### 需求分析
读写锁实现：
1. 多个读者可以同时持有锁
2. 写者必须独占锁
3. 读者和写者互斥
4. 实现线程安全的KV存储
5. 演示读写锁的使用场景

### 设计思路
1. 使用std::shared_mutex（C++17）
2. 读操作使用std::shared_lock（共享锁）
3. 写操作使用std::unique_lock（独占锁）
4. 用std::unordered_map作为存储
5. 封装get/set/remove方法

### 关键问题
- 锁的升级/降级：shared_mutex不支持直接升级，需要先解锁再加锁
- 写者饥饿：多个读者可能导致写者长时间等待（可以用公平锁解决）
- 适用场景：读多写少的时候性能提升明显
- RAII锁：使用lock_guard/shared_lock/unique_lock自动管理

### 代码实现
```cpp
#include <iostream>
#include <unordered_map>
#include <string>
#include <shared_mutex>
#include <thread>
#include <vector>
#include <chrono>

template<typename K, typename V>
class ThreadSafeMap {
public:
    std::optional<V> get(const K& key) {
        std::shared_lock<std::shared_mutex> lock(mutex_);
        auto it = map_.find(key);
        if (it != map_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

    void set(const K& key, V value) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        map_[key] = std::move(value);
    }

    bool remove(const K& key) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        return map_.erase(key) > 0;
    }

    size_t size() {
        std::shared_lock<std::shared_mutex> lock(mutex_);
        return map_.size();
    }

private:
    std::unordered_map<K, V> map_;
    mutable std::shared_mutex mutex_;
};

int main() {
    ThreadSafeMap<std::string, int> scores;
    scores.set("Alice", 95);
    scores.set("Bob", 87);
    scores.set("Charlie", 92);

    auto reader = [&](int id) {
        for (int i = 0; i < 100; ++i) {
            auto alice = scores.get("Alice");
            if (alice) {
                std::cout << "Reader " << id << ": Alice=" << *alice << std::endl;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(5));
        }
    };

    auto writer = [&](int id) {
        for (int i = 0; i < 10; ++i) {
            scores.set("Writer" + std::to_string(id), i);
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }
    };

    std::vector<std::thread> threads;
    for (int i = 0; i < 4; ++i) threads.emplace_back(reader, i);
    for (int i = 0; i < 2; ++i) threads.emplace_back(writer, i);

    for (auto& t : threads) t.join();

    std::cout << "Final size: " << scores.size() << std::endl;
    return 0;
}
```""")

# 13. 无锁栈
add("实现一个无锁（Lock-Free）栈数据结构，使用std::atomic原子操作和compare_exchange_weak实现push和pop操作，不使用任何互斥锁，确保在多线程环境下的线程安全。",
"""### 需求分析
无锁栈：
1. 不使用mutex/lock
2. 使用原子操作实现线程安全
3. CAS（Compare-And-Swap）操作
4. 支持多生产者多消费者
5. 避免内存泄漏（使用节点引用计数/危险指针）

### 设计思路
1. 链表实现栈，head是原子指针
2. push：创建新节点，CAS循环将head改为新节点
3. pop：CAS循环将head移到next，返回原head节点
4. 本简化版暂不处理ABA问题和内存回收
5. 使用compare_exchange_weak在循环中重试

### 关键问题
- ABA问题：线程1读head=A，被切换；线程2 pop A，push B，push A；线程1恢复CAS成功但数据结构可能已损坏
- 内存回收：pop的节点不能立即delete，可能还有其他线程在访问
- memory order：需要正确的内存序保证可见性
- CAS循环：compare_exchange失败时需要重读expected值

### 代码实现
```cpp
#include <iostream>
#include <atomic>
#include <thread>
#include <vector>

template<typename T>
class LockFreeStack {
private:
    struct Node {
        T data;
        Node* next;
        Node(const T& d) : data(d), next(nullptr) {}
    };

    std::atomic<Node*> head_{nullptr};

public:
    void push(const T& data) {
        Node* new_node = new Node(data);
        new_node->next = head_.load(std::memory_order_relaxed);
        while (!head_.compare_exchange_weak(
            new_node->next, new_node,
            std::memory_order_release, std::memory_order_relaxed)) {
        }
    }

    bool pop(T& result) {
        Node* old_head = head_.load(std::memory_order_relaxed);
        while (old_head && !head_.compare_exchange_weak(
            old_head, old_head->next,
            std::memory_order_acquire, std::memory_order_relaxed)) {
        }
        if (!old_head) return false;
        result = old_head->data;
        delete old_head;
        return true;
    }

    ~LockFreeStack() {
        T dummy;
        while (pop(dummy));
    }
};

int main() {
    LockFreeStack<int> stack;
    std::atomic<int> push_count{0};
    std::atomic<int> pop_count{0};

    auto pusher = [&]() {
        for (int i = 0; i < 1000; ++i) {
            stack.push(i);
            push_count++;
        }
    };

    auto popper = [&]() {
        int val;
        for (int i = 0; i < 1000; ++i) {
            if (stack.pop(val)) {
                pop_count++;
            } else {
                std::this_thread::yield();
                i--;
            }
        }
    };

    std::vector<std::thread> threads;
    for (int i = 0; i < 2; ++i) threads.emplace_back(pusher);
    for (int i = 0; i < 2; ++i) threads.emplace_back(popper);
    for (auto& t : threads) t.join();

    std::cout << "Pushed: " << push_count << ", Popped: " << pop_count << std::endl;
    return 0;
}
```""")

# 14. 策略模式
add("实现策略设计模式，定义抽象策略接口，实现多种具体策略（加法、减法、乘法、除法），创建上下文类使用不同策略执行计算，支持运行时动态切换策略。",
"""### 需求分析
策略模式：
1. 抽象策略接口：计算方法
2. 具体策略：加、减、乘、除
3. 上下文类持有策略引用
4. 运行时可切换策略
5. 客户端选择策略传给上下文

### 设计思路
1. Strategy抽象基类，纯虚函数execute
2. AddStrategy/SubtractStrategy等具体策略
3. Calculator上下文类，setStrategy切换策略
4. 使用std::unique_ptr管理策略对象生命周期
5. 主函数演示动态切换策略

### 关键问题
- 接口粒度：execute参数要足够通用
- 策略生命周期：上下文是否拥有策略
- vs状态模式：结构相似但意图不同（策略是选择算法，状态是状态切换行为）
- 消除条件分支：用策略对象替代if-else/switch

### 代码实现
```cpp
#include <iostream>
#include <memory>
#include <string>

class CalculationStrategy {
public:
    virtual double calculate(double a, double b) const = 0;
    virtual std::string name() const = 0;
    virtual ~CalculationStrategy() = default;
};

class AddStrategy : public CalculationStrategy {
public:
    double calculate(double a, double b) const override { return a + b; }
    std::string name() const override { return "Addition"; }
};

class SubtractStrategy : public CalculationStrategy {
public:
    double calculate(double a, double b) const override { return a - b; }
    std::string name() const override { return "Subtraction"; }
};

class MultiplyStrategy : public CalculationStrategy {
public:
    double calculate(double a, double b) const override { return a * b; }
    std::string name() const override { return "Multiplication"; }
};

class DivideStrategy : public CalculationStrategy {
public:
    double calculate(double a, double b) const override {
        if (b == 0) throw std::invalid_argument("Division by zero");
        return a / b;
    }
    std::string name() const override { return "Division"; }
};

class Calculator {
public:
    void setStrategy(std::unique_ptr<CalculationStrategy> s) {
        strategy_ = std::move(s);
    }

    double calculate(double a, double b) const {
        if (!strategy_) throw std::runtime_error("No strategy set");
        std::cout << "Performing " << strategy_->name() << ": ";
        return strategy_->calculate(a, b);
    }

private:
    std::unique_ptr<CalculationStrategy> strategy_;
};

int main() {
    Calculator calc;
    double a = 10, b = 5;

    calc.setStrategy(std::make_unique<AddStrategy>());
    std::cout << calc.calculate(a, b) << std::endl;

    calc.setStrategy(std::make_unique<SubtractStrategy>());
    std::cout << calc.calculate(a, b) << std::endl;

    calc.setStrategy(std::make_unique<MultiplyStrategy>());
    std::cout << calc.calculate(a, b) << std::endl;

    calc.setStrategy(std::make_unique<DivideStrategy>());
    std::cout << calc.calculate(a, b) << std::endl;

    return 0;
}
```""")

# 15. 装饰器模式
add("实现装饰器设计模式，为咖啡饮品对象动态添加配料（牛奶、糖、摩卡、奶泡），每个配料装饰器计算价格和描述，支持自由组合配料，对比继承和装饰器的灵活性差异。",
"""### 需求分析
装饰器模式：
1. 抽象组件：Coffee接口（cost、getDescription）
2. 具体组件：Espresso、HouseBlend等基础咖啡
3. 抽象装饰器：继承Coffee，持有Coffee指针
4. 具体装饰器：Milk、Sugar、Mocha、Whip
5. 可以层层包装动态添加功能

### 设计思路
1. Beverage抽象基类，description和cost()
2. 具体饮料类实现基础cost和description
3. CondimentDecorator抽象类继承Beverage，持有Beverage*
4. 每个调料装饰器在父类cost基础上加自己的价格
5. 包装过程：new Mocha(new Milk(new Espresso()))

### 关键问题
- 继承vs组合：装饰器用组合而非继承扩展功能
- 透明性：装饰器和被装饰对象接口一致
- 顺序敏感吗：一般装饰顺序不影响结果但某些情况会
- 装饰器数量过多时的类爆炸：可以用策略/函数式优化

### 代码实现
```cpp
#include <iostream>
#include <memory>
#include <string>

class Beverage {
public:
    virtual std::string getDescription() const = 0;
    virtual double cost() const = 0;
    virtual ~Beverage() = default;
};

class Espresso : public Beverage {
public:
    std::string getDescription() const override { return "Espresso"; }
    double cost() const override { return 1.99; }
};

class HouseBlend : public Beverage {
public:
    std::string getDescription() const override { return "House Blend Coffee"; }
    double cost() const override { return 0.89; }
};

class DarkRoast : public Beverage {
public:
    std::string getDescription() const override { return "Dark Roast Coffee"; }
    double cost() const override { return 0.99; }
};

class CondimentDecorator : public Beverage {
protected:
    std::unique_ptr<Beverage> beverage_;
public:
    CondimentDecorator(std::unique_ptr<Beverage> b) : beverage_(std::move(b)) {}
};

class Milk : public CondimentDecorator {
public:
    Milk(std::unique_ptr<Beverage> b) : CondimentDecorator(std::move(b)) {}
    std::string getDescription() const override {
        return beverage_->getDescription() + ", Milk";
    }
    double cost() const override { return beverage_->cost() + 0.30; }
};

class Mocha : public CondimentDecorator {
public:
    Mocha(std::unique_ptr<Beverage> b) : CondimentDecorator(std::move(b)) {}
    std::string getDescription() const override {
        return beverage_->getDescription() + ", Mocha";
    }
    double cost() const override { return beverage_->cost() + 0.20; }
};

class Whip : public CondimentDecorator {
public:
    Whip(std::unique_ptr<Beverage> b) : CondimentDecorator(std::move(b)) {}
    std::string getDescription() const override {
        return beverage_->getDescription() + ", Whip";
    }
    double cost() const override { return beverage_->cost() + 0.10; }
};

class Sugar : public CondimentDecorator {
public:
    Sugar(std::unique_ptr<Beverage> b) : CondimentDecorator(std::move(b)) {}
    std::string getDescription() const override {
        return beverage_->getDescription() + ", Sugar";
    }
    double cost() const override { return beverage_->cost() + 0.05; }
};

int main() {
    std::unique_ptr<Beverage> drink1 = std::make_unique<Espresso>();
    std::cout << drink1->getDescription() << " $" << drink1->cost() << std::endl;

    std::unique_ptr<Beverage> drink2 = std::make_unique<DarkRoast>();
    drink2 = std::make_unique<Mocha>(std::move(drink2));
    drink2 = std::make_unique<Mocha>(std::move(drink2));
    drink2 = std::make_unique<Whip>(std::move(drink2));
    std::cout << drink2->getDescription() << " $" << drink2->cost() << std::endl;

    std::unique_ptr<Beverage> drink3 = std::make_unique<HouseBlend>();
    drink3 = std::make_unique<Milk>(std::move(drink3));
    drink3 = std::make_unique<Mocha>(std::move(drink3));
    drink3 = std::make_unique<Whip>(std::move(drink3));
    drink3 = std::make_unique<Sugar>(std::move(drink3));
    std::cout << drink3->getDescription() << " $" << drink3->cost() << std::endl;

    return 0;
}
```""")

# 16. TCP客户端
add("实现TCP客户端程序，连接到指定的服务器IP和端口，发送数据并接收响应，处理连接失败、发送超时等异常情况，支持非阻塞模式和异步连接。",
"""### 需求分析
TCP客户端：
1. 建立TCP连接到服务器
2. 发送HTTP请求或自定义协议数据
3. 接收服务器响应
4. 处理连接错误和超时
5. Windows平台使用Winsock2

### 设计思路
1. WSAStartup初始化
2. 创建socket，设置超时选项
3. 使用getaddrinfo解析地址
4. connect连接服务器
5. send发送请求，recv接收响应
6. 正确清理资源

### 关键问题
- 阻塞vs非阻塞：默认阻塞模式，可用ioctlsocket设非阻塞
- 超时设置：SO_SNDTIMEO/SO_RCVTIMEO选项
- 错误处理：每个系统调用后检查WSAGetLastError
- 部分发送：send可能只发送部分数据，需要循环发送
- 优雅关闭：shutdown而非直接closesocket

### 代码实现
```cpp
#include <iostream>
#include <string>
#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib, "ws2_32.lib")

bool setSocketTimeout(SOCKET sock, int timeout_ms) {
    DWORD timeout = timeout_ms;
    return setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, (const char*)&timeout, sizeof(timeout)) == 0 &&
           setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, (const char*)&timeout, sizeof(timeout)) == 0;
}

int main() {
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "WSAStartup failed" << std::endl;
        return 1;
    }

    const char* server_ip = "93.184.216.34";
    const char* port = "80";

    addrinfo hints{}, *result = nullptr;
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_protocol = IPPROTO_TCP;

    if (getaddrinfo(server_ip, port, &hints, &result) != 0) {
        std::cerr << "getaddrinfo failed: " << WSAGetLastError() << std::endl;
        WSACleanup();
        return 1;
    }

    SOCKET sock = socket(result->ai_family, result->ai_socktype, result->ai_protocol);
    if (sock == INVALID_SOCKET) {
        std::cerr << "socket creation failed" << std::endl;
        freeaddrinfo(result);
        WSACleanup();
        return 1;
    }

    setSocketTimeout(sock, 5000);

    std::cout << "Connecting to " << server_ip << ":" << port << "..." << std::endl;
    if (connect(sock, result->ai_addr, (int)result->ai_addrlen) == SOCKET_ERROR) {
        std::cerr << "connect failed: " << WSAGetLastError() << std::endl;
        closesocket(sock);
        freeaddrinfo(result);
        WSACleanup();
        return 1;
    }
    std::cout << "Connected!" << std::endl;
    freeaddrinfo(result);

    std::string request = "GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n";
    int sent = send(sock, request.c_str(), request.size(), 0);
    std::cout << "Sent " << sent << " bytes" << std::endl;

    char buffer[4096];
    std::string response;
    int received;
    while ((received = recv(sock, buffer, sizeof(buffer) - 1, 0)) > 0) {
        buffer[received] = '\0';
        response += buffer;
        std::cout << buffer;
    }

    std::cout << "\\nTotal response received: " << response.size() << " bytes" << std::endl;

    closesocket(sock);
    WSACleanup();
    return 0;
}
```""")

# 17. 内存映射文件
add("使用内存映射文件（Memory-Mapped File）读取大文件，在Windows系统下使用CreateFileMapping和MapViewOfFile将文件映射到进程地址空间，像访问内存一样访问文件内容，对比普通文件I/O的性能差异。",
"""### 需求分析
内存映射文件：
1. 将文件映射到虚拟内存地址
2. 通过指针直接读写文件内容
3. 操作系统负责页面调度
4. 适合大文件随机访问
5. 比read/write系统调用减少拷贝

### 设计思路
1. CreateFile打开文件
2. CreateFileMapping创建文件映射对象
3. MapViewOfFile映射到进程地址空间
4. 直接用指针操作内存
5. UnmapViewOfFile、CloseHandle清理

### 关键问题
- 映射粒度：按系统分配粒度（通常64KB）对齐
- 一致性：多个进程映射同一文件共享内存（可用于IPC）
- 写回：修改内存后操作系统会自动写回磁盘（可FlushViewOfFile强制）
- 大文件支持：可以只映射文件的一部分

### 代码实现
```cpp
#include <windows.h>
#include <iostream>
#include <string>
#include <chrono>

int main() {
    const char* filename = "large_file.dat";
    const size_t file_size = 100 * 1024 * 1024;

    HANDLE hFile = CreateFileA(
        filename,
        GENERIC_READ | GENERIC_WRITE,
        0,
        nullptr,
        CREATE_ALWAYS,
        FILE_ATTRIBUTE_NORMAL,
        nullptr
    );

    if (hFile == INVALID_HANDLE_VALUE) {
        std::cerr << "CreateFile failed" << std::endl;
        return 1;
    }

    LARGE_INTEGER liSize;
    liSize.QuadPart = file_size;
    SetFilePointerEx(hFile, liSize, nullptr, FILE_BEGIN);
    SetEndOfFile(hFile);

    HANDLE hMap = CreateFileMappingA(
        hFile,
        nullptr,
        PAGE_READWRITE,
        0, 0,
        nullptr
    );

    if (!hMap) {
        std::cerr << "CreateFileMapping failed" << std::endl;
        CloseHandle(hFile);
        return 1;
    }

    auto start = std::chrono::high_resolution_clock::now();

    char* data = (char*)MapViewOfFile(hMap, FILE_MAP_ALL_ACCESS, 0, 0, file_size);
    if (!data) {
        std::cerr << "MapViewOfFile failed" << std::endl;
        CloseHandle(hMap);
        CloseHandle(hFile);
        return 1;
    }

    for (size_t i = 0; i < file_size; ++i) {
        data[i] = (char)(i % 256);
    }

    size_t checksum = 0;
    for (size_t i = 0; i < file_size; ++i) {
        checksum += (unsigned char)data[i];
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

    std::cout << "Memory-mapped I/O completed in " << ms.count() << "ms" << std::endl;
    std::cout << "Checksum: " << checksum << std::endl;

    UnmapViewOfFile(data);
    CloseHandle(hMap);
    CloseHandle(hFile);

    DeleteFileA(filename);
    return 0;
}
```""")

# 18. 适配器模式
add("实现适配器设计模式，将一个旧的矩形绘图接口（LegacyRectangle）适配到新的Shape接口，让原本不兼容的接口可以一起工作，演示类适配器（继承）和对象适配器（组合）两种实现方式。",
"""### 需求分析
适配器模式：
1. 目标接口：Shape（draw, getArea）
2. 适配者：LegacyRectangle（display, calculateArea）
3. 适配器：将LegacyRectangle接口转换为Shape接口
4. 类适配器：多重继承
5. 对象适配器：组合方式（推荐）

### 设计思路
1. 定义新系统使用的Shape接口
2. 遗留类LegacyRectangle接口不兼容
3. RectangleAdapter继承Shape，持有（或继承）LegacyRectangle
4. 在适配器方法中调用遗留对象的方法
5. 客户端只依赖Shape接口

### 关键问题
- 类适配器vs对象适配器：类适配器用继承，适配器不能适配子类；对象适配器用组合，更灵活
- 双向适配器：可以同时实现两个接口支持双方使用
- 适配器vs装饰器：适配器改变接口，装饰器增强功能不改变接口
- 默认适配器：为接口提供默认实现，子类只覆盖需要的方法

### 代码实现
```cpp
#include <iostream>
#include <memory>

class Shape {
public:
    virtual void draw() const = 0;
    virtual double getArea() const = 0;
    virtual ~Shape() = default;
};

class LegacyRectangle {
public:
    LegacyRectangle(int x1, int y1, int x2, int y2)
        : x1_(x1), y1_(y1), x2_(x2), y2_(y2) {}

    void display() const {
        std::cout << "LegacyRectangle: (" << x1_ << "," << y1_ << ") -> ("
                  << x2_ << "," << y2_ << ")" << std::endl;
    }

    int calculateArea() const {
        return abs((x2_ - x1_) * (y2_ - y1_));
    }

private:
    int x1_, y1_, x2_, y2_;
};

class RectangleAdapter : public Shape {
public:
    RectangleAdapter(int x, int y, int w, int h)
        : legacy_rect_(x, y, x + w, y + h) {}

    void draw() const override {
        legacy_rect_.display();
    }

    double getArea() const override {
        return legacy_rect_.calculateArea();
    }

private:
    LegacyRectangle legacy_rect_;
};

class Circle : public Shape {
public:
    Circle(int cx, int cy, int r) : cx_(cx), cy_(cy), r_(r) {}
    void draw() const override {
        std::cout << "Circle at (" << cx_ << "," << cy_ << ") radius " << r_ << std::endl;
    }
    double getArea() const override {
        return 3.14159 * r_ * r_;
    }
private:
    int cx_, cy_, r_;
};

void drawShape(const Shape& shape) {
    shape.draw();
    std::cout << "Area: " << shape.getArea() << std::endl;
}

int main() {
    Circle circle(0, 0, 5);
    RectangleAdapter rect(10, 10, 20, 30);

    std::cout << "=== Drawing shapes uniformly ===" << std::endl;
    drawShape(circle);
    std::cout << std::endl;
    drawShape(rect);

    return 0;
}
```""")

# 19. 命令模式
add("实现命令设计模式，将请求封装为对象，支持撤销操作、命令日志、宏命令（多个命令组合）。实现一个简单的文本编辑器，支持插入、删除、撤销、重做功能。",
"""### 需求分析
命令模式：
1. Command接口：execute, undo
2. 具体命令：InsertCommand, DeleteCommand
3. 接收者：Document（实际执行操作）
4. 调用者：Editor/CommandQueue
5. 支持undo/redo历史栈
6. 宏命令组合多个命令

### 设计思路
1. Command抽象类，execute和undo纯虚函数
2. Document类保存文本，提供insert/remove方法
3. 每个具体命令保存执行时的状态以便撤销
4. 历史栈保存已执行命令（undo），重做栈保存被撤销命令（redo）
5. 执行新命令时清空redo栈

### 关键问题
- 保存什么状态：命令需要足够信息undo（插入位置、内容、长度）
- 深拷贝vs快照：保存前状态还是反向操作
- 异常安全：execute失败时不应该入栈
- 宏命令：MacroCommand实现Command接口，内部持有vector<CommandPtr>，依次执行/撤销

### 代码实现
```cpp
#include <iostream>
#include <string>
#include <stack>
#include <memory>
#include <vector>

class Document {
public:
    void insert(size_t pos, const std::string& text) {
        if (pos > content_.size()) pos = content_.size();
        content_.insert(pos, text);
    }

    void remove(size_t pos, size_t len) {
        if (pos >= content_.size()) return;
        len = std::min(len, content_.size() - pos);
        content_.erase(pos, len);
    }

    const std::string& getContent() const { return content_; }

private:
    std::string content_;
};

class Command {
public:
    virtual void execute(Document& doc) = 0;
    virtual void undo(Document& doc) = 0;
    virtual ~Command() = default;
};

class InsertCommand : public Command {
public:
    InsertCommand(size_t pos, std::string text) : pos_(pos), text_(std::move(text)) {}
    void execute(Document& doc) override { doc.insert(pos_, text_); }
    void undo(Document& doc) override { doc.remove(pos_, text_.size()); }
private:
    size_t pos_;
    std::string text_;
};

class DeleteCommand : public Command {
public:
    DeleteCommand(size_t pos, size_t len) : pos_(pos), len_(len) {}
    void execute(Document& doc) override {
        saved_text_ = doc.getContent().substr(pos_, len_);
        doc.remove(pos_, len_);
    }
    void undo(Document& doc) override { doc.insert(pos_, saved_text_); }
private:
    size_t pos_, len_;
    std::string saved_text_;
};

class Editor {
public:
    Editor(Document& doc) : doc_(doc) {}

    void executeCommand(std::unique_ptr<Command> cmd) {
        cmd->execute(doc_);
        undo_stack_.push(std::move(cmd));
        while (!redo_stack_.empty()) redo_stack_.pop();
    }

    void undo() {
        if (undo_stack_.empty()) return;
        auto cmd = std::move(undo_stack_.top());
        undo_stack_.pop();
        cmd->undo(doc_);
        redo_stack_.push(std::move(cmd));
    }

    void redo() {
        if (redo_stack_.empty()) return;
        auto cmd = std::move(redo_stack_.top());
        redo_stack_.pop();
        cmd->execute(doc_);
        undo_stack_.push(std::move(cmd));
    }

    void print() const {
        std::cout << "Content: \"" << doc_.getContent() << "\"" << std::endl;
    }

private:
    Document& doc_;
    std::stack<std::unique_ptr<Command>> undo_stack_;
    std::stack<std::unique_ptr<Command>> redo_stack_;
};

int main() {
    Document doc;
    Editor editor(doc);

    std::cout << "=== Inserting text ===" << std::endl;
    editor.executeCommand(std::make_unique<InsertCommand>(0, "Hello World"));
    editor.print();

    editor.executeCommand(std::make_unique<InsertCommand>(5, ", C++"));
    editor.print();

    std::cout << "\\n=== Undo ===" << std::endl;
    editor.undo();
    editor.print();

    std::cout << "\\n=== Redo ===" << std::endl;
    editor.redo();
    editor.print();

    std::cout << "\\n=== Delete then undo ===" << std::endl;
    editor.executeCommand(std::make_unique<DeleteCommand>(5, 5));
    editor.print();
    editor.undo();
    editor.print();

    return 0;
}
```""")

# 20. UDP广播
add("实现UDP广播发送和接收程序，使用setsockopt启用SO_BROADCAST选项，向局域网广播消息，接收端监听指定端口接收广播数据报，实现一个简单的局域网消息广播系统。",
"""### 需求分析
UDP广播：
1. 无连接的数据报通信
2. 发送到广播地址（255.255.255.255或子网广播）
3. 同一局域网所有主机都能收到
4. 不需要知道接收者IP
5. 使用SOCK_DGRAM类型socket

### 设计思路
1. 发送端：创建UDP socket，设置SO_BROADCAST选项
2. 构造sockaddr_in为广播地址INADDR_BROADCAST
3. sendto发送数据报到广播地址
4. 接收端：绑定到INADDR_ANY和指定端口
5. recvfrom接收数据，可获取发送者地址

### 关键问题
- 广播vs组播：广播发给整个子网，组播发给特定多播组
- 端口：接收端必须bind到正确端口
- 广播风暴：不要在大网络频繁广播
- 权限：某些系统需要特殊权限发送广播
- 防火墙：可能阻止广播数据包

### 代码实现
```cpp
#include <iostream>
#include <string>
#include <thread>
#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib, "ws2_32.lib")

const int BROADCAST_PORT = 9999;

void receiver() {
    SOCKET sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    BOOL opt = TRUE;
    setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, (const char*)&opt, sizeof(opt));

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(BROADCAST_PORT);
    addr.sin_addr.s_addr = INADDR_ANY;
    bind(sock, (sockaddr*)&addr, sizeof(addr));

    std::cout << "[Receiver] Listening for broadcasts on port " << BROADCAST_PORT << std::endl;

    char buffer[1024];
    sockaddr_in sender_addr{};
    int addr_len = sizeof(sender_addr);
    while (true) {
        int recv_len = recvfrom(sock, buffer, sizeof(buffer) - 1, 0,
                                (sockaddr*)&sender_addr, &addr_len);
        if (recv_len > 0) {
            buffer[recv_len] = '\0';
            char ip_str[INET_ADDRSTRLEN];
            inet_ntop(AF_INET, &sender_addr.sin_addr, ip_str, sizeof(ip_str));
            std::cout << "[Receiver] From " << ip_str << ":" << ntohs(sender_addr.sin_port)
                      << " - " << buffer << std::endl;
        }
    }
    closesocket(sock);
}

void sender() {
    std::this_thread::sleep_for(std::chrono::seconds(1));
    SOCKET sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    BOOL broadcast = TRUE;
    setsockopt(sock, SOL_SOCKET, SO_BROADCAST, (const char*)&broadcast, sizeof(broadcast));

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(BROADCAST_PORT);
    addr.sin_addr.s_addr = INADDR_BROADCAST;

    for (int i = 1; i <= 5; ++i) {
        std::string msg = "Broadcast message #" + std::to_string(i);
        sendto(sock, msg.c_str(), msg.size(), 0, (sockaddr*)&addr, sizeof(addr));
        std::cout << "[Sender] Sent: " << msg << std::endl;
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    closesocket(sock);
}

int main() {
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);

    std::thread recv_thread(receiver);
    recv_thread.detach();

    std::thread send_thread(sender);
    send_thread.join();

    std::this_thread::sleep_for(std::chrono::milliseconds(500));
    WSACleanup();
    return 0;
}
```""")

with open("f:/数据集/doubao/cot_data/cpp/cpp_cot_3_part2.json", "w", encoding="utf-8") as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)

print(f"Generated {len(entries)} entries in part2")

import json
import sys

all_entries = []

def add(instr, output):
    all_entries.append({"instruction": instr, "input": "", "output": output})

# 先读取已生成的部分
parts = [
    "cpp_cot_3_part1.json",
    "cpp_cot_3_part2.json",
    "cpp_cot_3_part3a.json"
]

for p in parts:
    try:
        with open(f"f:/数据集/doubao/cot_data/cpp/{p}", "r", encoding="utf-8") as f:
            data = json.load(f)
            all_entries.extend(data)
            print(f"Loaded {len(data)} from {p}")
    except Exception as e:
        print(f"Could not load {p}: {e}")

# 添加剩余20条
print(f"Have {len(all_entries)} entries so far, adding 20 more...")

# 31. RAII资源管理
add("演示C++ RAII（资源获取即初始化） idiom，实现一个文件句柄管理类、互斥锁守卫类，对比手动管理资源和RAII的差异，演示异常发生时资源的正确释放。",
"""### 需求分析
RAII机制演示：
1. 将资源绑定到对象生命周期
2. 构造时获取资源，析构时释放
3. 异常安全：无论正常还是异常路径都能释放资源
4. 实现文件句柄包装
5. 实现unique_lock风格的锁守卫
6. 对比手动fopen/fclose的问题

### 设计思路
1. FileGuard类：构造打开文件，析构关闭
2. LockGuard类：构造加锁，析构解锁
3. 在可能抛异常的代码中使用RAII对象
4. 演示如果忘记关闭资源的情况
5. 对比C风格手动管理和RAII的区别

### 关键问题
- 对象语义：RAII对象一般不可拷贝（独占资源）
- 移动语义：可以转移所有权
- 异常发生时栈展开：析构函数会被正确调用
- 标准库大量使用RAII：lock_guard、unique_ptr、fstream等

### 代码实现
```cpp
#include <iostream>
#include <stdexcept>
#include <mutex>
#include <string>
#include <windows.h>

class FileHandle {
    HANDLE hFile_;
public:
    FileHandle(const char* path, DWORD access, DWORD create) {
        hFile_ = CreateFileA(path, access, 0, nullptr, create, FILE_ATTRIBUTE_NORMAL, nullptr);
        if (hFile_ == INVALID_HANDLE_VALUE) {
            throw std::runtime_error("Failed to open file");
        }
        std::cout << "[FileHandle] File opened: " << path << std::endl;
    }

    ~FileHandle() {
        if (hFile_ != INVALID_HANDLE_VALUE) {
            CloseHandle(hFile_);
            std::cout << "[FileHandle] File closed automatically" << std::endl;
        }
    }

    HANDLE get() const { return hFile_; }

    FileHandle(const FileHandle&) = delete;
    FileHandle& operator=(const FileHandle&) = delete;
};

class LockGuard {
    HANDLE mutex_;
public:
    LockGuard(HANDLE m) : mutex_(m) {
        WaitForSingleObject(mutex_, INFINITE);
        std::cout << "[LockGuard] Lock acquired" << std::endl;
    }
    ~LockGuard() {
        ReleaseMutex(mutex_);
        std::cout << "[LockGuard] Lock released automatically" << std::endl;
    }
    LockGuard(const LockGuard&) = delete;
    LockGuard& operator=(const LockGuard&) = delete;
};

void riskyOperation(bool fail) {
    std::cout << "Inside riskyOperation(" << fail << ")" << std::endl;
    FileHandle fh("raii_test.txt", GENERIC_WRITE, CREATE_ALWAYS);
    HANDLE mtx = CreateMutexA(nullptr, FALSE, nullptr);
    {
        LockGuard lg(mtx);
        if (fail) {
            CloseHandle(mtx);
            DeleteFileA("raii_test.txt");
            throw std::runtime_error("Something went wrong!");
        }
        std::cout << "Operation completed successfully" << std::endl;
    }
    CloseHandle(mtx);
}

int main() {
    std::cout << "=== Normal case ===" << std::endl;
    try {
        riskyOperation(false);
    } catch (const std::exception& e) {
        std::cerr << "Caught: " << e.what() << std::endl;
    }

    std::cout << "\\n=== Exception case (RAII still cleans up!) ===" << std::endl;
    try {
        riskyOperation(true);
    } catch (const std::exception& e) {
        std::cerr << "Caught: " << e.what() << std::endl;
    }

    std::cout << "\\nNotice that even with exception, file was closed and lock released!" << std::endl;
    DeleteFileA("raii_test.txt");
    return 0;
}
```""")

# 32. constexpr编译期计算
add("使用C++11/14/17 constexpr特性实现编译期计算，包括编译期阶乘、斐波那契数列、字符串哈希、查找数组最大值，验证这些计算在编译时完成而非运行时。",
"""### 需求分析
constexpr编译期计算：
1. constexpr函数在编译期求值
2. 编译期阶乘、斐波那契
3. 编译期字符串哈希
4. 编译期数组操作
5. 使用static_assert验证编译期结果

### 设计思路
1. 使用C++14 relaxed constexpr（允许局部变量和循环）
2. 递归或循环实现编译期算法
3. constexpr变量存储编译期结果
4. static_assert在编译时检查结果正确性
5. 对比运行时计算性能（编译期计算零运行时开销）

### 关键问题
- C++11 constexpr限制：函数体只能有return语句
- C++14放宽：允许if、循环、局部变量
- C++20支持constexpr new/delete、vector、string
- 并非所有constexpr调用都在编译期：需要常量表达式上下文

### 代码实现
```cpp
#include <iostream>
#include <array>
#include <string_view>

constexpr int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

constexpr int fibonacci(int n) {
    if (n <= 1) return n;
    int a = 0, b = 1;
    for (int i = 2; i <= n; ++i) {
        int c = a + b;
        a = b;
        b = c;
    }
    return b;
}

constexpr size_t strHash(std::string_view s) {
    size_t hash = 5381;
    for (char c : s) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash;
}

template<typename T, size_t N>
constexpr T maxElement(const std::array<T, N>& arr) {
    T maxVal = arr[0];
    for (size_t i = 1; i < N; ++i) {
        if (arr[i] > maxVal) maxVal = arr[i];
    }
    return maxVal;
}

constexpr int power(int base, int exp) {
    int result = 1;
    for (int i = 0; i < exp; ++i) {
        result *= base;
    }
    return result;
}

static_assert(factorial(0) == 1, "factorial(0) should be 1");
static_assert(factorial(5) == 120, "factorial(5) should be 120");
static_assert(fibonacci(10) == 55, "fibonacci(10) should be 55");
static_assert(power(2, 10) == 1024, "2^10 should be 1024");

int main() {
    constexpr int fact5 = factorial(5);
    constexpr int fib10 = fibonacci(10);
    constexpr size_t hashHello = strHash("hello");
    constexpr std::array<int, 5> nums = {3, 7, 2, 9, 5};
    constexpr int maxNum = maxElement(nums);

    std::cout << "Compile-time computed values (no runtime cost!):" << std::endl;
    std::cout << "factorial(5) = " << fact5 << std::endl;
    std::cout << "fibonacci(10) = " << fib10 << std::endl;
    std::cout << "strHash(\"hello\") = " << hashHello << std::endl;
    std::cout << "max of {3,7,2,9,5} = " << maxNum << std::endl;
    std::cout << "power(2,10) = " << power(2, 10) << std::endl;

    return 0;
}
```""")

# 33. 内存序与原子操作
add("深入理解C++内存模型和std::atomic的内存序（memory_order），演示relaxed、acquire-release、seq_cst不同内存序的行为和使用场景，通过生产者消费者示例说明可见性保证。",
"""### 需求分析
C++内存序：
1. 六种内存序：relaxed, consume, acquire, release, acq_rel, seq_cst
2. 原子操作的可见性和顺序保证
3. happens-before关系
4. 使用release-acquire实现线程间同步
5. 对比mutex与原子操作的性能

### 设计思路
1. 使用std::atomic<bool>和std::atomic<int>
2. 演示relaxed：无顺序保证，仅原子性
3. 演示release-store和acquire-load配对：保证可见性
4. 实现简单的自旋锁
5. 单生产者单消费者无锁消息传递

### 关键问题
- 不要随意使用relaxed：除非完全理解后果
- release-acquire配对：像单向围栏
- seq_cst最强但可能最慢
- 内存序是关于可见性而非执行顺序
- consume内存序暂时不建议使用（编译器支持不完善）

### 代码实现
```cpp
#include <iostream>
#include <atomic>
#include <thread>
#include <vector>
#include <cassert>

std::atomic<int> data{0};
std::atomic<bool> ready{false};
std::atomic<int> counter{0};

void producer() {
    data.store(42, std::memory_order_relaxed);
    ready.store(true, std::memory_order_release);
    std::cout << "[Producer] Data published" << std::endl;
}

void consumer() {
    while (!ready.load(std::memory_order_acquire)) {
        std::this_thread::yield();
    }
    int value = data.load(std::memory_order_relaxed);
    std::cout << "[Consumer] Received data: " << value << std::endl;
    assert(value == 42);
}

void relaxedIncrement() {
    for (int i = 0; i < 10000; ++i) {
        counter.fetch_add(1, std::memory_order_relaxed);
    }
}

class SpinLock {
    std::atomic_flag flag_ = ATOMIC_FLAG_INIT;
public:
    void lock() {
        while (flag_.test_and_set(std::memory_order_acquire)) {
            std::this_thread::yield();
        }
    }
    void unlock() {
        flag_.clear(std::memory_order_release);
    }
};

SpinLock spinMtx;
int sharedData = 0;

void spinLockWorker(int id) {
    for (int i = 0; i < 1000; ++i) {
        spinMtx.lock();
        sharedData++;
        spinMtx.unlock();
    }
}

int main() {
    std::cout << "=== Release-Acquire synchronization ===" << std::endl;
    std::thread t1(producer);
    std::thread t2(consumer);
    t1.join();
    t2.join();

    std::cout << "\\n=== Relaxed atomic increment ===" << std::endl;
    std::vector<std::thread> threads;
    for (int i = 0; i < 4; ++i) {
        threads.emplace_back(relaxedIncrement);
    }
    for (auto& t : threads) t.join();
    std::cout << "Counter: " << counter.load() << " (should be 40000)" << std::endl;

    std::cout << "\\n=== Spinlock demo ===" << std::endl;
    std::vector<std::thread> workers;
    for (int i = 0; i < 4; ++i) {
        workers.emplace_back(spinLockWorker, i);
    }
    for (auto& t : workers) t.join();
    std::cout << "sharedData: " << sharedData << " (should be 4000)" << std::endl;

    return 0;
}
```""")

# 34. 可变参数模板
add("实现C++可变参数模板（variadic template），编写print函数打印任意数量任意类型的参数，实现tuple的简化版本，以及递归遍历tuple元素的方法。",
"""### 需求分析
可变参数模板：
1. 模板参数包：typename... Args
2. 函数参数包：Args... args
3. 递归展开参数包
4. 编写类型安全的printf
5. 简单tuple实现
6. C++17折叠表达式简化

### 设计思路
1. print函数：基础情况+递归展开
2. 使用C++17折叠表达式简化
3. Tuple实现：递归继承存储元素
4. 通过索引访问tuple元素
5. 实现make_tuple和get函数

### 关键问题
- 参数包展开：递归或折叠表达式
- 完美转发：std::forward保持值类别
- 结束递归：重载无参数版本或if constexpr（C++17）
- Tuple的递归结构：每个实例化层存储一个元素

### 代码实现
```cpp
#include <iostream>
#include <string>
#include <utility>

void print() {
    std::cout << std::endl;
}

template<typename T, typename... Args>
void print(T&& first, Args&&... rest) {
    std::cout << first;
    if (sizeof...(rest) > 0) std::cout << ", ";
    print(std::forward<Args>(rest)...);
}

template<typename... Args>
void printFold(Args&&... args) {
    ((std::cout << args << ", "), ...);
    std::cout << std::endl;
}

template<size_t N, typename T, typename... Rest>
struct TupleImpl : TupleImpl<N+1, Rest...> {
    T value;
    TupleImpl(T v, Rest... rest) : TupleImpl<N+1, Rest...>(rest...), value(v) {}
};

template<size_t N, typename T>
struct TupleImpl<N, T> {
    T value;
    TupleImpl(T v) : value(v) {}
};

template<typename... Ts>
struct Tuple : TupleImpl<0, Ts...> {
    using Base = TupleImpl<0, Ts...>;
    Tuple(Ts... vs) : Base(vs...) {}
};

template<size_t N, typename T>
T& get(TupleImpl<N, T>& t) {
    return t.value;
}

template<size_t N, typename T>
const T& get(const TupleImpl<N, T>& t) {
    return t.value;
}

int main() {
    std::cout << "=== Variadic print ===" << std::endl;
    print(1, 2.5, "hello", 'a', std::string("world"));

    std::cout << "=== Fold expression print ===" << std::endl;
    printFold(42, "test", 3.14, true);

    std::cout << "=== Simple Tuple ===" << std::endl;
    Tuple<int, double, std::string> t(1, 3.14, "hello");
    std::cout << "get<0>: " << get<0>(t) << std::endl;
    std::cout << "get<1>: " << get<1>(t) << std::endl;
    std::cout << "get<2>: " << get<2>(t) << std::endl;

    auto t2 = std::make_tuple(10, 20, "abc");
    std::cout << "std::tuple get<1>: " << std::get<1>(t2) << std::endl;

    return 0;
}
```""")

# 35. 状态模式
add("实现状态设计模式，创建一个TCP连接对象，根据不同状态（Closed、Listening、Established）表现出不同行为，状态转换时改变对象的行为，避免大量if-else判断。",
"""### 需求分析
状态模式：
1. 对象行为取决于其状态
2. 运行时改变状态
3. 避免大量if/switch判断状态
4. TCP连接示例：Closed->Listening->Established->Closed
5. 每个状态封装自己的行为和转换逻辑

### 设计思路
1. 抽象State基类，定义所有操作接口
2. 具体状态类：ClosedState、ListeningState、EstablishedState
3. TCPConnection持有当前状态指针
4. 状态类持有context引用，可以触发转换
5. 委托当前状态处理请求

### 关键问题
- 谁定义状态转换：状态类还是Context？取决于设计
- 状态对象共享：状态对象可以是无状态的单例
- vs策略模式：结构相似，意图不同（状态是内部驱动变化，策略是外部选择）
- 状态创建销毁：转换时创建新状态还是共享实例

### 代码实现
```cpp
#include <iostream>
#include <memory>
#include <string>

class TCPConnection;

class TCPState {
public:
    virtual void open(TCPConnection&) { std::cout << "Invalid operation for current state" << std::endl; }
    virtual void close(TCPConnection&) { std::cout << "Invalid operation for current state" << std::endl; }
    virtual void listen(TCPConnection&) { std::cout << "Invalid operation for current state" << std::endl; }
    virtual void send(TCPConnection&, const std::string&) { std::cout << "Invalid operation for current state" << std::endl; }
    virtual std::string name() const = 0;
    virtual ~TCPState() = default;
};

class TCPConnection {
    std::unique_ptr<TCPState> state_;
public:
    TCPConnection();
    void changeState(std::unique_ptr<TCPState> newState);
    void open() { state_->open(*this); }
    void close() { state_->close(*this); }
    void listen() { state_->listen(*this); }
    void send(const std::string& data) { state_->send(*this, data); }
    std::string currentState() const { return state_->name(); }
};

class ClosedState : public TCPState {
public:
    void open(TCPConnection& conn) override;
    void listen(TCPConnection& conn) override;
    std::string name() const override { return "CLOSED"; }
};

class ListeningState : public TCPState {
public:
    void close(TCPConnection& conn) override;
    void send(TCPConnection&, const std::string&) override {
        std::cout << "Cannot send while listening" << std::endl;
    }
    std::string name() const override { return "LISTENING"; }
};

class EstablishedState : public TCPState {
public:
    void close(TCPConnection& conn) override;
    void send(TCPConnection&, const std::string& data) override {
        std::cout << "[ESTABLISHED] Sending data: " << data << std::endl;
    }
    std::string name() const override { return "ESTABLISHED"; }
};

TCPConnection::TCPConnection() : state_(std::make_unique<ClosedState>()) {}
void TCPConnection::changeState(std::unique_ptr<TCPState> newState) {
    std::cout << "State changing from " << state_->name() << " to " << newState->name() << std::endl;
    state_ = std::move(newState);
}

void ClosedState::open(TCPConnection& conn) {
    std::cout << "[CLOSED] Opening connection..." << std::endl;
    conn.changeState(std::make_unique<EstablishedState>());
}
void ClosedState::listen(TCPConnection& conn) {
    std::cout << "[CLOSED] Starting to listen..." << std::endl;
    conn.changeState(std::make_unique<ListeningState>());
}
void ListeningState::close(TCPConnection& conn) {
    std::cout << "[LISTENING] Stopping listening..." << std::endl;
    conn.changeState(std::make_unique<ClosedState>());
}
void EstablishedState::close(TCPConnection& conn) {
    std::cout << "[ESTABLISHED] Closing connection..." << std::endl;
    conn.changeState(std::make_unique<ClosedState>());
}

int main() {
    TCPConnection conn;
    std::cout << "Initial state: " << conn.currentState() << std::endl;

    std::cout << "\\n--- Operations ---" << std::endl;
    conn.send("test");
    conn.open();
    conn.send("Hello World");
    conn.send("More data");
    conn.close();
    conn.listen();
    conn.send("data");
    conn.close();

    return 0;
}
```""")

# 36. 中介者模式
add("实现中介者设计模式，创建一个聊天室中介者，多个用户对象通过中介者发送消息，用户之间不直接通信，而是通过聊天室转发，实现用户加入/离开和群发消息功能。",
"""### 需求分析
中介者模式：
1. 封装一组对象的交互
2. 对象之间不直接引用
3. 松耦合，独立改变交互
4. 聊天室：用户发消息给中介者，中介者转发给其他人
5. 集中控制交互逻辑

### 设计思路
1. Mediator接口：sendMessage、addUser、removeUser
2. Colleague（User）持有中介者引用
3. ChatRoom具体中介者维护用户列表
4. User发送消息时调用mediator.broadcast
5. 中介者将消息转发给除发送者外的所有人

### 关键问题
- 中介者过度膨胀：所有交互逻辑都在中介者里
- vs观察者：观察者是一对多广播，中介者是多对多协调
- Colleague要知道Mediator接口
- 降低组件耦合但增加中介者复杂度

### 代码实现
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <algorithm>

class ChatRoom;

class User {
    std::string name_;
    ChatRoom* room_;
public:
    User(const std::string& name) : name_(name), room_(nullptr) {}
    void joinRoom(ChatRoom* room);
    void send(const std::string& msg);
    void receive(const std::string& from, const std::string& msg);
    const std::string& name() const { return name_; }
};

class ChatRoom {
    std::vector<User*> users_;
public:
    void addUser(User* u) {
        users_.push_back(u);
        std::cout << "[System] " << u->name() << " joined the chat" << std::endl;
        broadcast(u, "has joined the room");
    }

    void removeUser(User* u) {
        users_.erase(std::remove(users_.begin(), users_.end(), u), users_.end());
        std::cout << "[System] " << u->name() << " left the chat" << std::endl;
    }

    void broadcast(User* sender, const std::string& msg) {
        for (User* u : users_) {
            if (u != sender) {
                u->receive(sender->name(), msg);
            }
        }
    }
};

void User::joinRoom(ChatRoom* room) {
    room_ = room;
    room_->addUser(this);
}

void User::send(const std::string& msg) {
    std::cout << "[" << name_ << "] sends: " << msg << std::endl;
    if (room_) {
        room_->broadcast(this, msg);
    }
}

void User::receive(const std::string& from, const std::string& msg) {
    std::cout << "[" << name_ << "] received from " << from << ": " << msg << std::endl;
}

int main() {
    ChatRoom room;

    User alice("Alice");
    User bob("Bob");
    User charlie("Charlie");

    alice.joinRoom(&room);
    bob.joinRoom(&room);
    charlie.joinRoom(&room);

    std::cout << std::endl;
    alice.send("Hi everyone!");
    std::cout << std::endl;
    bob.send("Hello Alice!");
    std::cout << std::endl;
    charlie.send("Hey guys, how are you?");

    room.removeUser(&bob);
    alice.send("Bob left?");

    return 0;
}
```""")

# 37. INI配置文件解析
add("实现INI配置文件解析器，支持section（[section]）、key=value键值对、注释（;或#开头），读取INI文件到内存数据结构，支持查询、修改和保存，处理字符串引号和转义。",
"""### 需求分析
INI文件解析：
1. [section]定义节
2. key=value键值对
3. ;或#开头是注释
4. 支持空行
5. 字符串值可以带引号
6. 加载、查询、修改、保存

### 设计思路
1. 数据结构：map<section, map<key, value>>
2. 逐行读取文件
3. trim空白字符
4. 识别section：[section]
5. 识别注释行跳过
6. 按第一个=分割key和value
7. 保存时按原格式写入

### 关键问题
- 空白处理：key和value前后的空格要trim
- 重复key/section：后出现的覆盖还是报错
- 值中的=：只在第一个=处分割
- 大小写敏感：section和key通常大小写不敏感（本实现保持大小写敏感）
- 转义字符：可扩展支持\\n等

### 代码实现
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <sstream>
#include <algorithm>

class INIConfig {
    std::map<std::string, std::map<std::string, std::string>> data_;

    static std::string trim(const std::string& s) {
        size_t start = s.find_first_not_of(" \\t\\r\\n");
        if (start == std::string::npos) return "";
        size_t end = s.find_last_not_of(" \\t\\r\\n");
        return s.substr(start, end - start + 1);
    }

public:
    bool load(const std::string& filename) {
        std::ifstream file(filename);
        if (!file) return false;

        std::string line, currentSection;
        while (std::getline(file, line)) {
            line = trim(line);
            if (line.empty()) continue;
            if (line[0] == ';' || line[0] == '#') continue;

            if (line[0] == '[' && line.back() == ']') {
                currentSection = trim(line.substr(1, line.size() - 2));
                continue;
            }

            size_t eq = line.find('=');
            if (eq != std::string::npos) {
                std::string key = trim(line.substr(0, eq));
                std::string value = trim(line.substr(eq + 1));
                if (value.size() >= 2 && value.front() == '"' && value.back() == '"') {
                    value = value.substr(1, value.size() - 2);
                }
                data_[currentSection][key] = value;
            }
        }
        return true;
    }

    bool save(const std::string& filename) {
        std::ofstream file(filename);
        if (!file) return false;
        for (const auto& [section, kvs] : data_) {
            file << "[" << section << "]\\n";
            for (const auto& [k, v] : kvs) {
                file << k << " = " << v << "\\n";
            }
            file << "\\n";
        }
        return true;
    }

    std::string get(const std::string& section, const std::string& key, const std::string& def = "") {
        auto sit = data_.find(section);
        if (sit == data_.end()) return def;
        auto kit = sit->second.find(key);
        if (kit == sit->second.end()) return def;
        return kit->second;
    }

    void set(const std::string& section, const std::string& key, const std::string& value) {
        data_[section][key] = value;
    }

    bool has(const std::string& section, const std::string& key) {
        return data_.count(section) && data_[section].count(key);
    }

    void print() const {
        for (const auto& [section, kvs] : data_) {
            std::cout << "[" << section << "]" << std::endl;
            for (const auto& [k, v] : kvs) {
                std::cout << "  " << k << " = " << v << std::endl;
            }
        }
    }
};

int main() {
    INIConfig config;
    config.set("database", "host", "localhost");
    config.set("database", "port", "3306");
    config.set("server", "port", "8080");
    config.set("server", "debug", "true");
    config.save("test_config.ini");

    INIConfig loaded;
    loaded.load("test_config.ini");
    loaded.print();

    std::cout << "\\nQueries:" << std::endl;
    std::cout << "database.host = " << loaded.get("database", "host") << std::endl;
    std::cout << "database.port = " << loaded.get("database", "port") << std::endl;
    std::cout << "nonexistent = " << loaded.get("a", "b", "default_value") << std::endl;

    DeleteFileA("test_config.ini");
    return 0;
}
```""")

# 38. CSV读写
add("实现CSV（逗号分隔值）文件读写，支持带引号的字段、字段内包含逗号和换行符，正确解析CSV格式，读取后可以按行和列访问数据，也可以导出CSV文件。",
"""### 需求分析
CSV解析：
1. 字段用逗号分隔
2. 字段含逗号/换行/引号时用双引号包裹
3. 引号用两个双引号转义（""表示一个"）
4. 按行存储，可以访问行列
5. 正确处理换行符（\\r\\n或\\n）

### 设计思路
1. CSVRow表示一行，vector<string>字段
2. CSVDocument包含vector<CSVRow>
3. 状态机解析：正常状态、引号内状态
4. 逐字符解析处理引号和转义
5. 写入时对包含特殊字符的字段加引号

### 关键问题
- CSV没有统一标准：RFC4180是常见标准
- 引号内的双引号：""表示字面量"
- 换行符：引号字段内可以有换行
- 结尾空行：是否保留

### 代码实现
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string>

class CSVReader {
public:
    using Row = std::vector<std::string>;

    static std::vector<Row> parse(const std::string& filename) {
        std::vector<Row> result;
        std::ifstream file(filename);
        if (!file) return result;

        Row row;
        std::string field;
        bool inQuotes = false;
        char c;

        while (file.get(c)) {
            if (inQuotes) {
                if (c == '"') {
                    if (file.peek() == '"') {
                        field += '"';
                        file.get();
                    } else {
                        inQuotes = false;
                    }
                } else {
                    field += c;
                }
            } else {
                if (c == '"') {
                    inQuotes = true;
                } else if (c == ',') {
                    row.push_back(field);
                    field.clear();
                } else if (c == '\\r') {
                    continue;
                } else if (c == '\\n') {
                    row.push_back(field);
                    result.push_back(row);
                    row.clear();
                    field.clear();
                } else {
                    field += c;
                }
            }
        }
        if (!field.empty() || !row.empty()) {
            row.push_back(field);
            result.push_back(row);
        }
        return result;
    }

    static void write(const std::string& filename, const std::vector<Row>& rows) {
        std::ofstream file(filename);
        for (const auto& row : rows) {
            for (size_t i = 0; i < row.size(); ++i) {
                if (i > 0) file << ",";
                const std::string& f = row[i];
                bool needQuote = f.find(',') != std::string::npos || f.find('"') != std::string::npos
                                 || f.find('\\n') != std::string::npos;
                if (needQuote) {
                    file << '"';
                    for (char ch : f) {
                        if (ch == '"') file << "\"\"";
                        else file << ch;
                    }
                    file << '"';
                } else {
                    file << f;
                }
            }
            file << "\\n";
        }
    }
};

int main() {
    std::vector<CSVReader::Row> data = {
        {"Name", "Age", "City", "Description"},
        {"Alice", "30", "Beijing", "Loves C++, coding"},
        {"Bob", "25", "Shanghai", "Says \"Hello, World!\""},
        {"Charlie", "35", "Guangzhou", "Multi-line\\nField with comma, here"},
    };

    CSVReader::write("test.csv", data);

    auto loaded = CSVReader::parse("test.csv");

    std::cout << "CSV contents:" << std::endl;
    for (const auto& row : loaded) {
        for (size_t i = 0; i < row.size(); ++i) {
            if (i > 0) std::cout << " | ";
            std::cout << row[i];
        }
        std::cout << std::endl;
    }

    DeleteFileA("test.csv");
    return 0;
}
```""")

# 39. 对象池
add("实现一个通用对象池（Object Pool），预先创建一组可重用对象，避免频繁创建销毁的开销，支持获取对象、归还对象、动态扩容，适用于数据库连接、线程等重量级资源。",
"""### 需求分析
对象池模式：
1. 预创建对象，复用而非新建销毁
2. 获取对象：从池里取，池空则创建或等待
3. 归还对象：用完放回池中
4. 适合创建/销毁开销大的对象
5. 线程安全版本

### 设计思路
1. 模板类ObjectPool<T>
2. 池用队列存储可用对象
3. mutex保护池操作
4. condition_variable等待可用对象
5. 提供shared_ptr定制deleter自动归还
6. 可配置初始大小和最大大小

### 关键问题
- 对象重置：归还时是否需要重置状态
- 最大池大小：限制内存使用
- 自动归还：用智能指针自定义删除器
- 线程安全：多线程同时获取/归还
- 对象创建：工厂函数注入构造逻辑

### 代码实现
```cpp
#include <iostream>
#include <queue>
#include <memory>
#include <mutex>
#include <condition_variable>
#include <functional>
#include <thread>

template<typename T>
class ObjectPool {
    std::queue<std::unique_ptr<T>> pool_;
    std::mutex mutex_;
    std::condition_variable cv_;
    std::function<std::unique_ptr<T>()> factory_;
    size_t maxSize_;
    size_t totalCreated_ = 0;

public:
    ObjectPool(std::function<std::unique_ptr<T>()> factory, size_t initialSize, size_t maxSize)
        : factory_(std::move(factory)), maxSize_(maxSize) {
        for (size_t i = 0; i < initialSize; ++i) {
            pool_.push(factory_());
            totalCreated_++;
        }
    }

    std::shared_ptr<T> acquire() {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_.wait(lock, [this] { return !pool_.empty() || totalCreated_ < maxSize_; });

        std::unique_ptr<T> obj;
        if (!pool_.empty()) {
            obj = std::move(pool_.front());
            pool_.pop();
        } else {
            obj = factory_();
            totalCreated_++;
        }

        return std::shared_ptr<T>(obj.release(), [this](T* p) {
            std::unique_lock<std::mutex> lock(mutex_);
            pool_.push(std::unique_ptr<T>(p));
            cv_.notify_one();
        });
    }

    size_t available() {
        std::lock_guard<std::mutex> lock(mutex_);
        return pool_.size();
    }
};

struct DatabaseConnection {
    int id;
    DatabaseConnection(int i) : id(i) {
        std::cout << "Creating DB connection #" << id << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    void query(const std::string& sql) {
        std::cout << "Connection #" << id << " executing: " << sql << std::endl;
    }
    ~DatabaseConnection() {
        std::cout << "Destroying DB connection #" << id << std::endl;
    }
};

int main() {
    static int nextId = 1;
    ObjectPool<DatabaseConnection> pool(
        [] { return std::make_unique<DatabaseConnection>(nextId++); },
        2, 5
    );

    std::cout << "Initial pool size: " << pool.available() << std::endl << std::endl;

    {
        auto c1 = pool.acquire();
        c1->query("SELECT * FROM users");
        std::cout << "Available after acquire 1: " << pool.available() << std::endl;

        auto c2 = pool.acquire();
        c2->query("SELECT * FROM products");
        std::cout << "Available after acquire 2: " << pool.available() << std::endl;

        auto c3 = pool.acquire();
        c3->query("INSERT INTO logs VALUES (...)");
        std::cout << "Available after acquire 3 (created new): " << pool.available() << std::endl;
    }

    std::cout << "\\nAfter all released, available: " << pool.available() << std::endl;

    return 0;
}
```""")

# 40. 简易状态机
add("实现一个有限状态机（FSM）框架，支持定义状态、事件、转换动作，实现一个简单的交通灯状态机（红->绿->黄->红），演示状态转换、进入/退出动作、守卫条件。",
"""### 需求分析
有限状态机：
1. 状态：系统可能的状态
2. 事件：触发转换
3. 转换：源状态+事件->目标状态+动作
4. 进入/退出动作
5. 守卫条件决定是否转换
6. 交通灯示例：红、绿、黄

### 设计思路
1. State基类，包含onEnter/onExit/handleEvent
2. 状态机持有当前状态
3. 转换表：源状态->事件->{目标，动作，守卫}
4. 交通灯具体状态
5. 定时器或事件触发转换

### 关键问题
- 转换表：用嵌套map或vector存储转换规则
- 动作执行：转换时执行动作
- 守卫条件：返回bool决定是否允许转换
- 历史状态：可扩展保存上次状态

### 代码实现
```cpp
#include <iostream>
#include <string>
#include <map>
#include <functional>
#include <chrono>
#include <thread>

enum class TrafficEvent { TIMER, EMERGENCY, RESET };

std::string eventName(TrafficEvent e) {
    switch(e) {
        case TrafficEvent::TIMER: return "TIMER";
        case TrafficEvent::EMERGENCY: return "EMERGENCY";
        case TrafficEvent::RESET: return "RESET";
    }
    return "";
}

class TrafficLightFSM;

class LightState {
public:
    virtual void onEnter() {}
    virtual void onExit() {}
    virtual std::string name() const = 0;
    virtual ~LightState() = default;
};

class RedLight : public LightState {
public:
    std::string name() const override { return "RED"; }
    void onEnter() override { std::cout << "[RED] Stop! Pedestrians can cross." << std::endl; }
};

class GreenLight : public LightState {
public:
    std::string name() const override { return "GREEN"; }
    void onEnter() override { std::cout << "[GREEN] Go!" << std::endl; }
};

class YellowLight : public LightState {
public:
    std::string name() const override { return "YELLOW"; }
    void onEnter() override { std::cout << "[YELLOW] Prepare to stop!" << std::endl; }
};

class TrafficLightFSM {
    LightState* current_;
    RedLight red_;
    GreenLight green_;
    YellowLight yellow_;
public:
    TrafficLightFSM() : current_(&red_) {
        current_->onEnter();
    }

    void trigger(TrafficEvent event) {
        std::cout << "\\nEvent: " << eventName(event) << std::endl;
        LightState* next = nullptr;

        if (event == TrafficEvent::EMERGENCY) {
            next = &red_;
        } else if (event == TrafficEvent::TIMER) {
            if (current_ == &red_) next = &green_;
            else if (current_ == &green_) next = &yellow_;
            else if (current_ == &yellow_) next = &red_;
        } else if (event == TrafficEvent::RESET) {
            next = &red_;
        }

        if (next && next != current_) {
            current_->onExit();
            std::cout << "Transitioning from " << current_->name()
                      << " to " << next->name() << std::endl;
            current_ = next;
            current_->onEnter();
        }
    }

    std::string currentState() const { return current_->name(); }
};

int main() {
    TrafficLightFSM fsm;

    std::cout << "=== Normal cycle ===" << std::endl;
    std::cout << "Current: " << fsm.currentState() << std::endl;
    std::this_thread::sleep_for(std::chrono::seconds(1));

    fsm.trigger(TrafficEvent::TIMER);
    std::this_thread::sleep_for(std::chrono::seconds(1));

    fsm.trigger(TrafficEvent::TIMER);
    std::this_thread::sleep_for(std::chrono::milliseconds(500));

    std::cout << "\\n=== Emergency! ===" << std::endl;
    fsm.trigger(TrafficEvent::EMERGENCY);

    std::this_thread::sleep_for(std::chrono::seconds(1));

    std::cout << "\\n=== Resume cycle ===" << std::endl;
    fsm.trigger(TrafficEvent::TIMER);

    return 0;
}
```""")

print(f"Added 10 more, now have {len(all_entries)} entries, adding 10 more...")

# 41. 聊天室服务器
add("实现一个多用户聊天室服务器，支持多个客户端telnet连接，用户可以设置昵称、发送公共消息、查看在线用户列表，使用select多路复用处理多个连接，实现简单的IRC风格协议。",
"""### 需求分析
聊天室服务器：
1. 多客户端同时连接
2. 设置昵称命令：/nick <name>
3. 发送公共消息（广播给所有人）
4. 查看用户列表：/users
5. 用户加入/离开系统消息
6. select多路复用处理

### 设计思路
1. 监听socket + select
2. 每个客户端维护一个状态（昵称）
3. map<socket, nickname>存储客户端
4. 收到消息时解析命令
5. 非命令消息广播给所有人
6. 新用户加入广播欢迎消息

### 关键问题
- 消息缓冲：TCP是流，需要按行缓冲解析
- 广播：遍历所有客户端发送
- telnet换行：\\r\\n
- 昵称冲突：检查昵称是否已存在

### 代码实现
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <algorithm>
#include <sstream>

#pragma comment(lib, "ws2_32.lib")

const int PORT = 6667;
const int BUF_SIZE = 2048;

std::map<SOCKET, std::string> clients;
std::map<SOCKET, std::string> buffers;

void broadcast(const std::string& msg, SOCKET except = INVALID_SOCKET) {
    std::string data = msg + "\\r\\n";
    for (auto& [sock, name] : clients) {
        if (sock != except) {
            send(sock, data.c_str(), data.size(), 0);
        }
    }
}

void sendLine(SOCKET sock, const std::string& msg) {
    std::string data = msg + "\\r\\n";
    send(sock, data.c_str(), data.size(), 0);
}

void handleMessage(SOCKET sock, const std::string& line) {
    std::string& nick = clients[sock];
    if (line.substr(0, 6) == "/nick ") {
        std::string newNick = line.substr(6);
        for (auto& [s, n] : clients) {
            if (s != sock && n == newNick) {
                sendLine(sock, "ERROR: Nickname already taken");
                return;
            }
        }
        std::string oldNick = nick.empty() ? "Guest" : nick;
        nick = newNick;
        sendLine(sock, "OK: Nickname set to " + newNick);
        broadcast("*** " + oldNick + " is now known as " + newNick);
    } else if (line == "/users") {
        std::string userList = "Online users (" + std::to_string(clients.size()) + "):";
        for (auto& [s, n] : clients) {
            userList += "\\n  - " + (n.empty() ? "Guest" : n);
        }
        sendLine(sock, userList);
    } else if (line == "/quit") {
        std::string name = nick.empty() ? "A guest" : nick;
        broadcast("*** " + name + " has left the chat");
        closesocket(sock);
        clients.erase(sock);
        buffers.erase(sock);
    } else {
        std::string name = nick.empty() ? "Guest" : nick;
        broadcast("[" + name + "] " + line, sock);
        std::cout << "[" << name << "] " << line << std::endl;
    }
}

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

    std::cout << "Chat room server running on port " << PORT << std::endl;
    std::cout << "Connect with: telnet localhost " << PORT << std::endl;

    while (true) {
        fd_set readfds;
        FD_ZERO(&readfds);
        FD_SET(listenSock, &readfds);
        for (auto& [sock, _] : clients) FD_SET(sock, &readfds);

        timeval tv{0, 100000};
        select(0, &readfds, nullptr, nullptr, &tv);

        if (FD_ISSET(listenSock, &readfds)) {
            SOCKET client = accept(listenSock, nullptr, nullptr);
            clients[client] = "";
            buffers[client] = "";
            sendLine(client, "Welcome! Type /nick <name> to set your nickname");
            broadcast("*** A new guest joined", client);
            std::cout << "New client connected, total: " << clients.size() << std::endl;
        }

        std::vector<SOCKET> toRemove;
        for (auto& [sock, _] : clients) {
            if (FD_ISSET(sock, &readfds)) {
                char buf[BUF_SIZE];
                int r = recv(sock, buf, BUF_SIZE, 0);
                if (r <= 0) {
                    toRemove.push_back(sock);
                    continue;
                }
                buffers[sock].append(buf, r);
                size_t pos;
                while ((pos = buffers[sock].find_first_of("\\r\\n")) != std::string::npos) {
                    std::string line = buffers[sock].substr(0, pos);
                    buffers[sock].erase(0, pos + 1);
                    while (!buffers[sock].empty() && (buffers[sock][0] == '\\r' || buffers[sock][0] == '\\n')) {
                        buffers[sock].erase(0, 1);
                    }
                    if (!line.empty()) {
                        handleMessage(sock, line);
                    }
                }
            }
        }
        for (SOCKET s : toRemove) {
            std::string name = clients[s].empty() ? "A guest" : clients[s];
            broadcast("*** " + name + " has left the chat");
            closesocket(s);
            clients.erase(s);
            buffers.erase(s);
        }
    }

    WSACleanup();
    return 0;
}
```""")

# 42. 信号量
add("实现C++20 std::counting_semaphore和简化版信号量，演示信号量控制并发访问数量，实现资源池限流，允许多个线程同时访问但限制最大并发数。",
"""### 需求分析
信号量：
1. 计数信号量维护一个计数器
2. acquire/P操作：计数器减1，为0时阻塞
3. release/V操作：计数器加1，唤醒等待线程
4. 限制并发访问数量
5. 用条件变量和mutex实现C++20之前的信号量

### 设计思路
1. Semaphore类，count初始化为最大并发数
2. wait/acquire：等待count>0，然后减1
3. post/release：count加1，通知一个等待线程
4. mutex+condition_variable实现
5. 示例：限制最多3个线程同时访问资源

### 关键问题
- 互斥量vs信号量：互斥量是binary semaphore（0/1）
- 计数信号量：count可以是任意非负数
- 可以release超过初始count吗：可以，但一般避免
- 信号量不绑线程：一个线程acquire，另一个可以release（不同于mutex）

### 代码实现
```cpp
#include <iostream>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <vector>
#include <chrono>

class CountingSemaphore {
    int count_;
    std::mutex mtx_;
    std::condition_variable cv_;
public:
    CountingSemaphore(int initial) : count_(initial) {}

    void acquire() {
        std::unique_lock<std::mutex> lock(mtx_);
        cv_.wait(lock, [this] { return count_ > 0; });
        --count_;
    }

    void release() {
        std::lock_guard<std::mutex> lock(mtx_);
        ++count_;
        cv_.notify_one();
    }
};

CountingSemaphore sem(3);
int activeWorkers = 0;
std::mutex printMtx;

void worker(int id) {
    sem.acquire();
    {
        std::lock_guard<std::mutex> lock(printMtx);
        activeWorkers++;
        std::cout << "Worker " << id << " started, active: " << activeWorkers << std::endl;
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(500 + (id % 3) * 200));

    {
        std::lock_guard<std::mutex> lock(printMtx);
        std::cout << "Worker " << id << " finished" << std::endl;
        activeWorkers--;
    }
    sem.release();
}

int main() {
    std::cout << "Semaphore demo: max 3 concurrent workers\\n" << std::endl;
    std::vector<std::thread> threads;
    for (int i = 1; i <= 8; ++i) {
        threads.emplace_back(worker, i);
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    for (auto& t : threads) t.join();
    return 0;
}
```""")

# 43. 非阻塞Socket
add("实现非阻塞TCP客户端和服务器，使用ioctlsocket将socket设置为非阻塞模式，结合select实现非阻塞connect和非阻塞读写，演示异步连接过程。",
"""### 需求分析
非阻塞Socket：
1. socket操作立即返回，不会阻塞线程
2. 非阻塞connect：连接进行中返回WSAEWOULDBLOCK
3. select检测可写状态判断连接完成
4. 非阻塞send/recv可能只发送/接收部分数据
5. 实现非阻塞connect示例

### 设计思路
1. ioctlsocket(FIONBIO)设置非阻塞模式
2. connect时返回WSAEWOULDBLOCK是正常的
3. select等待socket可写表示连接成功/失败
4. getsockopt(SO_ERROR)检查连接结果
5. 非阻塞send/recv处理部分完成情况

### 关键问题
- connect后select超时：连接超时
- SO_ERROR检查：连接失败原因
- 非阻塞accept：没有连接时返回错误
- 必须处理WSAEWOULDBLOCK错误

### 代码实现
```cpp
#include <iostream>
#include <string>
#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib, "ws2_32.lib")

bool nonBlockingConnect(SOCKET sock, const sockaddr* addr, int addrLen, int timeoutMs) {
    u_long mode = 1;
    ioctlsocket(sock, FIONBIO, &mode);

    int ret = connect(sock, addr, addrLen);
    if (ret == 0) {
        mode = 0;
        ioctlsocket(sock, FIONBIO, &mode);
        return true;
    }

    if (WSAGetLastError() != WSAEWOULDBLOCK) return false;

    fd_set writefds, exceptfds;
    FD_ZERO(&writefds);
    FD_SET(sock, &writefds);
    FD_ZERO(&exceptfds);
    FD_SET(sock, &exceptfds);

    timeval timeout;
    timeout.tv_sec = timeoutMs / 1000;
    timeout.tv_usec = (timeoutMs % 1000) * 1000;

    int result = select(0, nullptr, &writefds, &exceptfds, &timeout);
    if (result <= 0) return false;

    int error = 0;
    int len = sizeof(error);
    getsockopt(sock, SOL_SOCKET, SO_ERROR, (char*)&error, &len);

    mode = 0;
    ioctlsocket(sock, FIONBIO, &mode);
    return error == 0;
}

int main() {
    WSADATA wsa;
    WSAStartup(MAKEWORD(2, 2), &wsa);

    const char* host = "example.com";
    const char* port = "80";

    addrinfo hints{}, *res;
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    getaddrinfo(host, port, &hints, &res);

    SOCKET sock = socket(res->ai_family, res->ai_socktype, res->ai_protocol);

    std::cout << "Connecting to " << host << ":" << port << " (non-blocking, 5s timeout)..." << std::endl;
    auto start = std::chrono::high_resolution_clock::now();

    if (nonBlockingConnect(sock, res->ai_addr, res->ai_addrlen, 5000)) {
        auto end = std::chrono::high_resolution_clock::now();
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
        std::cout << "Connected successfully in " << ms << "ms" << std::endl;

        std::string req = "HEAD / HTTP/1.1\\r\\nHost: example.com\\r\\nConnection: close\\r\\n\\r\\n";
        send(sock, req.c_str(), req.size(), 0);

        char buf[1024];
        int r = recv(sock, buf, sizeof(buf) - 1, 0);
        if (r > 0) {
            buf[r] = '\\0';
            std::cout << "Response:\\n" << buf << std::endl;
        }
    } else {
        std::cout << "Connection failed or timed out" << std::endl;
    }

    closesocket(sock);
    freeaddrinfo(res);
    WSACleanup();
    return 0;
}
```""")

# 44. 访问者模式
add("实现访问者设计模式，为一组元素（不同几何形状：圆形、矩形、三角形）添加新操作而不修改元素类，实现面积计算、周长计算、SVG导出访问者，演示双重分派。",
"""### 需求分析
访问者模式：
1. 为对象结构添加新操作不修改元素类
2. 元素类只需要accept(Visitor)方法
3. 双重分派：元素和访问者共同决定执行哪个方法
4. 具体元素：Circle、Rectangle、Triangle
5. 具体访问者：AreaVisitor、PerimeterVisitor

### 设计思路
1. Visitor接口：visit(Circle&), visit(Rectangle&), visit(Triangle&)
2. Element接口：accept(Visitor&)
3. 每个元素accept实现：v.visit(*this)
4. 访问者实现具体操作
5. 可以添加新访问者而不改形状类

### 关键问题
- 双重分派：两次虚函数调用确定具体方法
- 开闭原则：增加新操作容易，增加新元素需要改所有访问者
- 需要预先知道所有元素类型
- 破坏封装：访问者可能需要访问元素内部状态

### 代码实现
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <cmath>
#include <numbers>

class Circle;
class Rectangle;
class Triangle;

class ShapeVisitor {
public:
    virtual void visit(Circle& c) = 0;
    virtual void visit(Rectangle& r) = 0;
    virtual void visit(Triangle& t) = 0;
    virtual ~ShapeVisitor() = default;
};

class Shape {
public:
    virtual void accept(ShapeVisitor& v) = 0;
    virtual ~Shape() = default;
};

class Circle : public Shape {
public:
    double radius;
    Circle(double r) : radius(r) {}
    void accept(ShapeVisitor& v) override { v.visit(*this); }
};

class Rectangle : public Shape {
public:
    double width, height;
    Rectangle(double w, double h) : width(w), height(h) {}
    void accept(ShapeVisitor& v) override { v.visit(*this); }
};

class Triangle : public Shape {
public:
    double a, b, c;
    Triangle(double x, double y, double z) : a(x), b(y), c(z) {}
    void accept(ShapeVisitor& v) override { v.visit(*this); }
};

class AreaVisitor : public ShapeVisitor {
public:
    double totalArea = 0;
    void visit(Circle& c) override {
        double area = std::numbers::pi * c.radius * c.radius;
        std::cout << "Circle area: " << area << std::endl;
        totalArea += area;
    }
    void visit(Rectangle& r) override {
        double area = r.width * r.height;
        std::cout << "Rectangle area: " << area << std::endl;
        totalArea += area;
    }
    void visit(Triangle& t) override {
        double s = (t.a + t.b + t.c) / 2;
        double area = std::sqrt(s * (s-t.a) * (s-t.b) * (s-t.c));
        std::cout << "Triangle area (Heron): " << area << std::endl;
        totalArea += area;
    }
};

class PerimeterVisitor : public ShapeVisitor {
public:
    double totalPerim = 0;
    void visit(Circle& c) override {
        double p = 2 * std::numbers::pi * c.radius;
        std::cout << "Circle perimeter: " << p << std::endl;
        totalPerim += p;
    }
    void visit(Rectangle& r) override {
        double p = 2 * (r.width + r.height);
        std::cout << "Rectangle perimeter: " << p << std::endl;
        totalPerim += p;
    }
    void visit(Triangle& t) override {
        double p = t.a + t.b + t.c;
        std::cout << "Triangle perimeter: " << p << std::endl;
        totalPerim += p;
    }
};

int main() {
    std::vector<std::unique_ptr<Shape>> shapes;
    shapes.push_back(std::make_unique<Circle>(5));
    shapes.push_back(std::make_unique<Rectangle>(4, 6));
    shapes.push_back(std::make_unique<Triangle>(3, 4, 5));

    std::cout << "=== Calculating areas ===" << std::endl;
    AreaVisitor areaV;
    for (auto& s : shapes) s->accept(areaV);
    std::cout << "Total area: " << areaV.totalArea << std::endl;

    std::cout << "\\n=== Calculating perimeters ===" << std::endl;
    PerimeterVisitor perimV;
    for (auto& s : shapes) s->accept(perimV);
    std::cout << "Total perimeter: " << perimV.totalPerim << std::endl;

    return 0;
}
```""")

# 45. 移动语义演示
add("深入理解C++11移动语义和右值引用，实现一个支持移动构造和移动赋值的动态数组类，演示拷贝与移动的性能差异，理解std::move的作用和完美转发。",
"""### 需求分析
移动语义：
1. 右值引用T&&绑定临时对象
2. 移动构造/赋值转移资源所有权
3. std::move将左值转为右值
4. noexcept移动构造让容器使用移动而非拷贝
5. 对比深拷贝和移动的性能差异

### 设计思路
1. 实现MyVector类管理动态数组
2. 拷贝构造：深拷贝所有元素
3. 移动构造：窃取指针，置空源对象
4. 移动赋值：释放自己资源，窃取源资源
5. push_back使用完美转发
6. 测试拷贝vs移动性能

### 关键问题
- noexcept标记：移动操作应该标记noexcept
- 自赋值检查：移动赋值也要检查
- 移后源对象状态：应该是有效但未指定状态（可析构、可赋值）
- 不要在移动后使用源对象的值
- std::move本身不移动，只是启用移动

### 代码实现
```cpp
#include <iostream>
#include <utility>
#include <chrono>
#include <cstring>
#include <vector>

class Buffer {
    size_t size_;
    char* data_;
public:
    explicit Buffer(size_t size) : size_(size), data_(new char[size]) {
        std::cout << "Buffer(" << size << ") constructed" << std::endl;
        memset(data_, 0, size);
    }

    ~Buffer() {
        delete[] data_;
        std::cout << "Buffer(" << size_ << ") destroyed" << std::endl;
    }

    Buffer(const Buffer& other) : size_(other.size_), data_(new char[other.size_]) {
        std::cout << "Buffer copied (size " << size_ << ")" << std::endl;
        memcpy(data_, other.data_, size_);
    }

    Buffer(Buffer&& other) noexcept : size_(other.size_), data_(other.data_) {
        std::cout << "Buffer moved (size " << size_ << ")" << std::endl;
        other.data_ = nullptr;
        other.size_ = 0;
    }

    Buffer& operator=(const Buffer& other) {
        if (this != &other) {
            delete[] data_;
            size_ = other.size_;
            data_ = new char[size_];
            memcpy(data_, other.data_, size_);
            std::cout << "Buffer copy-assigned (size " << size_ << ")" << std::endl;
        }
        return *this;
    }

    Buffer& operator=(Buffer&& other) noexcept {
        if (this != &other) {
            delete[] data_;
            size_ = other.size_;
            data_ = other.data_;
            other.data_ = nullptr;
            other.size_ = 0;
            std::cout << "Buffer move-assigned (size " << size_ << ")" << std::endl;
        }
        return *this;
    }

    size_t size() const { return size_; }
};

Buffer createLargeBuffer(size_t size) {
    return Buffer(size);
}

int main() {
    std::cout << "=== Copy vs Move demo ===" << std::endl;
    const size_t N = 10000000;

    auto start1 = std::chrono::high_resolution_clock::now();
    Buffer b1(N);
    Buffer b2 = b1;
    auto end1 = std::chrono::high_resolution_clock::now();
    auto copyTime = std::chrono::duration<double, std::milli>(end1 - start1).count();

    std::cout << std::endl;

    auto start2 = std::chrono::high_resolution_clock::now();
    Buffer b3(N);
    Buffer b4 = std::move(b3);
    auto end2 = std::chrono::high_resolution_clock::now();
    auto moveTime = std::chrono::duration<double, std::milli>(end2 - start2).count();

    std::cout << "\\n=== Performance ===" << std::endl;
    std::cout << "Copy time: " << copyTime << "ms" << std::endl;
    std::cout << "Move time: " << moveTime << "ms" << std::endl;
    std::cout << "Move is ~" << (int)(copyTime / moveTime) << "x faster!" << std::endl;

    std::cout << "\\n=== RVO (return value optimization) ===" << std::endl;
    Buffer b5 = createLargeBuffer(100);

    return 0;
}
```""")

# 46. 类型擦除
add("实现C++类型擦除（Type Erasure）技术，创建一个可以存储任意可调用对象的Function类，类似std::function的简化实现，演示如何用模板和继承擦除具体类型。",
"""### 需求分析
类型擦除：
1. 统一接口隐藏不同具体类型
2. 类似std::function可以存储任何可调用对象
3. 使用模板构造+抽象基类+具体子类
4. 不使用模板参数存储不同类型
5. 简化版function<R(Args...)>实现

### 设计思路
1. 抽象基类CallableBase，虚函数call
2. 具体派生类CallableImpl<F>存储具体函数对象
3. Function类持有CallableBase指针
4. 模板构造函数从任意可调用对象创建CallableImpl
5. operator()调用call

### 关键问题
- 为什么要堆分配：不同F类型大小不同
- 小对象优化：std::function有小缓冲区优化避免new
- 拷贝语义：需要实现拷贝/移动
- 函数签名：返回值和参数类型是Function类的模板参数

### 代码实现
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <utility>

template<typename Signature>
class Function;

template<typename R, typename... Args>
class Function<R(Args...)> {
    struct CallableBase {
        virtual R call(Args... args) = 0;
        virtual std::unique_ptr<CallableBase> clone() const = 0;
        virtual ~CallableBase() = default;
    };

    template<typename F>
    struct CallableImpl : CallableBase {
        F func;
        CallableImpl(F f) : func(std::move(f)) {}
        R call(Args... args) override {
            return func(std::forward<Args>(args)...);
        }
        std::unique_ptr<CallableBase> clone() const override {
            return std::make_unique<CallableImpl<F>>(func);
        }
    };

    std::unique_ptr<CallableBase> impl_;

public:
    Function() = default;

    template<typename F>
    Function(F f) : impl_(std::make_unique<CallableImpl<F>>(std::move(f))) {}

    Function(const Function& other) {
        if (other.impl_) impl_ = other.impl_->clone();
    }

    Function(Function&& other) noexcept = default;

    Function& operator=(const Function& other) {
        if (this != &other) {
            impl_ = other.impl_ ? other.impl_->clone() : nullptr;
        }
        return *this;
    }

    Function& operator=(Function&& other) noexcept = default;

    R operator()(Args... args) const {
        if (!impl_) throw std::runtime_error("Empty function");
        return impl_->call(std::forward<Args>(args)...);
    }

    explicit operator bool() const { return impl_ != nullptr; }
};

int add(int a, int b) { return a + b; }

struct Multiply {
    int operator()(int a, int b) const { return a * b; }
};

int main() {
    Function<int(int, int)> f1 = add;
    std::cout << "add(3, 4) = " << f1(3, 4) << std::endl;

    Function<int(int, int)> f2 = Multiply{};
    std::cout << "multiply(3, 4) = " << f2(3, 4) << std::endl;

    int factor = 10;
    Function<int(int)> f3 = [factor](int x) { return x * factor; };
    std::cout << "lambda(5) = " << f3(5) << std::endl;

    Function<std::string(const std::string&)> f4 = [](const std::string& s) {
        return "Hello, " + s + "!";
    };
    std::cout << f4("World") << std::endl;

    Function<void()> f5 = [] { std::cout << "No args, no return" << std::endl; };
    f5();

    return 0;
}
```""")

# 47. 简单内存池
add("实现一个固定大小块的内存池（Memory Pool），比默认new/delete更快分配固定大小对象，减少内存碎片，适用于频繁分配销毁小对象的场景，演示池的性能优势。",
"""### 需求分析
固定大小内存池：
1. 预分配一大块内存
2. 划分为固定大小块
3. 空闲块用链表管理（free list）
4. 分配时取表头，释放时放回链表
5. 比malloc/free快，减少碎片

### 设计思路
1. MemoryPool类，块大小block_size
2. 分配时如果free list空，向系统申请一个大chunk并切分为块
3. 块的前几个字节作为next指针（复用空闲块内存）
4. allocate从free list取头，deallocate放回free list
5. 支持模板封装operator new/delete

### 关键问题
- 块大小至少能放下指针（next）
- 对齐：块地址要适当对齐
- 扩容：池可以动态增加新chunk
- 不要混用：从池分配必须用池释放
- 性能：O(1)分配和释放

### 代码实现
```cpp
#include <iostream>
#include <vector>
#include <chrono>
#include <cstddef>

class PoolAllocator {
    struct Block { Block* next; };
    size_t blockSize_;
    Block* freeList_ = nullptr;
    std::vector<void*> chunks_;
    static const size_t CHUNK_SIZE = 1024;

public:
    explicit PoolAllocator(size_t blockSize)
        : blockSize_(blockSize < sizeof(Block*) ? sizeof(Block*) : blockSize) {}

    ~PoolAllocator() {
        for (void* chunk : chunks_) ::operator delete(chunk);
    }

    void* allocate() {
        if (!freeList_) {
            size_t chunkBytes = blockSize_ * CHUNK_SIZE;
            char* chunk = static_cast<char*>(::operator new(chunkBytes));
            chunks_.push_back(chunk);
            for (size_t i = 0; i < CHUNK_SIZE; ++i) {
                Block* b = reinterpret_cast<Block*>(chunk + i * blockSize_);
                b->next = freeList_;
                freeList_ = b;
            }
        }
        Block* b = freeList_;
        freeList_ = b->next;
        return b;
    }

    void deallocate(void* p) {
        if (!p) return;
        Block* b = static_cast<Block*>(p);
        b->next = freeList_;
        freeList_ = b;
    }

    PoolAllocator(const PoolAllocator&) = delete;
    PoolAllocator& operator=(const PoolAllocator&) = delete;
};

struct ListNode {
    int value;
    ListNode* next;
    static PoolAllocator pool;

    static void* operator new(size_t) { return pool.allocate(); }
    static void operator delete(void* p) { pool.deallocate(p); }
};

PoolAllocator ListNode::pool(sizeof(ListNode));

int main() {
    const int N = 1000000;

    std::cout << "=== Allocating " << N << " ListNodes ===" << std::endl;

    auto start1 = std::chrono::high_resolution_clock::now();
    std::vector<ListNode*> nodes;
    nodes.reserve(N);
    for (int i = 0; i < N; ++i) {
        nodes.push_back(new ListNode{i, nullptr});
    }
    auto end1 = std::chrono::high_resolution_clock::now();
    auto poolTime = std::chrono::duration<double, std::milli>(end1 - start1).count();

    for (auto* n : nodes) delete n;
    nodes.clear();

    std::cout << "Pool allocation time: " << poolTime << "ms" << std::endl;

    auto start2 = std::chrono::high_resolution_clock::now();
    class DefaultNode { public: int value; void* next; };
    for (int i = 0; i < N; ++i) {
        nodes.push_back(reinterpret_cast<ListNode*>(new DefaultNode{i, nullptr}));
    }
    auto end2 = std::chrono::high_resolution_clock::now();
    auto defaultTime = std::chrono::duration<double, std::milli>(end2 - start2).count();

    std::cout << "Default new/delete time: " << defaultTime << "ms" << std::endl;

    for (auto* n : nodes) delete (reinterpret_cast<DefaultNode*>(n));

    std::cout << "Pool speedup: " << defaultTime / poolTime << "x" << std::endl;
    return 0;
}
```""")

# 48. 模板方法模式
add("实现模板方法设计模式，在抽象基类中定义算法骨架，具体步骤由子类实现，实现一个数据处理器：读取->解析->处理->保存，不同文件格式（CSV、JSON）实现各自的解析和保存方法。",
"""### 需求分析
模板方法模式：
1. 基类定义算法固定骨架
2. 某些步骤延迟到子类实现
3. 钩子方法提供可选扩展
4. 父类控制流程，子类填充细节
5. 数据处理流程示例

### 设计思路
1. DataProcessor抽象基类定义process模板方法
2. process固定流程：read->parse->process->save
3. parse和save是纯虚函数，子类实现
4. read可以是共同步骤
5. CsvProcessor和JsonProcessor具体实现

### 关键问题
- 为什么叫模板方法：C++模板无关，而是算法模板
- 好莱坞原则：不要调用我们，我们调用你（父类调用子类实现）
- 钩子：子类可以选择覆盖的虚函数（不是纯虚函数，有默认实现）
- 策略vs模板方法：策略用组合，模板方法用继承

### 代码实现
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <fstream>
#include <sstream>

class DataProcessor {
public:
    void process(const std::string& filename) {
        std::cout << "======== Processing " << filename << " ========" << std::endl;
        std::string rawData = readFile(filename);
        std::cout << "[1] Read " << rawData.size() << " bytes" << std::endl;

        auto data = parseData(rawData);
        std::cout << "[2] Parsed " << data.size() << " records" << std::endl;

        auto processed = processData(data);
        std::cout << "[3] Processed " << processed.size() << " records" << std::endl;

        saveData(processed, filename + ".out");
        std::cout << "[4] Saved output\\n" << std::endl;
    }

    virtual ~DataProcessor() = default;

protected:
    std::string readFile(const std::string& filename) {
        return "simulated raw data from " + filename;
    }

    virtual std::vector<std::vector<std::string>> parseData(const std::string& raw) = 0;

    virtual std::vector<std::vector<std::string>> processData(std::vector<std::vector<std::string>> data) {
        for (auto& row : data) {
            for (auto& field : row) {
                field = "[" + field + "]";
            }
        }
        return data;
    }

    virtual void saveData(const std::vector<std::vector<std::string>>& data, const std::string& outFile) = 0;
};

class CsvProcessor : public DataProcessor {
protected:
    std::vector<std::vector<std::string>> parseData(const std::string& raw) override {
        std::cout << "    CSV parsing..." << std::endl;
        return {{"Name", "Age"}, {"Alice", "30"}, {"Bob", "25"}};
    }

    void saveData(const std::vector<std::vector<std::string>>& data, const std::string& outFile) override {
        std::cout << "    Saving as CSV to " << outFile << std::endl;
    }
};

class JsonProcessor : public DataProcessor {
protected:
    std::vector<std::vector<std::string>> parseData(const std::string& raw) override {
        std::cout << "    JSON parsing..." << std::endl;
        return {{"key", "value"}, {"id", "123"}, {"status", "ok"}};
    }

    void saveData(const std::vector<std::vector<std::string>>& data, const std::string& outFile) override {
        std::cout << "    Saving as JSON to " << outFile << std::endl;
    }

    std::vector<std::vector<std::string>> processData(std::vector<std::vector<std::string>> data) override {
        std::cout << "    [JSON hook] Adding metadata fields..." << std::endl;
        data.push_back({"processed_by", "JsonProcessor"});
        return DataProcessor::processData(std::move(data));
    }
};

int main() {
    CsvProcessor csv;
    csv.process("data.csv");

    JsonProcessor json;
    json.process("data.json");

    return 0;
}
```""")

# 49. 异步任务调度器
add("实现一个简单的定时任务调度器，支持一次性延时任务和周期性重复任务，使用优先队列按下次执行时间排序，工作线程等待并执行到期任务。",
"""### 需求分析
定时任务调度器：
1. 延时执行任务：多少毫秒后执行
2. 重复任务：按固定间隔重复执行
3. 优先队列按下次执行时间排序
4. 工作线程等待到下一个任务时间
5. 支持取消任务

### 设计思路
1. Task结构体包含：执行时间、周期、回调函数、是否取消
2. 优先队列（最小堆）按执行时间最早在前
3. mutex保护队列
4. 条件变量等待，新任务插入时唤醒
5. 循环获取最顶任务，时间到执行，重复任务重新入队

### 关键问题
- 时间更新：重复任务执行后计算next run time
- 取消：标记cancelled，执行前检查
- 时钟调整：使用steady_clock避免系统时间调整影响
- 时钟跳跃：新任务比当前等待的更早执行需要唤醒线程

### 代码实现
```cpp
#include <iostream>
#include <queue>
#include <functional>
#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <memory>

using Clock = std::chrono::steady_clock;
using TimePoint = Clock::time_point;

struct ScheduledTask {
    TimePoint nextRun;
    std::chrono::milliseconds period;
    std::function<void()> callback;
    bool cancelled = false;
    int id;

    bool operator>(const ScheduledTask& other) const {
        return nextRun > other.nextRun;
    }
};

class TaskScheduler {
    std::priority_queue<ScheduledTask, std::vector<ScheduledTask>, std::greater<ScheduledTask>> tasks_;
    std::mutex mutex_;
    std::condition_variable cv_;
    std::atomic<bool> running_{false};
    std::thread worker_;
    int nextId_ = 1;

    void run() {
        while (running_) {
            std::function<void()> task;
            {
                std::unique_lock<std::mutex> lock(mutex_);
                if (tasks_.empty()) {
                    cv_.wait(lock, [this] { return !tasks_.empty() || !running_; });
                    if (!running_) return;
                }

                auto now = Clock::now();
                auto& top = tasks_.top();
                if (top.nextRun > now) {
                    cv_.wait_until(lock, top.nextRun);
                    continue;
                }

                auto t = top;
                tasks_.pop();
                if (t.cancelled) continue;

                task = t.callback;
                if (t.period.count() > 0) {
                    t.nextRun = now + t.period;
                    tasks_.push(t);
                }
            }
            if (task) task();
        }
    }

public:
    void start() {
        running_ = true;
        worker_ = std::thread([this] { run(); });
    }

    void stop() {
        running_ = false;
        cv_.notify_all();
        if (worker_.joinable()) worker_.join();
    }

    int scheduleOnce(std::chrono::milliseconds delay, std::function<void()> cb) {
        std::lock_guard<std::mutex> lock(mutex_);
        int id = nextId_++;
        tasks_.push({Clock::now() + delay, std::chrono::milliseconds(0), cb, false, id});
        cv_.notify_all();
        return id;
    }

    int scheduleRepeating(std::chrono::milliseconds period, std::function<void()> cb) {
        std::lock_guard<std::mutex> lock(mutex_);
        int id = nextId_++;
        tasks_.push({Clock::now() + period, period, cb, false, id});
        cv_.notify_all();
        return id;
    }

    ~TaskScheduler() { if (running_) stop(); }
};

int main() {
    TaskScheduler scheduler;
    scheduler.start();

    std::cout << "Scheduler started" << std::endl;

    scheduler.scheduleOnce(std::chrono::milliseconds(500), [] {
        std::cout << "[0.5s] One-time task executed!" << std::endl;
    });

    scheduler.scheduleOnce(std::chrono::milliseconds(2000), [] {
        std::cout << "[2.0s] Delayed announcement" << std::endl;
    });

    int count = 0;
    int repeatId = scheduler.scheduleRepeating(std::chrono::milliseconds(1000), [&count] {
        count++;
        std::cout << "[1s tick] Repeat task #" << count << std::endl;
    });

    std::this_thread::sleep_for(std::chrono::milliseconds(4500));

    std::cout << "Stopping scheduler..." << std::endl;
    scheduler.stop();
    std::cout << "Scheduler stopped" << std::endl;

    return 0;
}
```""")

# 50. 备忘录模式
add("实现备忘录设计模式（Memento），保存和恢复对象的历史状态，支持撤销功能，实现一个文本编辑器的历史记录，保存多次快照并可以回退到任意历史状态，类似编辑器的撤销/重做。",
"""### 需求分析
备忘录模式：
1. 保存对象内部状态（快照）
2. 不破坏封装
3. 之后可以恢复到该状态
4. Caretaker管理备忘录历史
5. 编辑器撤销/重做示例

### 设计思路
1. Memento类存储Editor状态（文本、光标位置）
2. Originator（Editor）创建和恢复备忘录
3. Caretaker（History）维护备忘录栈
4. 保存：createMemento并入栈
5. 撤销：弹出Memento，restore

### 关键问题
- 封装：Memento接口窄，只有Originator能访问内部状态（C++用friend或接口隔离）
- 内存：历史记录可能很大，可以限制保存数量
- 深拷贝：备忘录要完全拷贝状态
- vs命令模式：命令保存要执行的反向操作，备忘录保存状态快照

### 代码实现
```cpp
#include <iostream>
#include <string>
#include <stack>
#include <memory>
#include <fstream>

class EditorMemento {
    std::string text;
    size_t cursorPos;
    EditorMemento(std::string t, size_t pos) : text(std::move(t)), cursorPos(pos) {}
    friend class TextEditor;
public:
    size_t getCursor() const { return cursorPos; }
    const std::string& getText() const { return text; }
};

class TextEditor {
    std::string text;
    size_t cursor = 0;
public:
    void type(const std::string& s) {
        text.insert(cursor, s);
        cursor += s.size();
    }

    void backspace() {
        if (cursor > 0) {
            text.erase(cursor - 1, 1);
            cursor--;
        }
    }

    void moveCursor(size_t pos) {
        cursor = std::min(pos, text.size());
    }

    std::shared_ptr<EditorMemento> save() const {
        return std::shared_ptr<EditorMemento>(new EditorMemento(text, cursor));
    }

    void restore(const std::shared_ptr<EditorMemento>& m) {
        text = m->text;
        cursor = m->cursorPos;
    }

    void print() const {
        std::cout << "Text: \"" << text << "\" (cursor at " << cursor << ")" << std::endl;
    }
};

class History {
    std::stack<std::shared_ptr<EditorMemento>> undoStack;
    std::stack<std::shared_ptr<EditorMemento>> redoStack;
public:
    void push(std::shared_ptr<EditorMemento> m) {
        undoStack.push(m);
        while (!redoStack.empty()) redoStack.pop();
    }

    std::shared_ptr<EditorMemento> undo() {
        if (undoStack.size() <= 1) return nullptr;
        auto current = undoStack.top();
        undoStack.pop();
        redoStack.push(current);
        return undoStack.top();
    }

    std::shared_ptr<EditorMemento> redo() {
        if (redoStack.empty()) return nullptr;
        auto m = redoStack.top();
        redoStack.pop();
        undoStack.push(m);
        return m;
    }
};

int main() {
    TextEditor editor;
    History history;

    std::cout << "=== Typing with auto-save ===" << std::endl;
    history.push(editor.save());
    editor.type("Hello");
    editor.print();

    history.push(editor.save());
    editor.type(" World");
    editor.print();

    history.push(editor.save());
    editor.type("!!!");
    editor.print();

    std::cout << "\\n=== Undo twice ===" << std::endl;
    if (auto m = history.undo()) { editor.restore(m); editor.print(); }
    if (auto m = history.undo()) { editor.restore(m); editor.print(); }

    std::cout << "\\n=== Redo once ===" << std::endl;
    if (auto m = history.redo()) { editor.restore(m); editor.print(); }

    std::cout << "\\n=== Backspace and type more ===" << std::endl;
    history.push(editor.save());
    editor.backspace();
    editor.print();

    history.push(editor.save());
    editor.type("?");
    editor.print();

    std::cout << "\\n=== Final undo ===" << std::endl;
    if (auto m = history.undo()) { editor.restore(m); editor.print(); }

    return 0;
}
```""")

print(f"Total entries generated: {len(all_entries)}")

# 写入最终文件
output_path = "f:/数据集/doubao/cot_data/cpp/cpp_cot_3.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_entries, f, ensure_ascii=False, indent=2)

print(f"Successfully wrote {len(all_entries)} entries to {output_path}")

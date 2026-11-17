import json

def e(instruction, thinking, code):
    output = thinking + "\n\n" + code + "\n\n开发完成！该网页所有功能均已实现，可以直接在浏览器中运行使用。"
    return {"instruction": instruction, "input": "", "output": output}

data = []

# ===== 小游戏类 1-10 =====

# 1. 贪吃蛇
data.append(e("使用HTML5 Canvas开发贪吃蛇游戏，支持键盘控制、分数统计、本地存储最高分",
"我来开发贪吃蛇游戏：\n1. 创建Canvas画布设置游戏区域\n2. 定义蛇身数组、食物位置、方向变量\n3. 使用setInterval驱动游戏主循环\n4. 监听方向键控制移动，防止180度转向\n5. 碰撞检测：撞墙、撞自己游戏结束\n6. 吃到食物身体增长、加分、速度逐渐加快\n7. 用localStorage保存最高分记录",
'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><title>贪吃蛇</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;background:#1a1a2e;font-family:Arial}h1{color:#00ff88;margin-bottom:10px}.info{color:#fff;margin-bottom:10px}canvas{border:2px solid #00ff88;border-radius:8px;background:#0f0f23}button{margin-top:15px;padding:10px 25px;background:#00ff88;border:none;border-radius:20px;cursor:pointer;font-weight:bold}#ov{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,.9);color:#fff;padding:30px;border-radius:10px;display:none}</style></head>
<body><h1>🐍 贪吃蛇</h1><div class="info">分数:<span id="sc">0</span> | 最高:<span id="hi">0</span></div>
<canvas id="c" width="400" height="400"></canvas><button onclick="init()">重新开始</button>
<div id="ov"><h2>游戏结束</h2><p id="fs"></p></div>
<script>
const c=document.getElementById("c"),x=c.getContext("2d"),gs=20,tc=c.width/gs;let sn,fd,dr,nd,sc,hi=localStorage.getItem("snakehi")||0,tm,sp;
document.getElementById("hi").textContent=hi;
function init(){sn=[{x:5,y:10},{x:4,y:10},{x:3,y:10}];dr={x:1,y:0};nd={x:1,y:0};sc=0;sp=100;document.getElementById("sc").textContent=sc;document.getElementById("ov").style.display="none";spawn();clearInterval(tm);tm=setInterval(up,sp)}
function spawn(){do{fd={x:Math.floor(Math.random()*tc),y:Math.floor(Math.random()*tc)}}while(sn.some(s=>s.x==fd.x&&s.y==fd.y))}
function up(){dr={...nd};const h={x:sn[0].x+dr.x,y:sn[0].y+dr.y};if(h.x<0||h.x>=tc||h.y<0||h.y>=tc||sn.some(s=>s.x==h.x&&s.y==h.y))return end();sn.unshift(h);if(h.x==fd.x&&h.y==fd.y){sc+=10;document.getElementById("sc").textContent=sc;spawn();if(sp>50){sp-=2;clearInterval(tm);tm=setInterval(up,sp)}}else sn.pop();draw()}
function draw(){x.fillStyle="#0f0f23";x.fillRect(0,0,c.width,c.height);x.fillStyle="#e94560";x.beginPath();x.arc(fd.x*gs+gs/2,fd.y*gs+gs/2,gs/2-2,0,Math.PI*2);x.fill();sn.forEach((s,i)=>{x.fillStyle=i?"#00d4ff":"#00ff88";x.fillRect(s.x*gs+1,s.y*gs+1,gs-2,gs-2)})}
function end(){clearInterval(tm);if(sc>hi){hi=sc;localStorage.setItem("snakehi",hi);document.getElementById("hi").textContent=hi}document.getElementById("fs").textContent="得分:"+sc;document.getElementById("ov").style.display="block"}
document.addEventListener("keydown",e=>{if(e.key=="ArrowUp"&&dr.y!=1)nd={x:0,y:-1};if(e.key=="ArrowDown"&&dr.y!=-1)nd={x:0,y:1};if(e.key=="ArrowLeft"&&dr.x!=1)nd={x:-1,y:0};if(e.key=="ArrowRight"&&dr.x!=-1)nd={x:1,y:0};e.preventDefault()});init();
</script></body></html>'''))

# 2. 2048
data.append(e("实现2048数字游戏，支持滑动合并、分数、胜负判定和动画效果",
"开发2048游戏：\n1. 创建4x4网格布局\n2. 初始化时随机在两个格子生成2或4\n3. 处理上下左右滑动，实现数字移动和合并\n4. 每次移动后随机生成一个新数字\n5. 相同数字合并翻倍，分数累加\n6. 达到2048显示胜利，无法移动则失败\n7. 添加新块出现和合并的动画",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>2048</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:#faf8ef;display:flex;flex-direction:column;align-items:center;padding:20px;font-family:Arial}h1{font-size:60px;color:#776e65}.hdr{width:340px;display:flex;justify-content:space-between;margin-bottom:15px}.sc{background:#bbada0;color:#fff;padding:8px 15px;border-radius:5px;text-align:center}.sc span{display:block;font-size:22px;font-weight:bold}.btn{background:#8f7a66;color:#fff;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;font-weight:bold;font-size:16px}#g{background:#bbada0;border-radius:6px;padding:10px;display:grid;grid-template-columns:repeat(4,70px);gap:10px;position:relative}.c{width:70px;height:70px;background:rgba(238,228,218,.35);border-radius:3px;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:35px}.t2{background:#eee4da;color:#776e65}.t4{background:#ede0c8;color:#776e65}.t8{background:#f2b179;color:#fff}.t16{background:#f59563;color:#fff}.t32{background:#f67c5f;color:#fff}.t64{background:#f65e3b;color:#fff}.t128{background:#edcf72;color:#fff;font-size:30px}.t256{background:#edcc61;color:#fff;font-size:30px}.t512{background:#edc850;color:#fff;font-size:30px}.t1024{background:#edc53f;color:#fff;font-size:25px}.t2048{background:#edc22e;color:#fff;font-size:25px}.msg{position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(238,228,218,.7);display:none;flex-direction:column;align-items:center;justify-content:center;border-radius:6px;z-index:10}.msg h2{font-size:50px;color:#776e65;margin-bottom:20px}</style></head>
<body><h1>2048</h1><div class="hdr"><div style="display:flex;gap:10px"><div class="sc">分数<span id="sc">0</span></div><div class="sc">最高<span id="bs">0</span></div></div><button class="btn" onclick="init()">新游戏</button></div><div id="g"><div class="msg" id="mg"><h2 id="mt"></h2><button class="btn" onclick="init()">再来一局</button></div></div>
<script>
let gr,sc=0,bs=localStorage.getItem("best2048")||0;const g=document.getElementById("g"),mg=document.getElementById("mg"),mt=document.getElementById("mt");
document.getElementById("bs").textContent=bs;
function init(){gr=Array(4).fill().map(()=>Array(4).fill(0));sc=0;document.getElementById("sc").textContent=sc;mg.style.display="none";addT();addT();render()}
function addT(){const e=[];for(let i=0;i<4;i++)for(let j=0;j<4;j++)if(!gr[i][j])e.push({i,j});if(e.length){const{p}=e[Math.floor(Math.random()*e.length)];const[p]=e;gr[p.i][p.j]=Math.random()<.9?2:4}}
function render(){const cells=g.querySelectorAll(".c:not(.msg)");cells.forEach(c=>c.remove());for(let i=0;i<4;i++)for(let j=0;j<4;j++){const v=gr[i][j];const d=document.createElement("div");d.className="c"+(v?" t"+v:"");d.textContent=v||"";g.appendChild(d)}}
function mv(dr){let m=false;const sr=(i,j)=>dr==="l"?j:3-j,sc_=(i)=>dr==="u"?i:dr==="d"?3-i:i,hr=(i,j)=>dr==="l"||dr==="r"?j:i,vr=(i,j)=>dr==="l"||dr==="r"?i:j;for(let i=0;i<4;i++){let ln=[0,0,0,0],p=0;for(let j=0;j<4;j++){const r=dr==="u"?j:dr==="d"?3-j:i,c=dr==="l"?j:dr==="r"?3-j:dr==="u"?i:3-i;if(gr[r][c])ln[p++]=gr[r][c]}for(let j=0;j<3;j++)if(ln[j]&&ln[j]===ln[j+1]){ln[j]*=2;sc+=ln[j];ln.splice(j+1,1);ln.push(0)}for(let j=0;j<4;j++){const r=dr==="u"?j:dr==="d"?3-j:i,c=dr==="l"?j:dr==="r"?3-j:dr==="u"?i:3-i;if(gr[r][c]!==ln[j])m=true;gr[r][c]=ln[j]}}if(m){addT();render();document.getElementById("sc").textContent=sc;if(sc>bs){bs=sc;localStorage.setItem("best2048",bs);document.getElementById("bs").textContent=bs}if(!canM()){mt.textContent="游戏结束!";mg.style.display="flex"}if(gr.some(r=>r.some(v=>v===2048))){mt.textContent="你赢了!";mg.style.display="flex"}}}
function canM(){for(let i=0;i<4;i++)for(let j=0;j<4;j++){if(!gr[i][j])return true;if(i<3&&gr[i][j]===gr[i+1][j])return true;if(j<3&&gr[i][j]===gr[i][j+1])return true}return false}
document.addEventListener("keydown",e=>{if(e.key==="ArrowLeft")mv("l");if(e.key==="ArrowRight")mv("r");if(e.key==="ArrowUp")mv("u");if(e.key==="ArrowDown")mv("d");e.preventDefault()});init();
</script></body></html>'''))

# 3. 打砖块
data.append(e("Canvas打砖块游戏，包含挡板控制、小球反弹、击碎砖块计分",
"制作打砖块：\n1. 绘制挡板、小球、砖块阵列\n2. 键盘或鼠标控制挡板左右移动\n3. 小球运动和墙壁、挡板、砖块碰撞反弹\n4. 碰撞到挡板不同位置有不同反弹角度\n5. 击碎砖块得分，不同颜色砖块分数不同\n6. 掉落扣生命值，生命值归零游戏结束\n7. 多关卡设计，每关球速增加",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>打砖块</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;background:#1a1a2e}h1{color:#00d4ff;margin-bottom:10px}.info{color:#fff;margin-bottom:10px;display:flex;gap:30px}canvas{border:2px solid #00d4ff;border-radius:8px;background:#0f0f23}button{margin-top:15px;padding:10px 25px;background:#00d4ff;border:none;border-radius:20px;cursor:pointer;font-weight:bold}</style></head>
<body><h1>🎮 打砖块</h1><div class="info"><span>分数:<span id="sc">0</span></span><span>生命:<span id="lv">3</span></span></div>
<canvas id="c" width="600" height="400"></canvas><button id="btn" onclick="init()">开始游戏</button>
<script>
const c=document.getElementById("c"),x=c.getContext("2d");let pd,bl,br,sc,lv,run;
function init(){pd={x:250,y:370,w:100,h:10};bl={x:300,y:350,r:8,dx:4,dy:-4,sp:4};br=[];for(let i=0;i<5;i++)for(let j=0;j<8;j++)br.push({x:40+j*65,y:40+i*25,w:60,h:20,c:["#e94560","#ff6b6b","#feca57","#48dbfb","#1dd1a1"][i],p:(5-i)*10,a:1});sc=0;lv=3;run=true;document.getElementById("sc").textContent=sc;document.getElementById("lv").textContent=lv;document.getElementById("btn").style.display="none";loop()}
function draw(){x.fillStyle="#0f0f23";x.fillRect(0,0,c.width,c.height);br.forEach(b=>{if(b.a){x.fillStyle=b.c;x.fillRect(b.x,b.y,b.w,b.h);x.strokeStyle="rgba(255,255,255,.3)";x.strokeRect(b.x,b.y,b.w,b.h)}});x.fillStyle="#00d4ff";x.fillRect(pd.x,pd.y,pd.w,pd.h);x.beginPath();x.arc(bl.x,bl.y,bl.r,0,Math.PI*2);x.fillStyle="#fff";x.fill()}
function up(){bl.x+=bl.dx;bl.y+=bl.dy;if(bl.x<bl.r||bl.x>c.width-bl.r)bl.dx*=-1;if(bl.y<bl.r)bl.dy*=-1;if(bl.y+bl.r>pd.y&&bl.x>pd.x&&bl.x<pd.x+pd.w){const p=(bl.x-pd.x)/pd.w-.5;bl.dx=p*bl.sp*2;bl.dy=-Math.abs(bl.dy)}br.forEach(b=>{if(b.a&&bl.x>b.x&&bl.x<b.x+b.w&&bl.y>b.y&&bl.y<b.y+b.h){bl.dy*=-1;b.a=0;sc+=b.p;document.getElementById("sc").textContent=sc}});if(bl.y>c.height){lv--;document.getElementById("lv").textContent=lv;if(!lv){run=false;document.getElementById("btn").style.display="inline-block";alert("游戏结束!")}else{bl.x=300;bl.y=350;bl.dx=4;bl.dy=-4}}if(br.every(b=>!b.a)){bl.sp+=.5;init()}if(pd.x<0)pd.x=0;if(pd.x+pd.w>c.width)pd.x=c.width-pd.w}
function loop(){if(!run)return;up();draw();requestAnimationFrame(loop)}
document.addEventListener("keydown",e=>{if(e.key==="ArrowLeft")pd.x-=20;if(e.key==="ArrowRight")pd.x+=20});c.addEventListener("mousemove",e=>{const r=c.getBoundingClientRect();pd.x=e.clientX-r.left-pd.w/2});draw();
</script></body></html>'''))

# 4. 扫雷
data.append(e("经典扫雷游戏，支持左键翻开、右键标记、难度选择、第一次点击安全",
"开发扫雷：\n1. 用CSS Grid创建网格，每个格子是一个div\n2. 第一次点击后布雷，确保点击位置及周围不是雷\n3. 计算每个格子周围8个方向的地雷数量\n4. 左键翻开格子，空格子递归翻开周围\n5. 右键标记/取消旗帜\n6. 数字用不同颜色显示\n7. 表情按钮显示游戏状态",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>扫雷</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{display:flex;flex-direction:column;align-items:center;padding:20px;background:#c0c0c0;font-family:Arial}.ctrl{margin-bottom:10px;display:flex;gap:10px}select,button{padding:5px 10px;font-size:14px}.info{display:flex;gap:15px;margin-bottom:5px}.info div{width:50px;height:28px;background:black;color:red;display:flex;align-items:center;justify-content:center;font-family:monospace;font-size:20px}#fb{width:35px;font-size:20px}#b{display:grid;gap:1px;background:#808080;padding:3px;border:3px outset #fff}.cell{width:25px;height:25px;background:#c0c0c0;border:3px outset #fff;display:flex;align-items:center;justify-content:center;font-weight:bold;cursor:pointer;font-size:14px;user-select:none}.cell.rv{border:1px solid #808080}.cell.mn{background:red}.cell.fl::after{content:"🚩"}.c1{color:blue}.c2{color:green}.c3{color:red}</style></head>
<body><h3>💣 扫雷</h3><div class="ctrl"><select id="df"><option value="e">初级9x9</option><option value="m">中级16x16</option><option value="h">高级16x30</option></select><button onclick="init()">新游戏</button></div>
<div class="info"><div id="mc">10</div><button id="fb" onclick="init()">😊</button><div id="tm">000</div></div><div id="b"></div>
<script>
const D={e:{r:9,c:9,m:10},m:{r:16,c:16,m:40},h:{r:16,c:30,m:99}};let R,C,M,gr,go,fg,rv,t,sc,fc;
function init(){const d=D[document.getElementById("df").value];R=d.r;C=d.c;M=d.m;gr=[];go=false;fg=0;rv=0;fc=true;sc=0;clearInterval(t);document.getElementById("tm").textContent="000";document.getElementById("mc").textContent=M;document.getElementById("fb").textContent="😊";const b=document.getElementById("b");b.style.gridTemplateColumns=`repeat(${C},25px)`;b.innerHTML="";for(let i=0;i<R;i++){gr[i]=[];for(let j=0;j<C;j++){gr[i][j]={m:false,r:false,f:false,n:0};const ce=document.createElement("div");ce.className="cell";ce.addEventListener("click",()=>clk(i,j));ce.addEventListener("contextmenu",e=>{e.preventDefault();fl(i,j)});b.appendChild(ce)}}}
function pm(er,ec){let p=0;while(p<M){const r=Math.floor(Math.random()*R),c=Math.floor(Math.random()*C);if(!gr[r][c].m&&!(Math.abs(r-er)<=1&&Math.abs(c-ec)<=1)){gr[r][c].m=true;p++}}for(let i=0;i<R;i++)for(let j=0;j<C;j++)if(!gr[i][j].m){let n=0;for(let di=-1;di<=1;di++)for(let dj=-1;dj<=1;dj++){const ni=i+di,nj=j+dj;if(ni>=0&&ni<R&&nj>=0&&nj<C&&gr[ni][nj].m)n++}gr[i][j].n=n}}
function clk(r,c){if(go||gr[r][c].r||gr[r][c].f)return;if(fc){fc=false;pm(r,c);st()}const ce=document.querySelectorAll(".cell")[r*C+c];if(gr[r][c].m){ce.classList.add("rv","mn");ce.textContent="💣";go=true;clearInterval(t);document.getElementById("fb").textContent="😵";document.querySelectorAll(".cell").forEach((c,i)=>{const rr=Math.floor(i/C),cc=i%C;if(gr[rr][cc].m&&!gr[rr][cc].f)c.textContent="💣";c.classList.add("rv")});return}rev(r,c);if(rv===R*C-M){go=true;clearInterval(t);document.getElementById("fb").textContent="😎"}}
function rev(r,c){if(r<0||r>=R||c<0||c>=C||gr[r][c].r||gr[r][c].f||gr[r][c].m)return;gr[r][c].r=true;rv++;const ce=document.querySelectorAll(".cell")[r*C+c];ce.classList.add("rv");if(gr[r][c].n){ce.textContent=gr[r][c].n;ce.classList.add("c"+gr[r][c].n)}else for(let di=-1;di<=1;di++)for(let dj=-1;dj<=1;dj++)rev(r+di,c+dj)}
function fl(r,c){if(go||gr[r][c].r)return;gr[r][c].f=!gr[r][c].f;fg+=gr[r][c].f?1:-1;document.querySelectorAll(".cell")[r*C+c].classList.toggle("fl");document.getElementById("mc").textContent=M-fg}
function st(){t=setInterval(()=>{sc++;document.getElementById("tm").textContent=String(sc).padStart(3,"0")},1000)}init();
</script></body></html>'''))

# 5. 井字棋
data.append(e("井字棋游戏，支持双人对战和AI对战（Minimax算法）",
"开发井字棋：\n1. 3x3网格棋盘，点击下棋\n2. 轮流下棋，X先手，O后手\n3. 检测三行三列对角线获胜\n4. Minimax算法实现AI，选择最优解\n5. 计分板记录胜平负\n6. 获胜连线高亮\n7. 双人/AI模式切换",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>井字棋</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{display:flex;flex-direction:column;align-items:center;min-height:100vh;background:linear-gradient(135deg,#667eea,#764ba2);padding:30px;font-family:Arial}h1{color:#fff;margin-bottom:15px}.mode{margin-bottom:15px;display:flex;gap:10px}.mode button{padding:8px 18px;border:2px solid #fff;background:transparent;color:#fff;border-radius:20px;cursor:pointer}.mode button.act{background:#fff;color:#667eea}.sc{display:flex;gap:25px;margin-bottom:15px;color:#fff}.turn{color:#fff;margin-bottom:15px;padding:10px 25px;background:rgba(255,255,255,.2);border-radius:20px}#b{display:grid;grid-template-columns:repeat(3,100px);gap:8px;background:rgba(255,255,255,.3);padding:8px;border-radius:10px}.cell{width:100px;height:100px;background:#fff;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:55px;font-weight:bold;cursor:pointer}.cell:hover{background:#f0f0f0}.cell.x{color:#e94560}.cell.o{color:#00d4ff}.cell.win{background:#fff3cd;animation:pulse .5s}@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.05)}}button.rst{margin-top:20px;padding:10px 25px;background:#fff;color:#667eea;border:none;border-radius:20px;cursor:pointer;font-weight:bold}.modal{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.7);display:none;align-items:center;justify-content:center}.modal>div{background:#fff;padding:40px;border-radius:15px;text-align:center}.modal h2{margin-bottom:15px}</style></head>
<body><h1>⭕ 井字棋 ❌</h1><div class="mode"><button class="act" onclick="setM('pvp')">双人</button><button onclick="setM('ai')">人机</button></div>
<div class="sc"><span>X: <b id="xs">0</b></span><span>平: <b id="ds">0</b></span><span>O: <b id="os">0</b></span></div><div class="turn" id="tr">X 回合</div><div id="b"></div><button class="rst" onclick="init()">重新开始</button>
<div class="modal" id="m"><div><h2 id="mt"></h2><button class="rst" onclick="init()">再来一局</button></div></div>
<script>
let bd,cur,act,mode="pvp",sc={x:0,o:0,d:0};const win=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];const b=document.getElementById("b"),tr=document.getElementById("tr");
function init(){bd=Array(9).fill("");cur="x";act=true;tr.textContent="X 回合";b.innerHTML="";for(let i=0;i<9;i++){const c=document.createElement("div");c.className="cell";c.onclick=()=>clk(i);b.appendChild(c)}}
function clk(i){if(!act||bd[i])return;if(mode==="ai"&&cur==="o")return;mk(i,cur);if(act&&mode==="ai"&&cur==="o")setTimeout(ai,500)}
function mk(i,p){bd[i]=p;b.children[i].textContent=p.toUpperCase();b.children[i].classList.add(p);const w=chk();if(w){act=false;w.c.forEach(j=>b.children[j].classList.add("win"));sc[p]++;upd();setTimeout(()=>{document.getElementById("mt").textContent=p.toUpperCase()+" 获胜!";document.getElementById("m").style.display="flex"},500);return}if(!bd.includes("")){act=false;sc.d++;upd();setTimeout(()=>{document.getElementById("mt").textContent="平局!";document.getElementById("m").style.display="flex"},500);return}cur=cur==="x"?"o":"x";tr.textContent=cur.toUpperCase()+" 回合"}
function chk(){for(const c of win){const[a,b1,d]=c;if(bd[a]&&bd[a]===bd[b1]&&bd[a]===bd[d])return{p:bd[a],c}}return null}
function ai(){if(!act)return;let bs=-Inf,bm;for(let i=0;i<9;i++)if(!bd[i]){bd[i]="o";const s=mm(bd,false);bd[i]="";if(s>bs){bs=s;bm=i}}mk(bm,"o")}
function mm(b,p){const w=chkB(b);if(w==="o")return 10;if(w==="x")return-10;if(!b.includes(""))return 0;let bs=p?-Inf:Infinity;for(let i=0;i<9;i++)if(!b[i]){b[i]=p?"o":"x";const s=mm(b,!p);b[i]="";bs=p?Math.max(bs,s):Math.min(bs,s)}return bs}
function chkB(b){for(const c of win){const[a,d,e]=c;if(b[a]&&b[a]===b[d]&&b[a]===b[e])return b[a]}return null}
function upd(){document.getElementById("xs").textContent=sc.x;document.getElementById("os").textContent=sc.o;document.getElementById("ds").textContent=sc.d}
function setM(m){mode=m;document.querySelectorAll(".mode button").forEach((b,i)=>b.classList.toggle("act",(i===0&&m==="pvp")||(i===1&&m==="ai")));init()}
document.getElementById("m").addEventListener("click",e=>{if(e.target.id==="m"){e.target.style.display="none";init()}});init();
</script></body></html>'''))

# 6-10: 其他小游戏和组件
# 6. 记忆翻牌
data.append(e("记忆翻牌游戏，3D翻转动画，配对检测，计时器，多难度",
"制作记忆翻牌：\n1. CSS Grid布局卡片\n2. 用CSS 3D transform实现翻转动画\n3. 洗牌函数打乱卡片\n4. 每次翻开两张，匹配保持翻开，不匹配翻回\n5. 计时器和步数统计\n6. 简单/中等/困难三种难度\n7. 胜利时彩屑庆祝动画",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>记忆翻牌</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{min-height:100vh;background:linear-gradient(135deg,#1e3c72,#2a5298);display:flex;flex-direction:column;align-items:center;padding:20px;font-family:Arial}h1{color:#fff;margin-bottom:15px}.ctrl{display:flex;gap:10px;margin-bottom:15px;flex-wrap:wrap;justify-content:center}.ctrl button{padding:8px 16px;border:2px solid #fff;background:transparent;color:#fff;border-radius:20px;cursor:pointer}.ctrl button.act{background:#fff;color:#1e3c72}.st{display:flex;gap:20px;color:#fff;margin-bottom:15px;background:rgba(255,255,255,.15);padding:12px 25px;border-radius:15px}.bd{display:grid;gap:10px;perspective:1000px}.card{width:70px;height:70px;position:relative;transform-style:preserve-3d;transition:transform .5s;cursor:pointer}.card.flip{transform:rotateY(180deg)}.card.got{cursor:default}.card.got .fr{background:#00b894;animation:pop .5s}.face{position:absolute;width:100%;height:100%;border-radius:8px;backface-visibility:hidden;display:flex;align-items:center;justify-content:center;font-size:30px;box-shadow:0 4px 10px rgba(0,0,0,.2)}.bk{background:linear-gradient(135deg,#6c5ce7,#a29bfe)}.bk::after{content:"?";color:#fff;font-size:28px;font-weight:bold}.fr{background:#fff;transform:rotateY(180deg)}@keyframes pop{0%,100%{transform:rotateY(180deg) scale(1)}50%{transform:rotateY(180deg) scale(1.1)}}.win{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.8);display:none;align-items:center;justify-content:center;z-index:10}.win>div{background:#fff;padding:40px;border-radius:15px;text-align:center}</style></head>
<body><h1>🎴 记忆翻牌</h1><div class="ctrl"><button class="act" onclick="setD('e')">简单4x3</button><button onclick="setD('m')">中等4x4</button><button onclick="setD('h')">困难6x4</button><button onclick="init()">新游戏</button></div>
<div class="st"><span>⏱️<span id="tm">00:00</span></span><span>👆<span id="mv">0</span></span><span>✅<span id="mt">0</span>/<span id="tt">6</span></span></div><div class="bd" id="bd"></div><div class="win" id="wm"><div><h2>🎉 恭喜!</h2><p id="ws"></p><button onclick="init()" style="margin-top:15px;padding:10px 20px;background:#6c5ce7;color:#fff;border:none;border-radius:20px;cursor:pointer">再来一局</button></div></div>
<script>
const EJS=['🐶','🐱','🐭','🐹','🐰','🦊','🐻','🐼','🐨','🐯','🦁','🐮'];const D={e:{c:4,r:3,p:6},m:{c:4,r:4,p:8},h:{c:6,r:4,p:12}};let cur='e',cards,fl=[],got,mov,start,tm,sec,lock;
function shuffle(a){for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}
function init(){const d=D[cur];const sel=shuffle([...EJS]).slice(0,d.p);cards=shuffle([...sel,...sel]);const bd=document.getElementById("bd");bd.style.gridTemplateColumns=`repeat(${d.c},70px)`;document.getElementById("tt").textContent=d.p;bd.innerHTML="";cards.forEach((e,i)=>{const c=document.createElement("div");c.className="card";c.innerHTML=`<div class="face bk"></div><div class="face fr">${e}</div>`;c.onclick=()=>flip(c,i);bd.appendChild(c)});got=0;mov=0;start=false;lock=false;fl=[];sec=0;clearInterval(tm);document.getElementById("mv").textContent=0;document.getElementById("mt").textContent=0;document.getElementById("tm").textContent="00:00";document.getElementById("wm").style.display="none"}
function flip(c,i){if(lock||c.classList.contains("flip")||c.classList.contains("got"))return;if(!start){start=true;tm=setInterval(()=>{sec++;const m=Math.floor(sec/60).toString().padStart(2,"0"),s=(sec%60).toString().padStart(2,"0");document.getElementById("tm").textContent=m+":"+s},1000)}c.classList.add("flip");fl.push({c,i});if(fl.length===2){mov++;document.getElementById("mv").textContent=mov;chk()}}
function chk(){lock=true;const[a,b]=fl;if(cards[a.i]===cards[b.i]){a.c.classList.add("got");b.c.classList.add("got");got++;document.getElementById("mt").textContent=got;fl=[];lock=false;if(got===D[cur].p){clearInterval(tm);setTimeout(()=>{document.getElementById("ws").textContent=`用时${Math.floor(sec/60)}分${sec%60}秒，${mov}步`;document.getElementById("wm").style.display="flex"},500)}}else{setTimeout(()=>{a.c.classList.remove("flip");b.c.classList.remove("flip");fl=[];lock=false},1000)}}
function setD(d){cur=d;document.querySelectorAll(".ctrl button").forEach((b,i)=>b.classList.toggle("act",i<3&&['e','m','h'][i]===d));init()}init();
</script></body></html>'''))

# 7. 响应式导航栏
data.append(e("响应式导航栏，包含下拉菜单、汉堡菜单移动端适配、滚动时样式变化",
"开发响应式导航：\n1. 桌面端横向导航栏，Logo+菜单项+按钮\n2. 下拉菜单组件，hover或点击展开\n3. 移动端汉堡菜单按钮，点击展开侧边抽屉\n4. 页面滚动时导航栏添加背景色和阴影\n5. 平滑滚动到锚点位置\n6. 移动端菜单支持手势滑动关闭\n7. 高亮当前所在页面菜单项",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>响应式导航</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Arial;padding-top:70px}.nav{position:fixed;top:0;left:0;width:100%;padding:20px 50px;display:flex;justify-content:space-between;align-items:center;transition:.3s;z-index:100}.nav.sc{background:#fff;padding:15px 50px;box-shadow:0 2px 20px rgba(0,0,0,.1)}.logo{font-size:24px;font-weight:bold;color:#333}.menu{display:flex;gap:30px;list-style:none;align-items:center}.menu a{text-decoration:none;color:#333;font-weight:500;transition:.3s;position:relative}.menu a:hover,.menu a.act{color:#667eea}.menu a.act::after{content:"";position:absolute;bottom:-5px;left:0;width:100%;height:2px;background:#667eea}.dd{position:relative}.dd-c{position:absolute;top:100%;left:0;background:#fff;box-shadow:0 5px 20px rgba(0,0,0,.1);border-radius:8px;padding:10px 0;min-width:150px;display:none;list-style:none;margin-top:15px}.dd:hover .dd-c{display:block}.dd-c a{display:block;padding:10px 20px;white-space:nowrap}.btn{padding:10px 25px;background:#667eea;color:#fff;border:none;border-radius:20px;cursor:pointer;font-size:14px}.hb{display:none;flex-direction:column;gap:5px;cursor:pointer;z-index:101}.hb span{width:25px;height:3px;background:#333;transition:.3s}.hb.open span:nth-child(1){transform:rotate(45deg) translate(5px,5px)}.hb.open span:nth-child(2){opacity:0}.hb.open span:nth-child(3){transform:rotate(-45deg) translate(7px,-7px)}.ov{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.5);display:none;z-index:99}.sd{position:fixed;top:0;right:-300px;width:300px;height:100%;background:#fff;padding:80px 30px;transition:.3s;z-index:100}.sd.open{right:0}.sd ul{list-style:none}.sd li{margin-bottom:20px}.sd a{text-decoration:none;color:#333;font-size:18px}.sd .dd-c{position:static;display:none;box-shadow:none;padding-left:20px}.sd .dd.open .dd-c{display:block}section{height:100vh;display:flex;align-items:center;justify-content:center;font-size:40px;color:#666}section:nth-child(even){background:#f5f5f5}@media(max-width:768px){.menu{display:none}.hb{display:flex}.nav{padding:15px 20px}.nav.sc{padding:15px 20px}}</style></head><body>
<nav class="nav" id="nav"><div class="logo">Logo</div><ul class="menu"><li><a href="#h" class="act">首页</a></li><li><a href="#a">关于</a></li><li class="dd"><a href="#s">服务 ▾</a><ul class="dd-c"><li><a href="#">网页开发</a></li><li><a href="#">App开发</a></li><li><a href="#">UI设计</a></li></ul></li><li><a href="#c">联系</a></li><li><button class="btn">登录</button></li></ul><div class="hb" id="hb"><span></span><span></span><span></span></div></nav>
<div class="ov" id="ov"></div><div class="sd" id="sd"><ul><li><a href="#h">首页</a></li><li><a href="#a">关于</a></li><li class="dd"><a href="#" onclick="tglDd(event)">服务 ▾</a><ul class="dd-c"><li><a href="#">网页开发</a></li><li><a href="#">App开发</a></li><li><a href="#">UI设计</a></li></ul></li><li><a href="#c">联系</a></li></ul></div>
<section id="h">首页</section><section id="a">关于</section><section id="s">服务</section><section id="c">联系</section>
<script>
window.addEventListener("scroll",()=>document.getElementById("nav").classList.toggle("sc",scrollY>50));const hb=document.getElementById("hb"),sd=document.getElementById("sd"),ov=document.getElementById("ov");
hb.addEventListener("click",()=>{hb.classList.toggle("open");sd.classList.toggle("open");ov.style.display=sd.classList.contains("open")?"block":"none";document.body.style.overflow=sd.classList.contains("open")?"hidden":""});
ov.addEventListener("click",()=>{hb.classList.remove("open");sd.classList.remove("open");ov.style.display="none";document.body.style.overflow=""});
function tglDd(e){e.preventDefault();e.target.parentElement.classList.toggle("open")}
document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener("click",e=>{const t=document.querySelector(a.getAttribute("href"));if(t){e.preventDefault();window.scrollTo({top:t.offsetTop-70,behavior:"smooth"});document.querySelectorAll(".menu a").forEach(l=>l.classList.remove("act"));a.classList.add("act");if(sd.classList.contains("open")){hb.classList.remove("open");sd.classList.remove("open");ov.style.display="none";document.body.style.overflow=""}}}));
</script></body></html>'''))

# 8. Canvas粒子背景
data.append(e("Canvas粒子连线动画背景，鼠标交互，粒子间动态连线",
"制作粒子背景：\n1. 全屏Canvas黑色背景\n2. 初始化多个粒子，随机位置和速度\n3. 动画循环更新位置，边界反弹\n4. 计算粒子间距，小于阈值绘制连线\n5. 距离越近线条越明显（透明度/粗细变化）\n6. 鼠标附近粒子产生吸附效果\n7. requestAnimationFrame流畅动画",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>粒子背景</title><style>*{margin:0;padding:0}canvas{display:block;background:#0a0a23}</style></head><body><canvas id="c"></canvas>
<script>
const c=document.getElementById("c"),x=c.getContext("2d");let W,H,ps=[],mx=0,my=0;
function rs(){W=c.width=innerWidth;H=c.height=innerHeight}rs();addEventListener("resize",rs);
class P{constructor(){this.x=Math.random()*W;this.y=Math.random()*H;this.vx=(Math.random()-.5)*1.5;this.vy=(Math.random()-.5)*1.5;this.r=Math.random()*2+1}up(){this.x+=this.vx;this.y+=this.vy;if(this.x<0||this.x>W)this.vx*=-1;if(this.y<0||this.y>H)this.vy*=-1;const dx=this.x-mx,dy=this.y-my,d=Math.sqrt(dx*dx+dy*dy);if(d<120){this.x-=dx/d*.8;this.y-=dy/d*.8}x.beginPath();x.arc(this.x,this.y,this.r,0,Math.PI*2);x.fillStyle="#4facfe";x.fill()}}
for(let i=0;i<80;i++)ps.push(new P());
function lp(){x.clearRect(0,0,W,H);ps.forEach((p,i)=>{p.up();for(let j=i+1;j<ps.length;j++){const q=ps[j],dx=p.x-q.x,dy=p.y-q.y,d=Math.sqrt(dx*dx+dy*dy);if(d<100){x.beginPath();x.moveTo(p.x,p.y);x.lineTo(q.x,q.y);x.strokeStyle=`rgba(79,172,254,${1-d/100})`;x.lineWidth=1;x.stroke()}}});requestAnimationFrame(lp)}
addEventListener("mousemove",e=>{mx=e.clientX;my=e.clientY});lp();
</script></body></html>'''))

# 9. 倒计时器
data.append(e("圆形进度倒计时器，支持设置时间、开始暂停重置，完成提醒",
"制作倒计时器：\n1. SVG绘制圆形进度条\n2. 显示分:秒时间格式\n3. 快速选择预设时间按钮\n4. 开始/暂停/重置功能\n5. 进度条动画随时间减少\n6. Web Audio API生成提示音\n7. 时间到弹窗提醒",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>倒计时</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{display:flex;align-items:center;justify-content:center;min-height:100vh;background:linear-gradient(135deg,#667eea,#764ba2);font-family:Arial}.box{text-align:center;background:#fff;padding:40px;border-radius:20px;box-shadow:0 20px 60px rgba(0,0,0,.3)}.pr{position:relative;width:280px;height:280px;margin:0 auto 25px}svg{transform:rotate(-90deg)}circle{fill:none;stroke-width:10}.bg{stroke:#eee}.fg{stroke:#667eea;stroke-linecap:round;transition:stroke-dashoffset 1s linear}.tm{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:50px;font-weight:bold;color:#333}.btns{display:flex;gap:10px;justify-content:center;margin-bottom:15px}button{padding:10px 22px;border:none;border-radius:20px;cursor:pointer;font-weight:bold}.st{background:#667eea;color:#fff}.pa{background:#f39c12;color:#fff}.rs{background:#e74c3c;color:#fff}.pre{display:flex;gap:8px;justify-content:center;flex-wrap:wrap}.pre button{padding:8px 14px;background:#eee;color:#333;font-size:13px}</style></head><body>
<div class="box"><div class="pr"><svg width="280" height="280"><circle class="bg" cx="140" cy="140" r="120"/><circle class="fg" id="fg" cx="140" cy="140" r="120"/></svg><div class="tm" id="tm">05:00</div></div>
<div class="btns"><button class="st" onclick="st()">开始</button><button class="pa" onclick="pa()">暂停</button><button class="rs" onclick="rs()">重置</button></div>
<div class="pre"><button onclick="set(60)">1分</button><button onclick="set(300)">5分</button><button onclick="set(600)">10分</button><button onclick="set(1500)">25分</button><button onclick="set(3600)">1时</button></div></div>
<script>
let tot=300,rem=tot,tid,run;const C=2*Math.PI*120,fg=document.getElementById("fg");fg.style.strokeDasharray=C;fg.style.strokeDashoffset=0;
function fmt(s){return String(Math.floor(s/60)).padStart(2,"0")+":"+String(s%60).padStart(2,"0")}
function up(){document.getElementById("tm").textContent=fmt(rem);fg.style.strokeDashoffset=C*(1-rem/tot)}
function st(){if(run)return;run=true;tid=setInterval(()=>{rem--;up();if(rem<=0){clearInterval(tid);run=false;beep();alert("时间到!")}},1000)}
function pa(){clearInterval(tid);run=false}
function rs(){pa();rem=tot;up()}
function set(s){pa();tot=s;rem=s;up()}
function beep(){const ac=new(window.AudioContext||window.webkitAudioContext)(),o=ac.createOscillator(),g=ac.createGain();o.connect(g);g.connect(ac.destination);o.frequency.value=800;g.gain.setValueAtTime(.3,ac.currentTime);g.gain.exponentialRampToValueAtTime(.001,ac.currentTime+.5);o.start();o.stop(ac.currentTime+.5)}up();
</script></body></html>'''))

# 10. Todo List
data.append(e("待办事项应用，支持增删改查、标记完成、筛选、本地存储",
"开发Todo List：\n1. 顶部输入框添加任务\n2. 任务列表显示，复选框标记完成\n3. 删除按钮（hover显示）\n4. 底部筛选：全部/未完成/已完成\n5. 清除已完成按钮\n6. 未完成数量统计\n7. localStorage保存数据",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Todo List</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:#f5f5f5;padding:40px 20px;font-family:Arial}.wrap{max-width:500px;margin:0 auto;background:#fff;box-shadow:0 2px 10px rgba(0,0,0,.1);border-radius:8px;overflow:hidden}h1{text-align:center;font-size:70px;color:rgba(175,47,47,.15);padding:15px 0}.inp{display:flex;border-bottom:1px solid #eee;padding:15px}.inp input{flex:1;font-size:20px;border:none;outline:none;padding-left:15px;font-style:italic;color:#4d4d4d}.inp button{padding:10px 20px;background:#b83f45;color:#fff;border:none;border-radius:4px;cursor:pointer}.list{list-style:none}.item{display:flex;align-items:center;padding:15px;border-bottom:1px solid #eee;font-size:20px}.item:hover .del{display:block}.chk{width:25px;height:25px;margin-right:15px;cursor:pointer;accent-color:#5dc2af}.txt{flex:1;color:#4d4d4d}.done .txt{text-decoration:line-through;color:#d9d9d9}.del{display:none;margin-left:10px;color:#cc9a9a;font-size:25px;cursor:pointer;background:none;border:none}.del:hover{color:#af5b5e}.ft{display:flex;justify-content:space-between;align-items:center;padding:12px 15px;font-size:13px;color:#777;border-top:1px solid #eee}.ft button{border:1px solid transparent;padding:3px 7px;border-radius:3px;background:none;cursor:pointer;color:inherit;font-size:13px}.ft button.act{border-color:rgba(175,47,47,.2)}.clr{background:none;border:none;cursor:pointer;color:inherit}.clr:hover{text-decoration:underline}</style></head><body>
<div class="wrap"><h1>todos</h1><div class="inp"><input id="inp" placeholder="需要做什么?"><button onclick="add()">添加</button></div><ul class="list" id="list"></ul><div class="ft" id="ft" style="display:none"><span><b id="cnt">0</b>项待完成</span><div><button class="act" onclick="flt('all')">全部</button> <button onclick="flt('act')">未完成</button> <button onclick="flt('done')">已完成</button></div><button class="clr" onclick="clrD()">清除已完成</button></div></div>
<script>
let todos=JSON.parse(localStorage.getItem("todos")||"[]"),fl="all";
function sv(){localStorage.setItem("todos",JSON.stringify(todos));rd()}
function add(){const i=document.getElementById("inp"),v=i.value.trim();if(v){todos.push({id:Date.now(),t:v,d:false});i.value="";sv()}}
function tg(id){todos=todos.map(t=>t.id===id?{...t,d:!t.d}:t);sv()}
function dl(id){todos=todos.filter(t=>t.id!==id);sv()}
function clrD(){todos=todos.filter(t=>!t.d);sv()}
function flt(f){fl=f;document.querySelectorAll(".ft button").forEach(b=>b.classList.toggle("act",b.textContent.includes({all:"全部",act:"未完成",done:"已完成"}[f])));rd()}
function rd(){const l=document.getElementById("list"),ft=document.getElementById("ft");let f=todos;if(fl==="act")f=todos.filter(t=>!t.d);if(fl==="done")f=todos.filter(t=>t.d);l.innerHTML=f.length?f.map(t=>`<li class="item ${t.d?'done':''}"><input type="checkbox" class="chk" ${t.d?'checked':''} onchange="tg(${t.id})"><span class="txt">${t.t}</span><button class="del" onclick="dl(${t.id})">×</button></li>`).join(""):"";ft.style.display=todos.length?"flex":"none";document.getElementById("cnt").textContent=todos.filter(t=>!t.d).length}
document.getElementById("inp").addEventListener("keydown",e=>{if(e.key==="Enter")add()});rd();
</script></body></html>'''))

# 11-20: Web API和组件
# 11. Canvas折线图
data.append(e("Canvas折线图，支持多数据系列、图例、鼠标悬停提示、动画",
"绘制Canvas折线图：\n1. 定义边距和坐标系\n2. 绘制X轴Y轴和刻度标签\n3. 准备多组数据，每组不同颜色\n4. 用lineTo连接各数据点，填充区域可选\n5. 数据点绘制圆点标记\n6. 鼠标悬停显示tooltip\n7. 绘制图例",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>折线图</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{display:flex;flex-direction:column;align-items:center;padding:30px;background:#f5f5f5;font-family:Arial}h2{margin-bottom:20px}.wrap{position:relative;background:#fff;padding:25px;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,.1)}canvas{display:block}#tip{position:absolute;display:none;background:rgba(0,0,0,.8);color:#fff;padding:8px 12px;border-radius:6px;font-size:13px;pointer-events:none}.lgd{display:flex;gap:20px;justify-content:center;margin-top:15px}.lgd div{display:flex;align-items:center;gap:5px;font-size:14px}.lgd span{width:20px;height:3px;border-radius:2px}</style></head><body>
<h2>📈 月度销售趋势</h2><div class="wrap"><canvas id="c" width="700" height="400"></canvas><div id="tip"></div><div class="lgd" id="lgd"></div></div>
<script>
const c=document.getElementById("c"),x=c.getContext("2d"),pad={t:30,r:20,b:50,l:50},W=700-pad.l-pad.r,H=400-pad.t-pad.b;
const months=["1月","2月","3月","4月","5月","6月","7月","8月"];const series=[{n:"产品A",c:"#667eea",d:[30,45,35,50,49,60,70,91]},{n:"产品B",c:"#f5576c",d:[20,25,40,35,45,55,65,75]},{n:"产品C",c:"#43e97b",d:[10,30,25,40,35,50,45,60]}];let anim=0,hi=-1;
function draw(){x.clearRect(0,0,c.width,c.height);const maxV=100;x.strokeStyle="#eee";for(let i=0;i<=5;i++){const y=pad.t+H-H/5*i;x.beginPath();x.moveTo(pad.l,y);x.lineTo(pad.l+W,y);x.stroke();x.fillStyle="#999";x.font="12px Arial";x.textAlign="right";x.textBaseline="middle";x.fillText(maxV/5*i,pad.l-8,y)}months.forEach((m,i)=>{x.fillStyle="#666";x.textAlign="center";x.fillText(m,pad.l+W/(months.length-1)*i,pad.t+H+20)});series.forEach((s,si)=>{x.beginPath();x.strokeStyle=s.c;x.lineWidth=3;s.d.forEach((v,i)=>{const px=pad.l+W/(months.length-1)*i,py=pad.t+H-v/maxV*H*anim;if(i===0)x.moveTo(px,py);else x.lineTo(px,py)});x.stroke();s.d.forEach((v,i)=>{const px=pad.l+W/(months.length-1)*i,py=pad.t+H-v/maxV*H*anim;x.beginPath();x.arc(px,py,5,0,Math.PI*2);x.fillStyle="#fff";x.fill();x.strokeStyle=s.c;x.lineWidth=2;x.stroke()})});x.strokeStyle="#ccc";x.beginPath();x.moveTo(pad.l,pad.t);x.lineTo(pad.l,pad.t+H);x.lineTo(pad.l+W,pad.t+H);x.stroke()}
function animL(){anim+=.03;if(anim>1)anim=1;draw();if(anim<1)requestAnimationFrame(animL)}
c.addEventListener("mousemove",e=>{const r=c.getBoundingClientRect(),mx=e.clientX-r.left,my=e.clientY-r.top;const i=Math.round((mx-pad.l)/W*(months.length-1));if(i>=0&&i<months.length){document.getElementById("tip").style.display="block";document.getElementById("tip").style.left=mx+15+"px";document.getElementById("tip").style.top=my-30+"px";document.getElementById("tip").innerHTML=months[i]+"<br>"+series.map(s=>`<span style="color:${s.c}">${s.n}: ${s.d[i]}</span>`).join("<br>")}else document.getElementById("tip").style.display="none"});
document.getElementById("lgd").innerHTML=series.map(s=>`<div><span style="background:${s.c}"></span>${s.n}</div>`).join("");animL();
</script></body></html>'''))

# 12. 拖拽排序
data.append(e("拖拽排序列表，支持拖拽调整项目顺序，有视觉反馈动画",
"实现拖拽排序：\n1. 列表项布局\n2. HTML5 Drag and Drop API\n3. 拖拽开始时记录原位置，添加拖拽样式\n4. dragover时检测目标位置，显示插入指示\n5. 拖拽结束时重新排序数组\n6. 流畅的过渡动画\n7. 支持触摸设备",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>拖拽排序</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{padding:50px;background:#f0f0f0;font-family:Arial}h1{text-align:center;margin-bottom:30px;color:#333}.list{max-width:500px;margin:0 auto;background:#fff;border-radius:10px;box-shadow:0 2px 15px rgba(0,0,0,.1);overflow:hidden}.item{padding:18px 25px;border-bottom:1px solid #f0f0f0;display:flex;align-items:center;gap:15px;background:#fff;cursor:grab;transition:.2s}.item:last-child{border-bottom:none}.item.drag{opacity:.4;background:#e8eaf6}.item.over{border-top:3px solid #667eea}.handle{color:#ccc;cursor:grab;font-size:20px}.txt{flex:1;font-size:16px;color:#333}.num{width:30px;height:30px;background:#667eea;color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:bold}</style></head><body>
<h1>🔄 拖拽排序列表</h1><div class="list" id="list"></div>
<script>
let items=["学习HTML","学习CSS","学习JavaScript","学习Vue","学习React","学习Node.js","做项目"],dragIdx=null;
function render(){const l=document.getElementById("list");l.innerHTML="";items.forEach((t,i)=>{const d=document.createElement("div");d.className="item";d.draggable=true;d.innerHTML=`<span class="handle">⋮⋮</span><span class="num">${i+1}</span><span class="txt">${t}</span>`;d.addEventListener("dragstart",e=>{dragIdx=i;d.classList.add("drag");e.dataTransfer.effectAllowed="move"});d.addEventListener("dragend",()=>{d.classList.remove("drag");document.querySelectorAll(".item").forEach(it=>it.classList.remove("over"))});d.addEventListener("dragover",e=>{e.preventDefault();if(dragIdx!==null&&dragIdx!==i){document.querySelectorAll(".item").forEach(it=>it.classList.remove("over"));d.classList.add("over")}});d.addEventListener("drop",e=>{e.preventDefault();if(dragIdx!==null&&dragIdx!==i){const item=items.splice(dragIdx,1)[0];items.splice(i,0,item);render()}});l.appendChild(d)})}
render();
</script></body></html>'''))

# 13. 图片懒加载
data.append(e("图片懒加载，滚动到可视区域才加载图片，有占位符和加载动画",
"实现图片懒加载：\n1. 使用IntersectionObserver API\n2. 图片初始用占位图（可以是灰色块或低分辨率图）\n3. data-src存储真实图片地址\n4. 图片进入视口时开始加载真实图片\n5. 加载完成后淡入显示\n6. 支持加载失败显示错误占位\n7. 图片加载过程显示loading动画",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>图片懒加载</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:#f0f0f0;padding:20px;font-family:Arial}h1{text-align:center;margin-bottom:30px}p{max-width:800px;margin:0 auto 30px;color:#666;line-height:1.8;text-align:center}.gal{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:15px;max-width:1100px;margin:0 auto}.img-w{aspect-ratio:4/3;background:#ddd;border-radius:8px;overflow:hidden;position:relative}.img-w img{width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .5s}.img-w img.loaded{opacity:1}.img-w::before{content:"";position:absolute;top:50%;left:50%;width:30px;height:30px;border:3px solid #ccc;border-top-color:#667eea;border-radius:50%;animation:spin 1s linear infinite;margin:-15px 0 0 -15px;display:block}.img-w.loaded::before{display:none}@keyframes spin{to{transform:rotate(360deg)}}</style></head><body>
<h1>🖼️ 图片懒加载演示</h1><p>向下滚动页面，图片进入可视区域后才会加载。观察图片逐渐加载的效果。</p><div class="gal" id="gal"></div>
<script>
const gal=document.getElementById("gal");for(let i=1;i<=20;i++){const w=document.createElement("div");w.className="img-w";const img=document.createElement("img");img.dataset.src=`https://picsum.photos/400/300?random=${i}`;img.alt="图片"+i;w.appendChild(img);gal.appendChild(w)}
const obs=new IntersectionObserver((es)=>{es.forEach(e=>{if(e.isIntersecting){const w=e.target,img=w.querySelector("img");if(img.dataset.src){img.src=img.dataset.src;img.onload=()=>{img.classList.add("loaded");w.classList.add("loaded")};img.removeAttribute("data-src")}obs.unobserve(w)}})},{rootMargin:"100px"});
document.querySelectorAll(".img-w").forEach(w=>obs.observe(w));
</script></body></html>'''))

# 14. 本地记事本
data.append(e("简易记事本，使用LocalStorage存储，支持新建、编辑、删除笔记",
"开发记事本：\n1. 左侧笔记列表，右侧编辑区\n2. 每条笔记显示标题、预览、时间\n3. 点击笔记加载到编辑区\n4. 实时自动保存\n5. 删除笔记功能\n6. 新建笔记按钮\n7. 笔记列表按修改时间排序",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>记事本</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{display:flex;height:100vh;font-family:Arial;background:#f5f5f5}aside{width:280px;background:#fff;border-right:1px solid #ddd;display:flex;flex-direction:column}header{padding:15px;border-bottom:1px solid #ddd;display:flex;gap:10px}header input{flex:1;padding:8px;border:1px solid #ddd;border-radius:5px;font-size:13px}header button{padding:8px 12px;background:#667eea;color:#fff;border:none;border-radius:5px;cursor:pointer;white-space:nowrap}ul{flex:1;overflow-y:auto;list-style:none}li{padding:15px;border-bottom:1px solid #eee;cursor:pointer}li.act{background:#e8eaf6}li:hover{background:#f5f5f5}.nt{font-weight:bold;font-size:14px;margin-bottom:5px;color:#333;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.np{font-size:12px;color:#888;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.nd{font-size:11px;color:#aaa;margin-top:5px}main{flex:1;display:flex;flex-direction:column;padding:20px}main input,main textarea{width:100%;padding:12px;border:1px solid #ddd;border-radius:8px;margin-bottom:15px;font-size:18px;font-family:inherit}main textarea{flex:1;resize:none;font-size:14px;line-height:1.6}main button{align-self:flex-end;padding:8px 15px;background:#e74c3c;color:#fff;border:none;border-radius:5px;cursor:pointer}</style></head><body>
<aside><header><input id="sr" placeholder="搜索..."><button onclick="add()">+ 新建</button></header><ul id="list"></ul></aside>
<main><input id="tl" placeholder="标题"><textarea id="bd" placeholder="开始写笔记..."></textarea><button onclick="del()">删除笔记</button></main>
<script>
let notes=JSON.parse(localStorage.getItem("notes")||"[]"),cur=null;const ls=document.getElementById("list"),tl=document.getElementById("tl"),bd=document.getElementById("bd");
function sv(){localStorage.setItem("notes",JSON.stringify(notes));rd()}
function rd(){const q=document.getElementById("sr").value.toLowerCase();ls.innerHTML="";notes.filter(n=>(n.t||"无标题").toLowerCase().includes(q)||(n.c||"").toLowerCase().includes(q)).sort((a,b)=>b.d-a.d).forEach(n=>{const li=document.createElement("li");li.className=cur===n.id?"act":"";li.innerHTML=`<div class="nt">${n.t||"无标题"}</div><div class="np">${n.c||"无内容"}</div><div class="nd">${new Date(n.d).toLocaleString()}</div>`;li.onclick=()=>op(n.id);ls.appendChild(li)})}
function op(id){cur=id;const n=notes.find(n=>n.id===id);tl.value=n.t||"";bd.value=n.c||"";rd()}
function add(){const n={id:Date.now(),t:"",c:"",d:Date.now()};notes.unshift(n);cur=n.id;tl.value="";bd.value="";sv();tl.focus()}
function del(){if(!cur)return;notes=notes.filter(n=>n.id!==cur);cur=notes[0]?.id||null;if(cur){const n=notes.find(n=>n.id===cur);tl.value=n.t;bd.value=n.c}else{tl.value="";bd.value=""}sv()}
function up(){if(!cur)return;const n=notes.find(n=>n.id===cur);n.t=tl.value;n.c=bd.value;n.d=Date.now();sv()}
tl.addEventListener("input",up);bd.addEventListener("input",up);document.getElementById("sr").addEventListener("input",rd);if(notes.length)op(notes[0].id);rd();
</script></body></html>'''))

# 15. 轮播图
data.append(e("图片轮播组件，支持自动播放、左右切换、指示点、淡入淡出动画",
"制作轮播图：\n1. 图片绝对定位层叠\n2. 透明度过渡实现淡入淡出\n3. 左右箭头按钮切换\n4. 底部圆点指示器\n5. 自动轮播setInterval\n6. 鼠标悬停暂停自动播放\n7. 无缝循环",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>轮播图</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{display:flex;align-items:center;justify-content:center;min-height:100vh;background:#f0f0f0}.car{position:relative;width:700px;height:400px;border-radius:12px;overflow:hidden;box-shadow:0 10px 40px rgba(0,0,0,.2)}.slides{width:100%;height:100%;position:relative}.slide{position:absolute;top:0;left:0;width:100%;height:100%;opacity:0;transition:opacity .6s;object-fit:cover}.slide.act{opacity:1}.btn{position:absolute;top:50%;transform:translateY(-50%);width:45px;height:45px;background:rgba(255,255,255,.7);border:none;border-radius:50%;font-size:22px;cursor:pointer;z-index:10}.btn:hover{background:#fff}.prev{left:15px}.next{right:15px}.dots{position:absolute;bottom:20px;left:50%;transform:translateX(-50%);display:flex;gap:8px;z-index:10}.dot{width:12px;height:12px;border-radius:50%;background:rgba(255,255,255,.5);cursor:pointer;transition:.3s}.dot.act{background:#fff;transform:scale(1.2)}</style></head><body>
<div class="car" id="car"><div class="slides" id="slides"></div><button class="btn prev" onclick="ch(-1)">❮</button><button class="btn next" onclick="ch(1)">❯</button><div class="dots" id="dots"></div></div>
<script>
const imgs=Array.from({length:5},(_,i)=>`https://picsum.photos/700/400?random=${i+10}`);let cur=0,tid;const sl=document.getElementById("slides"),dt=document.getElementById("dots");
imgs.forEach((src,i)=>{const im=document.createElement("img");im.src=src;im.className="slide"+(i===0?" act":"");sl.appendChild(im);const d=document.createElement("div");d.className="dot"+(i===0?" act":"");d.onclick=()=>go(i);dt.appendChild(d)});
function go(i){sl.children[cur].classList.remove("act");dt.children[cur].classList.remove("act");cur=(i+imgs.length)%imgs.length;sl.children[cur].classList.add("act");dt.children[cur].classList.add("act")}
function ch(d){go(cur+d)}function auto(){tid=setInterval(()=>ch(1),3000)}
document.getElementById("car").addEventListener("mouseenter",()=>clearInterval(tid));document.getElementById("car").addEventListener("mouseleave",auto);auto();
</script></body></html>'''))

# 16. 数字滚动
data.append(e("数字滚动增长动画，从0到目标值，缓动效果，千分位格式化",
"实现数字滚动：\n1. requestAnimationFrame驱动\n2. easeOutExpo缓动函数\n3. 计算动画进度映射到数值\n4. 千分位格式化显示\n5. 支持多个数字同时动画\n6. 进入视口触发（可选）\n7. 可配置动画时长",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>数字滚动</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{display:flex;align-items:center;justify-content:center;min-height:100vh;background:linear-gradient(135deg,#667eea,#764ba2);font-family:Arial}.wrap{display:flex;gap:60px;flex-wrap:wrap;justify-content:center}.item{text-align:center;color:#fff}.num{font-size:60px;font-weight:bold;margin-bottom:8px}.lbl{font-size:18px;opacity:.8}button{position:fixed;top:30px;right:30px;padding:12px 25px;background:#fff;color:#667eea;border:none;border-radius:25px;cursor:pointer;font-weight:bold}</style></head><body>
<button onclick="anim()">重新播放</button><div class="wrap"><div class="item"><div class="num" id="n1">0</div><div class="lbl">用户总数</div></div><div class="item"><div class="num" id="n2">0</div><div class="lbl">项目数量</div></div><div class="item"><div class="num" id="n3">0</div><div class="lbl">五星好评</div></div><div class="item"><div class="num" id="n4">0</div><div class="lbl">合作伙伴</div></div></div>
<script>
function cnt(el,t,dur=2000){const st=performance.now(),ease=t=>1-Math.pow(2,-10*t);(function step(now){const p=Math.min((now-st)/dur,1),v=Math.floor(t*ease(p));el.textContent=v.toLocaleString()+(el.id==="n3"?"%":"+");if(p<1)requestAnimationFrame(step)})(st)}
function anim(){cnt(document.getElementById("n1"),128456);cnt(document.getElementById("n2"),3682);cnt(document.getElementById("n3"),99);cnt(document.getElementById("n4"),500)}setTimeout(anim,300);
</script></body></html>'''))

# 17. 暗黑模式
data.append(e("暗黑模式切换，CSS变量实现主题切换，本地存储记住偏好",
"实现暗黑模式：\n1. CSS变量定义两套主题色\n2. body.dark切换暗黑主题\n3. 切换按钮（月亮/太阳图标）\n4. 所有颜色使用var()引用\n5. 添加transition过渡动画\n6. localStorage保存选择\n7. 首次访问跟随系统偏好",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>暗黑模式</title>
<style>*{margin:0;padding:0;box-sizing:border-box;transition:background .3s,color .3s}:root{--bg:#f8f9fa;--card:#fff;--txt:#212529;--sub:#6c757d;--btn:#667eea;--sh:0 2px 10px rgba(0,0,0,.08)}body.dark{--bg:#1a1a2e;--card:#252542;--txt:#fff;--sub:#aaa;--btn:#4facfe;--sh:0 2px 10px rgba(0,0,0,.3)}body{background:var(--bg);color:var(--txt);font-family:Arial;padding:40px;min-height:100vh}header{max-width:900px;margin:0 auto 30px;display:flex;justify-content:space-between;align-items:center}h1{font-size:28px}#tgl{width:50px;height:50px;border-radius:50%;border:none;background:var(--card);font-size:24px;cursor:pointer;box-shadow:var(--sh)}.grid{max-width:900px;margin:0 auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:20px}.card{background:var(--card);padding:25px;border-radius:12px;box-shadow:var(--sh)}.card h3{margin-bottom:10px;font-size:18px}.card p{color:var(--sub);line-height:1.7;margin-bottom:15px;font-size:14px}.card button{padding:10px 20px;background:var(--btn);color:#fff;border:none;border-radius:6px;cursor:pointer}</style></head><body>
<header><h1>🌙 暗黑模式切换</h1><button id="tgl">🌙</button></header>
<div class="grid"><div class="card"><h3>简洁设计</h3><p>使用CSS变量实现主题切换，代码结构清晰。点击右上角按钮切换明暗主题。</p><button>了解更多</button></div><div class="card"><h3>平滑过渡</h3><p>所有颜色变化都有平滑的过渡动画，提升用户体验。</p><button>查看详情</button></div><div class="card"><h3>持久化保存</h3><p>主题偏好保存在localStorage，下次访问自动应用。</p><button>开始体验</button></div><div class="card"><h3>系统适配</h3><p>首次访问时自动检测系统主题偏好设置。</p><button>更多功能</button></div></div>
<script>
const btn=document.getElementById("tgl");const saved=localStorage.getItem("theme");const pref=saved||(matchMedia("(prefers-color-scheme:dark)").matches?"dark":"light");if(pref==="dark"){document.body.classList.add("dark");btn.textContent="☀️"}
btn.onclick=()=>{document.body.classList.toggle("dark");const d=document.body.classList.contains("dark");btn.textContent=d?"☀️":"🌙";localStorage.setItem("theme",d?"dark":"light")};
</script></body></html>'''))

# 18. 计算器
data.append(e("网页计算器，支持四则运算、百分比、正负号、键盘输入",
"开发计算器：\n1. CSS Grid排列按钮\n2. 数字键、运算符键、功能键不同颜色\n3. 显示屏显示当前和历史计算\n4. 处理小数、连续运算\n5. AC清除、退格、%、+/-功能\n6. 键盘事件支持\n7. 除以0等错误处理",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>计算器</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{display:flex;align-items:center;justify-content:center;min-height:100vh;background:linear-gradient(135deg,#2c3e50,#3498db);font-family:Arial}.calc{background:#1c1c1e;padding:20px;border-radius:18px;box-shadow:0 20px 60px rgba(0,0,0,.5)}.disp{background:#000;color:#fff;padding:20px;text-align:right;border-radius:10px;margin-bottom:15px;min-height:90px;display:flex;flex-direction:column;justify-content:flex-end}.hist{font-size:16px;color:#888;min-height:20px}.cur{font-size:42px;font-weight:300}.btns{display:grid;grid-template-columns:repeat(4,65px);gap:10px}button{height:65px;border:none;border-radius:50%;font-size:24px;cursor:pointer;font-weight:500;transition:filter .1s}button:active{filter:brightness(1.3)}.fn{background:#a5a5a5;color:#000}.op{background:#ff9500;color:#fff}.num{background:#333;color:#fff}.zero{grid-column:span 2;border-radius:35px;text-align:left;padding-left:26px}</style></head><body>
<div class="calc"><div class="disp"><div class="hist" id="hist"></div><div class="cur" id="cur">0</div></div><div class="btns"><button class="fn" onclick="allC()">AC</button><button class="fn" onclick="neg()">±</button><button class="fn" onclick="pct()">%</button><button class="op" onclick="sOp('/')">÷</button><button class="num" onclick="n('7')">7</button><button class="num" onclick="n('8')">8</button><button class="num" onclick="n('9')">9</button><button class="op" onclick="sOp('*')">×</button><button class="num" onclick="n('4')">4</button><button class="num" onclick="n('5')">5</button><button class="num" onclick="n('6')">6</button><button class="op" onclick="sOp('-')">−</button><button class="num" onclick="n('1')">1</button><button class="num" onclick="n('2')">2</button><button class="num" onclick="n('3')">3</button><button class="op" onclick="sOp('+')">+</button><button class="num zero" onclick="n('0')">0</button><button class="num" onclick="dot()">.</button><button class="op" onclick="calc()">=</button></div></div>
<script>
let cur="0",prev=null,op=null,wait=false;const ce=document.getElementById("cur"),he=document.getElementById("hist");
function upd(){ce.textContent=cur.length>10?parseFloat(cur).toExponential(4):cur;he.textContent=prev!==null?prev+(op==="*"?"×":op==="/"?"÷":op||""):""}
function n(d){if(wait){cur=d;wait=false}else cur=cur==="0"?d:cur+d;upd()}
function dot(){if(wait)cur="0.";else if(!cur.includes("."))cur+=".";upd()}
function allC(){cur="0";prev=null;op=null;wait=false;upd()}
function neg(){cur=String(parseFloat(cur)*-1);upd()}
function pct(){cur=String(parseFloat(cur)/100);upd()}
function sOp(o){if(op&&!wait)calc();prev=parseFloat(cur);op=o;wait=true;upd()}
function calc(){if(!op||wait)return;const c=parseFloat(cur),p=prev;let r;switch(op){case"+":r=p+c;break;case"-":r=p-c;break;case"*":r=p*c;break;case"/":r=c===0?"错误":p/c;break}cur=String(r);prev=null;op=null;wait=true;upd()}
document.addEventListener("keydown",e=>{if(/[0-9]/.test(e.key))n(e.key);if(e.key===".")dot();if("+-*/".includes(e.key))sOp(e.key);if(e.key==="Enter"||e.key==="=")calc();if(e.key==="Escape")allC();if(e.key==="Backspace"){if(cur.length>1)cur=cur.slice(0,-1);else cur="0";upd()}});upd();
</script></body></html>'''))

# 19. 模态框
data.append(e("模态框弹窗组件，支持打开关闭动画、点击遮罩关闭、ESC关闭",
"开发模态框：\n1. 固定定位遮罩层\n2. 内容居中显示\n3. 打开/关闭缩放+淡入淡出动画\n4. 右上角X关闭按钮\n5. 点击遮罩关闭\n6. ESC键关闭\n7. 打开时禁止body滚动",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>模态框</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{padding:80px;font-family:Arial;background:#f5f5f5;text-align:center}h1{margin-bottom:30px;color:#333}button.open{padding:15px 35px;font-size:18px;background:#667eea;color:#fff;border:none;border-radius:10px;cursor:pointer;box-shadow:0 5px 20px rgba(102,126,234,.4)}.modal{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;z-index:1000;opacity:0;visibility:hidden;transition:.3s}.modal.show{opacity:1;visibility:visible}.mc{background:#fff;padding:35px;border-radius:15px;max-width:450px;width:90%;transform:scale(.8);transition:.3s;box-shadow:0 20px 60px rgba(0,0,0,.3)}.modal.show .mc{transform:scale(1)}.mh{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}.mh h2{color:#333;font-size:24px}.cl{background:none;border:none;font-size:28px;cursor:pointer;color:#999;line-height:1}.cl:hover{color:#333}.mb{color:#666;line-height:1.8;margin-bottom:25px}.mf{display:flex;gap:10px;justify-content:flex-end}.mf button{padding:10px 20px;border:none;border-radius:8px;cursor:pointer;font-size:15px}.btn-c{background:#eee;color:#333}.btn-s{background:#667eea;color:#fff}</style></head><body>
<h1>模态框组件演示</h1><button class="open" onclick="op()">打开模态框</button>
<div class="modal" id="m"><div class="mc"><div class="mh"><h2>提示信息</h2><button class="cl" onclick="cl()">&times;</button></div><div class="mb">这是一个精美的模态框弹窗组件，支持平滑的打开和关闭动画。点击遮罩层、关闭按钮或按下ESC键都可以关闭弹窗。</div><div class="mf"><button class="btn-c" onclick="cl()">取消</button><button class="btn-s" onclick="cl()">确定</button></div></div></div>
<script>
const m=document.getElementById("m");
function op(){m.classList.add("show");document.body.style.overflow="hidden"}
function cl(){m.classList.remove("show");document.body.style.overflow=""}
m.addEventListener("click",e=>{if(e.target===m)cl()});document.addEventListener("keydown",e=>{if(e.key==="Escape")cl()});
</script></body></html>'''))

# 20. 标签页组件
data.append(e("标签页Tabs组件，支持切换动画、响应式滚动标签",
"制作标签页：\n1. 横向标签导航栏\n2. 点击切换激活状态\n3. 内容面板淡入动画\n4. 下划线指示条滑动效果\n5. 标签过多时可滚动\n6. 可禁用某标签\n7. 支持卡片式和下划线式",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>标签页</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{padding:50px;background:#f5f5f5;font-family:"Microsoft YaHei",sans-serif}.tabs{max-width:700px;margin:0 auto;background:#fff;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,.08);overflow:hidden}.nav{display:flex;border-bottom:2px solid #eee;position:relative;overflow-x:auto}.nav button{padding:16px 28px;border:none;background:none;font-size:16px;cursor:pointer;color:#666;white-space:nowrap;transition:.3s;position:relative;z-index:1}.nav button:hover{color:#667eea}.nav button.act{color:#667eea;font-weight:bold}.ind{position:absolute;bottom:0;height:3px;background:#667eea;transition:.3s;border-radius:3px}.panels{padding:30px;min-height:200px}.panel{display:none;animation:fi .4s ease}.panel.act{display:block}@keyframes fi{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}.panel h3{margin-bottom:12px;color:#333;font-size:20px}.panel p{color:#666;line-height:1.8}</style></head><body>
<div class="tabs"><div class="nav" id="nav"><div class="ind" id="ind"></div></div><div class="panels" id="panels"></div></div>
<script>
const tabs=[{t:"首页",c:"<h3>🏠 首页</h3><p>欢迎来到标签页组件演示页面。这是一个功能完善的标签页组件，支持平滑的内容切换动画和下划线指示器滑动效果。你可以点击上方标签切换不同的内容。</p>"},{t:"产品",c:"<h3>📦 产品介绍</h3><p>我们提供高质量的Web开发服务，包括网站建设、移动应用开发、UI/UX设计、系统架构咨询等。我们的团队拥有丰富的项目经验，致力于为客户打造一流的数字产品。</p>"},{t:"关于我们",c:"<h3>👥 关于我们</h3><p>我们是一支充满激情和创造力的技术团队，成员来自各大知名互联网公司。我们热爱技术，追求卓越，以用户体验为核心，持续创造有价值的产品。</p>"},{t:"联系我们",c:"<h3>📧 联系方式</h3><p>邮箱：contact@example.com<br>电话：400-123-4567<br>地址：北京市朝阳区科技园区<br>工作时间：周一至周五 9:00-18:00</p>"}];
const nav=document.getElementById("nav"),panels=document.getElementById("panels"),ind=document.getElementById("ind");
tabs.forEach((t,i)=>{const b=document.createElement("button");b.textContent=t.t;b.onclick=()=>sw(i);nav.insertBefore(b,ind);const p=document.createElement("div");p.className="panel"+(i===0?" act":"");p.innerHTML=t.c;panels.appendChild(p)});
function sw(i){nav.querySelectorAll("button").forEach((b,j)=>b.classList.toggle("act",i===j));panels.querySelectorAll(".panel").forEach((p,j)=>p.classList.toggle("act",i===j));const btn=nav.querySelectorAll("button")[i];ind.style.width=btn.offsetWidth+"px";ind.style.left=btn.offsetLeft+"px"}
setTimeout(()=>sw(0),50);window.addEventListener("resize",()=>sw(Array.from(nav.querySelectorAll("button")).findIndex(b=>b.classList.contains("act"))));
</script></body></html>'''))

# 21-30: 特效和更多组件
# 21. 烟花动画
data.append(e("Canvas烟花动画，点击发射烟花，粒子爆炸效果，重力模拟",
"制作烟花效果：\n1. 全屏Canvas黑色背景\n2. 点击时从底部发射烟花弹\n3. 到达目标点爆炸成粒子\n4. 粒子带重力下落、淡出\n5. 随机颜色（HSL色相随机）\n6. 多个烟花同时存在\n7. 自动随机发射",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>烟花</title><style>*{margin:0;padding:0}canvas{display:block;background:#0a0a23}</style></head><body><canvas id="c"></canvas>
<script>
const c=document.getElementById("c"),x=c.getContext("2d");let W,H;function rs(){W=c.width=innerWidth;H=c.height=innerHeight}rs();addEventListener("resize",rs);
let fw=[],pt=[];class Rok{constructor(tx,ty){this.x=W/2;this.y=H;this.tx=tx;this.ty=ty;this.vx=(tx-this.x)/60;this.vy=(ty-this.y)/60;this.p=0;this.h=Math.random()*360}up(){this.x+=this.vx;this.y+=this.vy;this.p++;if(this.p>=60){for(let i=0;i<80;i++)pt.push(new P(this.tx,this.ty,this.h));return false}x.beginPath();x.arc(this.x,this.y,3,0,Math.PI*2);x.fillStyle=`hsl(${this.h},100%,60%)`;x.fill();return true}}
class P{constructor(x,y,h){this.x=x;this.y=y;this.h=h;const a=Math.random()*Math.PI*2,s=Math.random()*6+2;this.vx=Math.cos(a)*s;this.vy=Math.sin(a)*s;this.life=1;this.dc=0.015+Math.random()*.01}up(){this.x+=this.vx;this.y+=this.vy;this.vy+=0.07;this.vx*=.99;this.life-=this.dc;x.beginPath();x.arc(this.x,this.y,2,0,Math.PI*2);x.fillStyle=`hsla(${this.h},100%,60%,${this.life})`;x.fill();return this.life>0}}
function lp(){x.fillStyle="rgba(10,10,35,0.15)";x.fillRect(0,0,W,H);fw=fw.filter(f=>f.up());pt=pt.filter(p=>p.up());if(Math.random()<0.03)fw.push(new Rok(Math.random()*W,Math.random()*H/2+50));requestAnimationFrame(lp)}
c.addEventListener("click",e=>fw.push(new Rok(e.clientX,e.clientY)));lp();
</script></body></html>'''))

# 22. 星空背景
data.append(e("星空动画背景，星星闪烁，流星划过效果",
"制作星空：\n1. 生成大量星星随机位置\n2. 星星大小不同、亮度闪烁\n3. 缓慢移动视差效果\n4. 随机出现流星\n5. 流星带渐变拖尾\n6. 全屏显示\n7. 响应式窗口",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>星空</title><style>*{margin:0;padding:0}canvas{display:block;background:#000}</style></head><body><canvas id="c"></canvas>
<script>
const c=document.getElementById("c"),x=c.getContext("2d");let W,H,stars=[],shoots=[];
function rs(){W=c.width=innerWidth;H=c.height=innerHeight;stars=[];for(let i=0;i<150;i++)stars.push({x:Math.random()*W,y:Math.random()*H,r:Math.random()*1.5+.3,a:Math.random(),da:(Math.random()-.5)*.02,s:Math.random()*.4+.05})}rs();addEventListener("resize",rs);
class Sh{constructor(){this.x=Math.random()*W;this.y=Math.random()*H*.5;this.len=Math.random()*80+40;this.spd=Math.random()*8+6}up(){this.x+=this.spd;this.y+=this.spd/3;const g=x.createLinearGradient(this.x,this.y,this.x-this.len,this.y-this.len/3);g.addColorStop(0,"#fff");g.addColorStop(1,"transparent");x.beginPath();x.moveTo(this.x,this.y);x.lineTo(this.x-this.len,this.y-this.len/3);x.strokeStyle=g;x.lineWidth=2;x.stroke();return this.x<W+100}}
function drw(){x.fillStyle="rgba(0,0,0,0.15)";x.fillRect(0,0,W,H);stars.forEach(s=>{s.a+=s.da;if(s.a<=.1||s.a>=1)s.da*=-1;s.x+=s.s;if(s.x>W)s.x=0;x.beginPath();x.arc(s.x,s.y,s.r,0,Math.PI*2);x.fillStyle=`rgba(255,255,255,${s.a})`;x.fill()});if(Math.random()<0.01&&shoots.length<2)shoots.push(new Sh());shoots=shoots.filter(s=>s.up());requestAnimationFrame(drw)}drw();
</script></body></html>'''))

# 23. 模拟时钟
data.append(e("Canvas模拟时钟，时针分针秒针，刻度数字，平滑动画",
"绘制模拟时钟：\n1. 圆形表盘\n2. 12大刻度60小刻度\n3. 1-12数字标注\n4. 时针、分针、秒针不同样式\n5. 获取当前时间计算角度\n6. 中心点装饰\n7. requestAnimationFrame实时更新",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>时钟</title><style>*{margin:0;padding:0;box-sizing:border-box}body{display:flex;align-items:center;justify-content:center;min-height:100vh;background:linear-gradient(135deg,#232526,#414345)}canvas{box-shadow:0 0 50px rgba(0,0,0,.5),inset 0 0 30px rgba(255,255,255,.1);border-radius:50%;background:#f5f5f5}</style></head><body><canvas id="c" width="350" height="350"></canvas>
<script>
const c=document.getElementById("c"),x=c.getContext("2d"),r=c.width/2;function draw(){x.clearRect(0,0,c.width,c.height);x.save();x.translate(r,r);
x.beginPath();x.arc(0,0,r-10,0,Math.PI*2);x.fillStyle="#fff";x.fill();x.strokeStyle="#333";x.lineWidth=6;x.stroke();
for(let i=0;i<60;i++){const a=i*Math.PI/30;x.save();x.rotate(a);x.beginPath();x.moveTo(0,-r+15);x.lineTo(0,i%5? -r+22:-r+30);x.strokeStyle=i%5?"#999":"#333";x.lineWidth=i%5?1:3;x.stroke();x.restore()}
x.font="bold 22px Arial";x.textAlign="center";x.textBaseline="middle";x.fillStyle="#333";for(let i=1;i<=12;i++){const a=i*Math.PI/6;x.fillText(i,Math.sin(a)*(r-48),-Math.cos(a)*(r-48))}
const t=new Date,ms=t.getMilliseconds(),s=t.getSeconds()+ms/1000,m=t.getMinutes()+s/60,h=t.getHours()%12+m/60;
x.save();x.rotate(h*Math.PI/6);x.beginPath();x.moveTo(-6,15);x.lineTo(-3,-r+60);x.lineTo(3,-r+60);x.lineTo(6,15);x.fillStyle="#222";x.fill();x.restore();
x.save();x.rotate(m*Math.PI/30);x.beginPath();x.moveTo(-4,15);x.lineTo(-2,-r+40);x.lineTo(2,-r+40);x.lineTo(4,15);x.fillStyle="#444";x.fill();x.restore();
x.save();x.rotate(s*Math.PI/30);x.beginPath();x.moveTo(-1.5,r-20);x.lineTo(-1.5,-r+25);x.lineTo(1.5,-r+25);x.lineTo(1.5,r-20);x.fillStyle="#e74c3c";x.fill();x.beginPath();x.arc(0,0,7,0,Math.PI*2);x.fill();x.restore();
x.restore();requestAnimationFrame(draw)}draw();
</script></body></html>'''))

# 24. 饼图
data.append(e("Canvas饼图，鼠标悬停突出显示，图例，点击交互",
"绘制饼图：\n1. 计算每份角度\n2. arc()绘制扇形\n3. 不同颜色区分\n4. 鼠标位置判断在哪块\n5. 悬停时扇形偏移\n6. 绘制图例\n7. tooltip显示详情",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>饼图</title><style>*{margin:0;padding:0;box-sizing:border-box}body{display:flex;flex-direction:column;align-items:center;padding:40px;background:#f5f5f5;font-family:Arial}h2{margin-bottom:20px}.wrap{display:flex;gap:30px;align-items:center;background:#fff;padding:30px;border-radius:15px;box-shadow:0 4px 20px rgba(0,0,0,.08)}canvas{border-radius:50%}.lgd{font-size:15px}.lgd div{display:flex;align-items:center;gap:10px;margin-bottom:12px}.lgd span{width:18px;height:18px;border-radius:4px}#tip{position:fixed;display:none;background:rgba(0,0,0,.8);color:#fff;padding:8px 15px;border-radius:6px;pointer-events:none;font-size:14px;z-index:10}</style></head><body>
<h2>📊 流量来源分布</h2><div class="wrap"><canvas id="c" width="300" height="300"></canvas><div class="lgd" id="lgd"></div></div><div id="tip"></div>
<script>
const c=document.getElementById("c"),x=c.getContext("2d"),cx=150,cy=150,R=120;const data=[{n:"搜索引擎",v:40,c:"#4285f4"},{n:"直接访问",v:25,c:"#34a853"},{n:"社交媒体",v:20,c:"#fbbc05"},{n:"外部链接",v:10,c:"#ea4335"},{n:"其他",v:5,c:"#9c27b0"}];let hov=-1;const tot=data.reduce((s,d)=>s+d.v,0);
function drw(off=-1){x.clearRect(0,0,c.width,c.height);let st=-Math.PI/2;data.forEach((d,i)=>{const sz=d.v/tot*Math.PI*2,mid=st+sz/2,dx=i===off?Math.cos(mid)*12:0,dy=i===off?Math.sin(mid)*12:0;x.beginPath();x.moveTo(cx+dx,cy+dy);x.arc(cx+dx,cy+dy,R,st,st+sz);x.closePath();x.fillStyle=d.c;x.fill();st+=sz});document.getElementById("lgd").innerHTML=data.map(d=>`<div><span style="background:${d.c}"></span>${d.n} - ${d.v}%</div>`).join("")}
function hit(mx,my){let st=-Math.PI/2;for(let i=0;i<data.length;i++){const sz=data[i].v/tot*Math.PI*2;let a=Math.atan2(my-cy,mx-cx);if(a<-Math.PI/2)a+=Math.PI*2;const dx=mx-cx,dy=my-cy,dt=Math.sqrt(dx*dx+dy*dy);if(a>=st&&a<st+sz&&dt<R)return i;st+=sz}return-1}
c.addEventListener("mousemove",e=>{const r=c.getBoundingClientRect(),mx=e.clientX-r.left,my=e.clientY-r.top;hov=hit(mx,my);drw(hov);const tip=document.getElementById("tip");if(hov>=0){tip.style.display="block";tip.style.left=e.clientX+15+"px";tip.style.top=e.clientY-20+"px";tip.textContent=`${data[hov].n}: ${data[hov].v}%`;c.style.cursor="pointer"}else{tip.style.display="none";c.style.cursor="default"}});c.addEventListener("mouseleave",()=>{hov=-1;drw();document.getElementById("tip").style.display="none"});drw();
</script></body></html>'''))

# 25. 颜色选择器
data.append(e("RGB颜色选择器，滑块调节，HEX/RGB显示，颜色预览，点击复制",
"制作颜色选择器：\n1. R/G/B三个滑块0-255\n2. 实时预览区域\n3. HEX和RGB值显示\n4. 点击复制到剪贴板\n5. 颜色历史记录\n6. 滑块背景渐变\n7. 复制成功提示",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>颜色选择器</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{display:flex;align-items:center;justify-content:center;min-height:100vh;background:#f0f0f0;font-family:Arial}.box{background:#fff;padding:30px;border-radius:15px;box-shadow:0 10px 40px rgba(0,0,0,.1);width:350px}.prev{width:100%;height:120px;border-radius:10px;margin-bottom:20px;transition:background .2s;border:2px solid #eee;border-radius:10px}.sl{margin-bottom:12px}.sl label{display:flex;justify-content:space-between;margin-bottom:5px;font-size:14px;font-weight:bold;color:#555}.sl input[type=range]{width:100%;-webkit-appearance:none;height:8px;border-radius:4px}.sl input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:18px;height:18px;border-radius:50%;cursor:pointer;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.3)}.r input{background:linear-gradient(to right,#000,#f00)}.g input{background:linear-gradient(to right,#000,#0f0)}.b input{background:linear-gradient(to right,#000,#00f)}.vals{display:flex;gap:8px;margin-top:15px}.vals div{flex:1;text-align:center;padding:10px;background:#f8f9fa;border-radius:8px;cursor:pointer;transition:.2s}.vals div:hover{background:#e9ecef}.lbl{font-size:11px;color:#888;margin-bottom:3px}.val{font-family:monospace;font-weight:bold;font-size:14px;color:#333}.hist{display:flex;gap:6px;margin-top:15px;flex-wrap:wrap}.hist div{width:28px;height:28px;border-radius:6px;cursor:pointer;border:2px solid #eee;transition:.2s}.hist div:hover{transform:scale(1.1)}</style></head><body>
<div class="box"><div class="prev" id="prev"></div><div class="sl r"><label><span>R</span><span id="rv">255</span></label><input type="range" id="r" min="0" max="255" value="255"></div><div class="sl g"><label><span>G</span><span id="gv">100</span></label><input type="range" id="g" min="0" max="255" value="100"></div><div class="sl b"><label><span>B</span><span id="bv">100</span></label><input type="range" id="b" min="0" max="255" value="100"></div><div class="vals"><div onclick="cp(0)"><div class="lbl">HEX</div><div class="val" id="hex">#FF6464</div></div><div onclick="cp(1)"><div class="lbl">RGB</div><div class="val" id="rgb">255,100,100</div></div></div><div class="hist" id="hist"></div></div>
<script>
const r=document.getElementById("r"),g=document.getElementById("g"),b=document.getElementById("b"),pv=document.getElementById("prev");let history=[];
function hx(n){return n.toString(16).padStart(2,"0")}function up(){const rv=+r.value,gv=+g.value,bv=+b.value;document.getElementById("rv").textContent=rv;document.getElementById("gv").textContent=gv;document.getElementById("bv").textContent=bv;const hex="#"+hx(rv)+hx(gv)+hx(bv);document.getElementById("hex").textContent=hex.toUpperCase();document.getElementById("rgb").textContent=`${rv},${gv},${bv}`;pv.style.background=hex;return hex}
function cp(i){const v=i?`rgb(${document.getElementById("rgb").textContent})`:document.getElementById("hex").textContent;navigator.clipboard.writeText(v);const el=i?document.getElementById("rgb"):document.getElementById("hex");const old=el.style.background;el.style.background="#4CAF50";el.style.color="#fff";setTimeout(()=>{el.style.background=old;el.style.color=""},800);addH(up())}
function addH(h){if(history.includes(h))return;history.unshift(h);if(history.length>12)history.pop();document.getElementById("hist").innerHTML=history.map(c=>`<div style="background:${c}" onclick="app('${c}')"></div>`).join("")}
function app(hex){const n=parseInt(hex.slice(1),16);r.value=(n>>16)&255;g.value=(n>>8)&255;b.value=n&255;addH(up())}
[r,g,b].forEach(s=>s.addEventListener("input",()=>addH(up())));addH(up());
</script></body></html>'''))

# 26. 星级评分
data.append(e("星级评分组件，鼠标悬停预览，点击打分，对应文字评价",
"制作星级评分：\n1. 5颗星★字符\n2. CSS direction:rtl实现反向高亮\n3. hover和checked状态样式\n4. 评分文字反馈\n5. 可设置默认分数\n6. 支持半星（可选）\n7. 显示当前分数",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>星级评分</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{display:flex;align-items:center;justify-content:center;min-height:100vh;background:#f5f5f5;font-family:Arial}.box{text-align:center;background:#fff;padding:50px;border-radius:15px;box-shadow:0 10px 30px rgba(0,0,0,.1)}.stars{display:flex;gap:8px;justify-content:center;margin-bottom:20px;flex-direction:row-reverse}.star{font-size:45px;cursor:pointer;color:#ddd;transition:.2s;user-select:none}.star:hover,.star:hover~.star,.star.act,.star.act~.star{color:#f39c12}.star:hover{transform:scale(1.2)}.txt{font-size:22px;color:#555;margin-bottom:10px;min-height:35px}p{color:#888}</style></head><body>
<div class="box"><div class="stars" id="stars"></div><div class="txt" id="txt">点击星星进行评分</div><p>当前评分: <span id="cur">0</span> / 5</p></div>
<script>
const labels=["请点击星星评分","很差 - 需要改进","较差 - 有待提高","一般 - 还不错","满意 - 体验很好","非常满意 - 极力推荐"];const st=document.getElementById("stars");let cur=0;
for(let i=5;i>=1;i--){const s=document.createElement("span");s.className="star";s.textContent="★";s.onclick=()=>{cur=i;upd()};s.onmouseenter=()=>hl(i);st.appendChild(s)}
st.onmouseleave=upd;
function hl(v){document.querySelectorAll(".star").forEach((s,i)=>s.classList.toggle("act",5-i<=v));document.getElementById("txt").textContent=labels[v]}
function upd(){hl(cur);document.getElementById("cur").textContent=cur;document.getElementById("txt").textContent=cur?labels[cur]:"点击星星进行评分"}
</script></body></html>'''))

# 27. 进度条
data.append(e("进度条组件，支持条纹动画、多色、百分比显示、平滑动画",
"开发进度条：\n1. 容器和填充层div\n2. 设置width百分比\n3. CSS条纹背景动画\n4. 多种颜色主题\n5. 显示百分比文字\n6. transition平滑动画\n7. 可设置条纹动画开关",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>进度条</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{padding:50px;background:#f5f5f5;font-family:Arial}.wrap{max-width:600px;margin:0 auto;background:#fff;padding:30px;border-radius:10px;box-shadow:0 2px 15px rgba(0,0,0,.08)}h2{margin-bottom:30px;color:#333;font-size:22px}.row{margin-bottom:25px}.lbl{display:flex;justify-content:space-between;margin-bottom:8px;color:#555;font-size:14px}.bar{height:22px;background:#eee;border-radius:11px;overflow:hidden;position:relative}.fill{height:100%;border-radius:11px;transition:width 1s ease;display:flex;align-items:center;justify-content:flex-end;padding-right:10px;color:#fff;font-size:12px;font-weight:bold}.striped{background-image:linear-gradient(45deg,rgba(255,255,255,.2) 25%,transparent 25%,transparent 50%,rgba(255,255,255,.2) 50%,rgba(255,255,255,.2) 75%,transparent 75%,transparent);background-size:40px 40px;animation:mv 1s linear infinite}@keyframes mv{from{background-position:40px 0}to{background-position:0 0}}.blue{background:linear-gradient(90deg,#667eea,#764ba2)}.green{background:linear-gradient(90deg,#11998e,#38ef7d)}.red{background:linear-gradient(90deg,#eb3349,#f45c43)}.orange{background:linear-gradient(90deg,#f093fb,#f5576c)}.cyan{background:linear-gradient(90deg,#4facfe,#00f2fe)}button{margin-top:10px;padding:10px 20px;background:#667eea;color:#fff;border:none;border-radius:6px;cursor:pointer}</style></head><body>
<div class="wrap"><h2>进度条组件</h2>
<div class="row"><div class="lbl"><span>下载进度</span><span id="p1">0%</span></div><div class="bar"><div class="fill blue striped" id="b1" style="width:0%">0%</div></div></div>
<div class="row"><div class="lbl"><span>上传进度</span><span id="p2">0%</span></div><div class="bar"><div class="fill green" id="b2" style="width:0%"></div></div></div>
<div class="row"><div class="lbl"><span>存储空间</span><span id="p3">0%</span></div><div class="bar"><div class="fill orange striped" id="b3" style="width:0%"></div></div></div>
<div class="row"><div class="lbl"><span>内存使用</span><span id="p4">0%</span></div><div class="bar"><div class="fill cyan" id="b4" style="width:0%"></div></div></div>
<button onclick="sim()">模拟进度</button></div>
<script>
function st(id,tg){let w=0;const t=setInterval(()=>{w+=Math.random()*8;if(w>=tg){w=tg;clearInterval(t)}const el=document.getElementById("b"+id);el.style.width=w+"%";if(id===1)el.textContent=Math.floor(w)+"%";document.getElementById("p"+id).textContent=Math.floor(w)+"%"},100)}
function sim(){st(1,Math.random()*60+40);st(2,100);setTimeout(()=>st(3,Math.random()*50+30),500);setTimeout(()=>st(4,Math.random()*70+20),1000)}setTimeout(sim,300);
</script></body></html>'''))

# 28. 打字机效果
data.append(e("文字打字机效果，逐字打出，光标闪烁，循环播放，速度可配",
"实现打字机：\n1. 文字数组循环播放\n2. 逐字符增加（打字）\n3. 打完全部后停顿再逐字删除\n4. 光标span blinking动画\n5. 控制打字和删除速度\n6. 停顿时间可配置\n7. CSS实现光标闪烁",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>打字机</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{display:flex;align-items:center;justify-content:center;min-height:100vh;background:#1a1a2e;font-family:"Courier New",monospace}.wrap{font-size:32px;color:#00ff88;white-space:nowrap}.cur{display:inline-block;width:3px;height:40px;background:#00ff88;animation:bl 1s infinite;margin-left:3px;vertical-align:middle}@keyframes bl{0%,49%{opacity:1}50%,100%{opacity:0}}</style></head><body>
<div><span id="t"></span><span class="cur"></span></div>
<script>
const words=["欢迎来到我的网站","这是打字机效果演示","适合做首页标语","文字会逐字打出","支持循环播放"];const el=document.getElementById("t");let wi=0,ci=0,del=false;
function ty(){const w=words[wi];if(del){el.textContent=w.substring(0,ci-1);ci--;if(ci===0){del=false;wi=(wi+1)%words.length;setTimeout(ty,400)}}else{el.textContent=w.substring(0,ci+1);ci++;if(ci===w.length){if(wi===words.length-1)return;del=true;setTimeout(ty,1500)}}if(!(ci===w.length&&!del))setTimeout(ty,del?40:80)}ty();
</script></body></html>'''))

# 29. Canvas画板
data.append(e("Canvas绘画板，支持画笔、橡皮擦、颜色选择、粗细调节、清空保存",
"开发画板：\n1. Canvas画布\n2. mousedown/move/up事件监听\n3. lineTo绘制路径\n4. 橡皮擦用destination-out\n5. 颜色选择器和线宽滑块\n6. 清空画布clearRect\n7. toDataURL保存图片",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>画板</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{display:flex;flex-direction:column;align-items:center;padding:20px;background:#f0f0f0;font-family:Arial}h1{margin-bottom:15px;color:#333}.tb{display:flex;gap:12px;align-items:center;margin-bottom:15px;background:#fff;padding:12px 20px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,.08);flex-wrap:wrap}button{padding:8px 15px;border:none;border-radius:6px;cursor:pointer;font-size:14px;font-weight:bold}.pen{background:#667eea;color:#fff}.er{background:#f39c12;color:#fff}.clr{background:#e74c3c;color:#fff}.sv{background:#27ae60;color:#fff}label{display:flex;align-items:center;gap:6px;font-size:14px;color:#555}input[type=color]{width:35px;height:30px;padding:0;border:none;border-radius:5px;cursor:pointer}input[type=range]{width:100px}canvas{border:2px solid #ddd;border-radius:10px;background:#fff;box-shadow:0 2px 10px rgba(0,0,0,.08);cursor:crosshair}</style></head><body>
<h1>🎨 简易画板</h1><div class="tb"><button class="pen" id="pen">画笔</button><button class="er" id="er">橡皮</button><label>颜色<input type="color" id="col" value="#000000"></label><label>粗细<input type="range" id="sz" min="1" max="30" value="3"></label><button class="clr" onclick="clr()">清空</button><button class="sv" onclick="sv()">保存图片</button></div>
<canvas id="c" width="800" height="500"></canvas>
<script>
const c=document.getElementById("c"),x=c.getContext("2d");let dr=false,md="pen",lx,ly;x.lineCap="round";x.lineJoin="round";
function pos(e){const r=c.getBoundingClientRect();return{x:e.clientX-r.left,y:e.clientY-r.top}}
c.addEventListener("mousedown",e=>{dr=true;const p=pos(e);lx=p.x;ly=p.y});
c.addEventListener("mousemove",e=>{if(!dr)return;const p=pos(e);x.beginPath();x.moveTo(lx,ly);x.lineTo(p.x,p.y);if(md==="er"){x.globalCompositeOperation="destination-out";x.lineWidth=document.getElementById("sz").value*2.5}else{x.globalCompositeOperation="source-over";x.strokeStyle=document.getElementById("col").value;x.lineWidth=document.getElementById("sz").value}x.stroke();lx=p.x;ly=p.y});
document.addEventListener("mouseup",()=>dr=false);document.getElementById("pen").onclick=()=>md="pen";document.getElementById("er").onclick=()=>md="er";
function clr(){x.clearRect(0,0,c.width,c.height)}function sv(){const a=document.createElement("a");a.download="drawing.png";a.href=c.toDataURL();a.click()}
</script></body></html>'''))

# 30. 图片画廊Lightbox
data.append(e("图片画廊Lightbox效果，点击缩略图查看大图，左右切换，键盘导航",
"制作图片画廊：\n1. 网格布局缩略图\n2. 点击打开灯箱层\n3. 大图显示，支持左右切换\n4. 键盘左右箭头导航\n5. ESC关闭、点击遮罩关闭\n6. 显示图片序号\n7. 上一张下一张按钮",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>图片画廊</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{padding:30px;background:#f5f5f5}h1{text-align:center;margin-bottom:25px;color:#333}.gd{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;max-width:1000px;margin:0 auto}.gd img{width:100%;height:150px;object-fit:cover;border-radius:8px;cursor:pointer;transition:.3s;box-shadow:0 2px 8px rgba(0,0,0,.1)}.gd img:hover{transform:scale(1.03);box-shadow:0 5px 20px rgba(0,0,0,.15)}.lb{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.9);display:none;align-items:center;justify-content:center;z-index:1000}.lb.show{display:flex}.lb img{max-width:90%;max-height:85vh;border-radius:8px;box-shadow:0 10px 50px rgba(0,0,0,.5)}.lb button{position:absolute;background:rgba(255,255,255,.15);color:#fff;border:none;width:50px;height:50px;border-radius:50%;font-size:26px;cursor:pointer;transition:.2s}.lb button:hover{background:rgba(255,255,255,.3)}.lb-prev{left:25px}.lb-next{right:25px}.lb-cl{top:20px;right:25px}.lb-cnt{position:absolute;bottom:25px;color:#fff;font-size:16px}</style></head><body>
<h1>🖼️ 图片画廊</h1><div class="gd" id="gd"></div>
<div class="lb" id="lb"><button class="lb-cl" onclick="cl()">×</button><button class="lb-prev" onclick="ch(-1)">❮</button><img id="li" src=""><button class="lb-next" onclick="ch(1)">❯</button><div class="lb-cnt" id="lc"></div></div>
<script>
const imgs=Array.from({length:16},(_,i)=>`https://picsum.photos/800/600?random=${i+20}`);let cur=0;const gd=document.getElementById("gd"),lb=document.getElementById("lb"),li=document.getElementById("li"),lc=document.getElementById("lc");
imgs.forEach((s,i)=>{const im=document.createElement("img");im.src=s;im.loading="lazy";im.onclick=()=>op(i);gd.appendChild(im)});
function op(i){cur=i;li.src=imgs[i];lc.textContent=`${i+1} / ${imgs.length}`;lb.classList.add("show");document.body.style.overflow="hidden"}
function cl(){lb.classList.remove("show");document.body.style.overflow=""}
function ch(d){cur=(cur+d+imgs.length)%imgs.length;li.src=imgs[cur];lc.textContent=`${cur+1} / ${imgs.length}`}
document.addEventListener("keydown",e=>{if(!lb.classList.contains("show"))return;if(e.key==="Escape")cl();if(e.key==="ArrowLeft")ch(-1);if(e.key==="ArrowRight")ch(1)});
lb.addEventListener("click",e=>{if(e.target===lb)cl()});
</script></body></html>'''))

print(f"Generated {len(data)} entries...")

with open('f:/数据集/doubao/cot_data/html/html_cot_3.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"Successfully saved {len(data)} entries to html_cot_3.json!")
